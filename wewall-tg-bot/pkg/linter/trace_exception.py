#!/usr/bin/env python3
"""
Линтер для проверки корректной обработки исключений в функциях с OpenTelemetry spans.
Проверяет, что все функции со span'ами правильно обрабатывают исключения.
"""

import ast
import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import difflib
from colorama import init, Fore, Style

init(autoreset=True)


class SpanExceptionChecker(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.issues = []
        self.current_function = None
        self.in_with_span = False
        self.span_var_name = None

    def visit_FunctionDef(self, node):
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_With(self, node):
        for item in node.items:
            if self._is_span_context(item):
                self.in_with_span = True
                self.span_var_name = item.optional_vars.id if item.optional_vars else None

                has_correct_handler = self._check_exception_handling(node.body)

                if not has_correct_handler:
                    self.issues.append({
                        'file': self.filename,
                        'function': self.current_function,
                        'line': node.lineno,
                        'node': node,
                        'span_var': self.span_var_name
                    })

                self.in_with_span = False
                self.span_var_name = None

        self.generic_visit(node)

    def _is_span_context(self, item):
        if isinstance(item.context_expr, ast.Call):
            call = item.context_expr

            if (isinstance(call.func, ast.Attribute) and
                    call.func.attr == 'start_as_current_span'):
                return True

            if (isinstance(call.func, ast.Attribute) and
                    call.func.attr == 'start_span'):
                return True

        return False

    def _check_exception_handling(self, body):
        for node in body:
            if isinstance(node, ast.Try):
                return self._check_except_handlers(node.handlers)
        return False

    def _check_except_handlers(self, handlers):
        for handler in handlers:
            if (handler.type is None or
                    (isinstance(handler.type, ast.Name) and handler.type.id == 'Exception')):

                has_record_exception = False
                has_set_status = False
                has_raise = False

                for stmt in handler.body:
                    if self._is_span_record_exception(stmt):
                        has_record_exception = True
                    elif self._is_span_set_status_error(stmt):
                        has_set_status = True
                    elif isinstance(stmt, ast.Raise):
                        has_raise = True

                return has_record_exception and has_set_status and has_raise

        return False

    def _is_span_record_exception(self, stmt):
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if (isinstance(call.func, ast.Attribute) and
                    call.func.attr == 'record_exception' and
                    isinstance(call.func.value, ast.Name) and
                    call.func.value.id == self.span_var_name):
                return True
        return False

    def _is_span_set_status_error(self, stmt):
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if (isinstance(call.func, ast.Attribute) and
                    call.func.attr == 'set_status' and
                    isinstance(call.func.value, ast.Name) and
                    call.func.value.id == self.span_var_name):
                if call.args and isinstance(call.args[0], ast.Call):
                    status_call = call.args[0]
                    if (isinstance(status_call.func, ast.Name) and
                            status_call.func.id == 'Status' and
                            status_call.args and
                            isinstance(status_call.args[0], ast.Attribute) and
                            status_call.args[0].attr == 'ERROR'):
                        return True
        return False


def generate_fixed_code(source: str, issues: List[dict]) -> str:
    tree = ast.parse(source)

    class CodeFixer(ast.NodeTransformer):
        def __init__(self, issues):
            self.issues = {issue['line']: issue for issue in issues}

        def visit_With(self, node):
            if node.lineno in self.issues:
                issue = self.issues[node.lineno]
                new_body = self._wrap_in_try_except(node.body, issue['span_var'])
                node.body = new_body
            self.generic_visit(node)
            return node

        def _wrap_in_try_except(self, body, span_var):
            except_handler = ast.ExceptHandler(
                type=ast.Name(id='Exception', ctx=ast.Load()),
                name='err',
                body=[
                    # span.record_exception(err)
                    ast.Expr(value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=span_var, ctx=ast.Load()),
                            attr='record_exception',
                            ctx=ast.Load()
                        ),
                        args=[ast.Name(id='err', ctx=ast.Load())],
                        keywords=[]
                    )),
                    ast.Expr(value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=span_var, ctx=ast.Load()),
                            attr='set_status',
                            ctx=ast.Load()
                        ),
                        args=[
                            ast.Call(
                                func=ast.Name(id='Status', ctx=ast.Load()),
                                args=[
                                    ast.Attribute(
                                        value=ast.Name(id='StatusCode', ctx=ast.Load()),
                                        attr='ERROR',
                                        ctx=ast.Load()
                                    ),
                                    ast.Call(
                                        func=ast.Name(id='str', ctx=ast.Load()),
                                        args=[ast.Name(id='err', ctx=ast.Load())],
                                        keywords=[]
                                    )
                                ],
                                keywords=[]
                            )
                        ],
                        keywords=[]
                    )),
                    ast.Raise(exc=ast.Name(id='err', ctx=ast.Load()))
                ]
            )

            try_node = ast.Try(
                body=body,
                handlers=[except_handler],
                orelse=[],
                finalbody=[]
            )

            return [try_node]

    fixer = CodeFixer(issues)
    fixed_tree = fixer.visit(tree)

    return ast.unparse(fixed_tree)


