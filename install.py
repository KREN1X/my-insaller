#!/usr/bin/env python3
import subprocess
import os
import sys
import shutil
import urllib.request

def run_command(command, use_sudo=False):
    if use_sudo:
        command = f"sudo {command}"
    print(f"→ Выполняем: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Ошибка при выполнении: {command}")
        sys.exit(1)

def download_file(url, save_path):
    print(f"Скачиваем {url} в {save_path}...")
    urllib.request.urlretrieve(url, save_path)
    print("Скачано.")

def main():
    print("Запрашиваем права администратора...")
    try:
        subprocess.run("sudo -v", shell=True, check=True)
    except subprocess.CalledProcessError:
        print("Не удалось получить права sudo. Выход.")
        sys.exit(1)

    script_dir = os.path.dirname(os.path.realpath(__file__))
    print(f"Скрипт запущен из: {script_dir}")

    if shutil.which("brew") is None:
        print("Homebrew не найден. Устанавливаем...")
        run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    else:
        print("Homebrew уже установлен.")

    print("Фиксируем права Homebrew...")
    run_command("chown -R $(whoami) /usr/local/var/homebrew", use_sudo=True)

    print("Обновляем Homebrew...")
    run_command("brew update")

    print("Устанавливаем Python...")
    run_command("brew install python")

    print("Устанавливаем speedtest-cli...")
    run_command("brew install speedtest-cli")

    print("Устанавливаем nmap...")
    run_command("brew install nmap")

    print("Устанавливаем jq...")
    run_command("brew install jq")

    # Скачиваем tui.py
    tui_url = "https://raw.githubusercontent.com/KREN1X/my-insaller/refs/heads/main/tui.py"
    tui_path = os.path.join(script_dir, "tui.py")
    download_file(tui_url, tui_path)

    # Запускаем tui.py
    if os.path.isfile(tui_path):
        print("Запускаем tui.py...")
        run_command(f"python3 \"{tui_path}\"")
    else:
        print("Файл tui.py не найден. Завершение установки.")

    print("Установка завершена.")

if __name__ == "__main__":
    main()
