import ast
import argparse
import sys
from pathlib import Path
from typing import List
import re


class TraceNameIssue:
    def __init__(self, filename: str, line_number: int, column: int,
                 expected_name: str, actual_name: str, class_name: str, method_name: str):
        self.filename = filename
        self.line_number = line_number
        self.column = column
        self.expected_name = expected_name
        self.actual_name = actual_name
        self.class_name = class_name
        self.method_name = method_name

    def __str__(self) -> str:
        return (f"{self.filename}:{self.line_number}:{self.column}: "
                f"Неверное название трейса. Ожидается '{self.expected_name}', "
                f"найдено '{self.actual_name}'")


class TraceNameVisitor(ast.NodeVisitor):
    def __init__(self, filename: str):
        self.filename = filename
        self.issues: List[TraceNameIssue] = []
        self.current_class = None
        self.current_method = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_method = self.current_method
        self.current_method = node.name
        self.generic_visit(node)
        self.current_method = old_method

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        old_method = self.current_method
        self.current_method = node.name
        self.generic_visit(node)
        self.current_method = old_method

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_start_span_call(node):
            self._check_span_name(node)
        self.generic_visit(node)

    def _is_start_span_call(self, node: ast.Call) -> bool:
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == 'start_as_current_span'
        return False

    def _check_span_name(self, node: ast.Call) -> None:
        if not node.args or not isinstance(node.args[0], ast.Constant):
            return

        actual_name = node.args[0].value
        if not isinstance(actual_name, str):
            return

        if not self.current_class or not self.current_method:
            return

        expected_name = f"{self.current_class}.{self.current_method}"

        if actual_name != expected_name:
            issue = TraceNameIssue(
                filename=self.filename,
                line_number=node.lineno,
                column=node.col_offset,
                expected_name=expected_name,
                actual_name=actual_name,
                class_name=self.current_class,
                method_name=self.current_method
            )
            self.issues.append(issue)