def show_diff(original: str, fixed: str, filename: str):
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        fixed.splitlines(keepends=True),
        fromfile=f"{filename} (original)",
        tofile=f"{filename} (fixed)",
        n=3
    )

    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            print(Fore.GREEN + line, end='')
        elif line.startswith('-') and not line.startswith('---'):
            print(Fore.RED + line, end='')
        elif line.startswith('@'):
            print(Fore.CYAN + line, end='')
        else:
            print(line, end='')


def process_file(filepath: Path, mode: str) -> Tuple[int, int]:
    try:
        source = filepath.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except Exception as e:
        print(f"{Fore.RED}Ошибка при обработке {filepath}: {e}")
        return 0, 0

    checker = SpanExceptionChecker(str(filepath))
    checker.visit(tree)

    if not checker.issues:
        return 0, 0

    if mode == 'show':
        print(f"\n{Fore.YELLOW}Файл: {filepath}")
        for issue in checker.issues:
            print(f"{Fore.RED}  Строка {issue['line']}, функция '{issue['function']}': "
                  f"отсутствует корректная обработка исключений для span")

    elif mode == 'fix':
        fixed_code = generate_fixed_code(source, checker.issues)
        filepath.write_text(fixed_code, encoding='utf-8')
        print(f"{Fore.GREEN}Исправлено: {filepath} ({len(checker.issues)} проблем)")

    elif mode == 'confirm':
        print(f"\n{Fore.YELLOW}Файл: {filepath}")
        fixed_code = generate_fixed_code(source, checker.issues)

        print(f"\n{Fore.CYAN}Предлагаемые изменения:")
        show_diff(source, fixed_code, str(filepath))

        response = input(f"\n{Fore.YELLOW}Применить изменения? [y/N]: ").lower()
        if response == 'y':
            filepath.write_text(fixed_code, encoding='utf-8')
            print(f"{Fore.GREEN}Изменения применены")
        else:
            print(f"{Fore.RED}Изменения отклонены")
            return len(checker.issues), 0

    return len(checker.issues), len(checker.issues) if mode != 'show' else 0


def main():
    parser = argparse.ArgumentParser(
        description='Линтер для проверки обработки исключений в функциях с OpenTelemetry spans'
    )
    parser.add_argument(
        'paths',
        nargs='+',
        help='Пути к файлам или директориям для проверки'
    )
    parser.add_argument(
        '-m', '--mode',
        choices=['show', 'fix', 'confirm'],
        default='show',
        help='Режим работы: show - показать ошибки, fix - автоисправление, confirm - исправление с подтверждением'
    )
    args = parser.parse_args()

    files_to_check = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file() and path.suffix == '.py':
            files_to_check.append(path)
        elif path.is_dir():
            files_to_check.extend(path.rglob('*.py'))


    if not files_to_check:
        print(f"{Fore.RED}Не найдено Python файлов для проверки")
        return 1

    total_issues = 0
    total_fixed = 0

    for filepath in files_to_check:
        issues, fixed = process_file(filepath, args.mode)
        total_issues += issues
        total_fixed += fixed

    print(f"\n{Fore.CYAN}{'=' * 50}")
    print(f"{Fore.CYAN}Итого:")
    print(f"  Проверено файлов: {len(files_to_check)}")
    print(f"  Найдено проблем: {total_issues}")

    if args.mode != 'show':
        print(f"  Исправлено проблем: {total_fixed}")

    return 0 if total_issues == 0 else 1


if __name__ == '__main__':
    sys.exit(main())