#!/usr/bin/env python3
"""
Упрощенная версия WireGuard OpenAI IP Tunneling Script
Для быстрого тестирования и отладки
"""

import os
import sys
import re
import shutil
import subprocess
import socket
import logging
from datetime import datetime


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def check_root():
    """Проверка прав root"""
    if os.geteuid() != 0:
        print("Ошибка: Скрипт должен запускаться с правами root")
        sys.exit(1)


def resolve_domain_ips(domain, logger):
    """Разрешение IP-адресов домена"""
    ips = []
    logger.info(f"Разрешаем домен: {domain}")

    # Метод 1: dig для IPv4
    try:
        result = subprocess.run(
            ["dig", "+short", "A", domain],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and re.match(r'^\d+\.\d+\.\d+\.\d+$', line):
                    ips.append(f"{line}/32")
                    logger.info(f"  Найден IPv4: {line}")
    except Exception as e:
        logger.warning(f"  Ошибка dig IPv4 для {domain}: {e}")

    # Метод 2: socket fallback
    if not ips:
        try:
            ip = socket.gethostbyname(domain)
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                ips.append(f"{ip}/32")
                logger.info(f"  Найден IPv4 (socket): {ip}")
        except Exception as e:
            logger.warning(f"  Ошибка socket для {domain}: {e}")

    return ips


def resolve_all_domains(logger):
    """Разрешение всех доменов OpenAI"""
    domains = [
        "api.openai.com",
        "openai.com",
        "cdn.openai.com",
        "chat.openai.com",
        "platform.openai.com"
    ]

    all_ips = []

    for domain in domains:
        domain_ips = resolve_domain_ips(domain, logger)
        all_ips.extend(domain_ips)

    # Убираем дубликаты
    unique_ips = list(set(all_ips))
    unique_ips.sort()

    logger.info(f"Всего уникальных IP-адресов найдено: {len(unique_ips)}")
    return unique_ips


def backup_config(config_path, logger):
    """Создание резервной копии"""
    if not os.path.exists(config_path):
        logger.error(f"WireGuard конфиг не найден: {config_path}")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{config_path}.backup.{timestamp}"

    try:
        shutil.copy2(config_path, backup_path)
        logger.info(f"Создана резервная копия: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Ошибка создания резервной копии: {e}")
        sys.exit(1)


def update_config(config_path, ips, logger):
    """Обновление конфигурации WireGuard"""
    if not ips:
        logger.error("Не найдено IP-адресов для добавления")
        return False

    logger.info("Обновляем конфигурацию WireGuard...")

    try:
        # Читаем существующий конфиг
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated_lines = []
        in_peer_section = False
        peer_processed = False

        for line in lines:
            stripped = line.strip()

            # Начало секции [Peer]
            if stripped == "[Peer]":
                in_peer_section = True
                peer_processed = False
                updated_lines.append(line)
                continue

            # Новая секция (не [Peer])
            if stripped.startswith('[') and stripped.endswith(']') and stripped != "[Peer]":
                in_peer_section = False

            # AllowedIPs в секции [Peer] - ЗАМЕНЯЕМ содержимое
            if (in_peer_section and
                    re.match(r'^AllowedIPs\s*=', stripped, re.IGNORECASE) and
                    not peer_processed):

                # Полностью заменяем строку AllowedIPs новыми IP
                updated_lines.append(f"AllowedIPs = {', '.join(ips)}\n")
                peer_processed = True
                logger.info(f"Заменили AllowedIPs на: {', '.join(ips)}")
                continue

            updated_lines.append(line)

        # Если AllowedIPs не найден, добавляем в конец секции [Peer]
        if not peer_processed:
            logger.warning("AllowedIPs не найден в секции [Peer]. Добавляем в конец.")

            final_lines = []
            in_peer = False
            added = False

            for line in updated_lines:
                stripped = line.strip()

                if stripped == "[Peer]":
                    in_peer = True
                    final_lines.append(line)
                    continue

                # Новая секция после [Peer]
                if (in_peer and
                        stripped.startswith('[') and
                        stripped.endswith(']') and
                        not added):
                    final_lines.append(f"AllowedIPs = {', '.join(ips)}\n")
                    final_lines.append("\n")
                    added = True
                    in_peer = False

                final_lines.append(line)

            # Добавляем в конец файла если не добавили
            if not added and in_peer:
                final_lines.append(f"AllowedIPs = {', '.join(ips)}\n")

            updated_lines = final_lines

        # Записываем обновленный конфиг
        with open(config_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

        logger.info("Конфигурация WireGuard успешно обновлена")
        return True

    except Exception as e:
        logger.error(f"Ошибка обновления конфигурации: {e}")
        return False


def restart_wireguard(interface, logger):
    """Перезапуск WireGuard"""
    logger.info(f"Перезапускаем WireGuard интерфейс: {interface}")

    try:
        # Проверяем статус
        result = subprocess.run(
            ["wg", "show", interface],
            capture_output=True,
            timeout=5
        )

        # Останавливаем если активен
        if result.returncode == 0:
            logger.info(f"Останавливаем интерфейс {interface}")
            subprocess.run(
                ["wg-quick", "down", interface],
                capture_output=True,
                timeout=30
            )

        # Запускаем
        logger.info(f"Запускаем интерфейс {interface}")
        result = subprocess.run(
            ["wg-quick", "up", interface],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info(f"WireGuard интерфейс {interface} успешно запущен")
            return True
        else:
            logger.error(f"Ошибка запуска: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Ошибка перезапуска WireGuard: {e}")
        return False


def test_connection(logger):
    """Тест подключения к OpenAI"""
    logger.info("Тестируем подключение к OpenAI...")

    test_domains = ["api.openai.com", "openai.com"]

    for domain in test_domains:
        try:
            import urllib.request
            import ssl

            ctx = ssl.create_default_context()
            with urllib.request.urlopen(f"https://{domain}", timeout=30, context=ctx) as response:
                if response.status in [200, 403]:  # 403 ожидается без API ключа
                    logger.info(f"✓ Успешное подключение к {domain}")
                else:
                    logger.warning(f"? Статус {response.status} для {domain}")
        except Exception as e:
            logger.error(f"✗ Ошибка подключения к {domain}: {e}")


def main():
    """Основная функция"""
    logger = setup_logging()

    # Параметры по умолчанию
    config_path = "/etc/wireguard/wg0.conf"
    interface = "wg0"
    test_only = False
    no_restart = False

    # Простой парсинг аргументов
    if "--test-only" in sys.argv:
        test_only = True
    if "--no-restart" in sys.argv:
        no_restart = True
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
Использование: python3 wg-openai-simple.py [ОПЦИИ]

ОПЦИИ:
    --test-only     Только проверить подключение
    --no-restart    Не перезапускать WireGuard
    --help, -h      Показать справку

ПРИМЕРЫ:
    python3 wg-openai-simple.py                # Полное обновление
    python3 wg-openai-simple.py --test-only    # Только тест
    python3 wg-openai-simple.py --no-restart   # Без перезапуска
        """)
        sys.exit(0)

    logger.info("=== Запуск WireGuard OpenAI IP Tunneling Script ===")

    # Только тест подключения
    if test_only:
        test_connection(logger)
        sys.exit(0)

    # Проверка прав
    check_root()

    # Проверка зависимостей
    for cmd in ["wg", "wg-quick", "dig"]:
        if not shutil.which(cmd):
            logger.error(f"Команда {cmd} не найдена. Установите wireguard-tools и dnsutils")
            sys.exit(1)

    # Создаем резервную копию
    backup_path = backup_config(config_path, logger)

    try:
        # Разрешаем домены
        resolved_ips = resolve_all_domains(logger)

        if not resolved_ips:
            logger.error("Не удалось разрешить ни одного домена")
            sys.exit(1)

        # Обновляем конфигурацию
        if update_config(config_path, resolved_ips, logger):
            logger.info("Конфигурация успешно обновлена")

            # Перезапускаем WireGuard
            if not no_restart:
                if restart_wireguard(interface, logger):
                    # Тестируем подключение
                    import time
                    time.sleep(5)
                    test_connection(logger)
                    logger.info("=== Скрипт завершен успешно ===")
                else:
                    # Восстанавливаем из резервной копии
                    logger.error("Восстанавливаем конфигурацию из резервной копии")
                    shutil.copy2(backup_path, config_path)
                    sys.exit(1)
            else:
                logger.info("Пропускаем перезапуск WireGuard")
                logger.info("=== Скрипт завершен успешно ===")
        else:
            logger.error("Ошибка обновления конфигурации")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Скрипт прерван пользователем")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        # Восстанавливаем из резервной копии при ошибке
        try:
            shutil.copy2(backup_path, config_path)
            logger.info("Конфигурация восстановлена из резервной копии")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()