class TraceNameLinter:
    def __init__(self):
        self.issues: List[TraceNameIssue] = []

    def lint_file(self, filepath: Path) -> List[TraceNameIssue]:
        try:
            content = filepath.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(filepath))

            visitor = TraceNameVisitor(str(filepath))
            visitor.visit(tree)

            return visitor.issues

        except SyntaxError as e:
            print(f"Ошибка синтаксиса в {filepath}: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Ошибка при обработке {filepath}: {e}", file=sys.stderr)
            return []

    def lint_directory(self, directory: Path) -> List[TraceNameIssue]:
        all_issues = []

        for py_file in directory.rglob("*.py"):
            if py_file.is_file():
                issues = self.lint_file(py_file)
                all_issues.extend(issues)

        return all_issues

    def fix_issue(self, issue: TraceNameIssue, debug: bool = False) -> bool:
        try:
            filepath = Path(issue.filename)
            content = filepath.read_text(encoding='utf-8')
            lines = content.splitlines()

            if issue.line_number > len(lines):
                if debug:
                    print(f"DEBUG: Номер строки {issue.line_number} больше количества строк {len(lines)}")
                return False

            search_range = min(5, len(lines) - issue.line_number + 1)
            found_line_idx = None
            target_line = ""

            for i in range(search_range):
                line_idx = issue.line_number - 1 + i
                if line_idx >= len(lines):
                    break

                line = lines[line_idx]
                if debug:
                    print(f"DEBUG: Проверяем строку {line_idx + 1}: {line.strip()}")

                if issue.actual_name in line:
                    found_line_idx = line_idx
                    target_line = line
                    if debug:
                        print(f"DEBUG: Найдено название трейса в строке {line_idx + 1}")
                    break

            if found_line_idx is None:
                if debug:
                    print(f"DEBUG: Название трейса '{issue.actual_name}' не найдено в ближайших строках")
                return False

            if debug:
                print(f"DEBUG: Обрабатываем строку {found_line_idx + 1}: {target_line}")
                print(f"DEBUG: Ищем: '{issue.actual_name}' -> '{issue.expected_name}'")

            patterns = [
                rf"'{re.escape(issue.actual_name)}'",
                rf'"{re.escape(issue.actual_name)}"',
                rf'(["\'])\s*{re.escape(issue.actual_name)}\s*\1',
            ]

            new_line = target_line
            for i, pattern in enumerate(patterns):
                if debug:
                    print(f"DEBUG: Пробуем паттерн {i + 1}: {pattern}")
                if re.search(pattern, target_line):
                    match = re.search(pattern, target_line)
                    if match:
                        if "'" in match.group():
                            replacement = f"'{issue.expected_name}'"
                        else:
                            replacement = f'"{issue.expected_name}"'

                        if debug:
                            print(f"DEBUG: Найден паттерн, заменяем на: {replacement}")
                        new_line = re.sub(pattern, replacement, target_line)
                        break

            if new_line == target_line:
                if debug:
                    print("DEBUG: Паттерны не сработали, пробуем простую замену")
                new_line = target_line.replace(issue.actual_name, issue.expected_name)

            if new_line != target_line:
                if debug:
                    print(f"DEBUG: Результат замены: {new_line}")
                lines[found_line_idx] = new_line
                new_content = '\n'.join(lines)
                if content.endswith('\n'):
                    new_content += '\n'
                filepath.write_text(new_content, encoding='utf-8')
                return True
            else:
                if debug:
                    print("DEBUG: Замена не произошла")

            return False

        except Exception as e:
            print(f"Ошибка при исправлении {issue.filename}: {e}", file=sys.stderr)
            if debug:
                import traceback
                traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Линтер для проверки соответствия названий трейсов"
    )
    parser.add_argument(
        "path",
        help="Путь к файлу или директории для проверки"
    )
    parser.add_argument(
        "--mode",
        choices=["check", "interactive", "fix"],
        default="check",
        help="Режим работы: check (показать ошибки), interactive (спросить перед фиксом), fix (автофикс)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Показать отладочную информацию"
    )

    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Ошибка: путь {path} не существует", file=sys.stderr)
        sys.exit(1)

    linter = TraceNameLinter()

    if path.is_file():
        issues = linter.lint_file(path)
    else:
        issues = linter.lint_directory(path)

    if not issues:
        print("✅ Проблем с названиями трейсов не найдено")
        sys.exit(0)

    if args.mode == "check":
        if args.quiet:
            print(f"Найдено проблем: {len(issues)}")
        else:
            print(f"Найдено проблем с названиями трейсов: {len(issues)}\n")
            for issue in issues:
                print(issue)
        sys.exit(1)

    elif args.mode == "interactive":
        # Интерактивный режим
        fixed_count = 0
        for issue in issues:
            print(f"\n{issue}")
            response = input("Исправить? (Enter/n/q): ").strip()

            if response.lower() == 'q':
                break
            elif response.lower() == 'n':
                continue
            elif response == '':
                if linter.fix_issue(issue, debug=args.debug):
                    print("✅ Исправлено")
                    fixed_count += 1
                else:
                    print("❌ Не удалось исправить")

        print(f"\nИсправлено: {fixed_count} из {len(issues)} проблем")

    elif args.mode == "fix":
        fixed_count = 0
        for issue in issues:
            if linter.fix_issue(issue, debug=args.debug):
                fixed_count += 1
                if not args.quiet:
                    print(f"✅ Исправлено: {issue.filename}:{issue.line_number}")
            else:
                if not args.quiet:
                    print(f"❌ Не удалось исправить: {issue.filename}:{issue.line_number}")

        if args.quiet:
            print(f"Исправлено: {fixed_count}/{len(issues)}")
        else:
            print(f"\nИсправлено: {fixed_count} из {len(issues)} проблем")


if __name__ == "__main__":
    main()