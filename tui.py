#!/usr/bin/env python3

######################################
# KRENIX NETWORK AUDIT TOOL - EXTENDED
# Поддержка macOS (ifconfig вместо ip)
######################################

import curses
import subprocess
import json
import datetime
import socket
import os

ping_results = []
speedtest_results = []
mtr_results = []
traceroute_results = []
dns_results = []
arp_results = []
iface_results = []
portscan_results = []
local_ports_results = []
service_check_results = []

# Устанавливаем путь для файла в домашней директории пользователя
output_file = os.path.join(os.path.expanduser("~"), "audit_results.txt")

ping_targets = [
    ('GW MikroTik', '172.16.1.254'),
    ('google.com', 'google.com'),
    ('mail.ru', 'mail.ru')
]

def run_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return output.decode()
    except subprocess.CalledProcessError as e:
        return e.output.decode()

def draw_banner(stdscr):
    stdscr.addstr(1, 2, "KRENIX NETWORK AUDIT TOOL", curses.A_BOLD)

def show_output(stdscr, text):
    lines = text.split('\n')
    max_y, max_x = stdscr.getmaxyx()
    offset = 0

    while True:
        stdscr.clear()
        draw_banner(stdscr)
        for idx, line in enumerate(lines[offset:offset + max_y - 4]):
            stdscr.addstr(idx + 3, 2, line[:max_x - 4])
        stdscr.addstr(max_y - 1, 2, "Нажмите ВВЕРХ/ВНИЗ для прокрутки, 'q' для возврата.")
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_DOWN and offset < len(lines) - (max_y - 4):
            offset += 1
        elif key == curses.KEY_UP and offset > 0:
            offset -= 1
        elif key in [ord('q'), 27]:
            break

def get_input_inline(stdscr, prompt):
    curses.echo()
    stdscr.addstr(curses.LINES - 2, 2, prompt)
    stdscr.clrtoeol()
    stdscr.refresh()
    input_bytes = stdscr.getstr(curses.LINES - 2, len(prompt) + 3)
    curses.noecho()
    try:
        return input_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return input_bytes.decode('utf-8', errors='replace')

def ping_screen(stdscr):
    options = [f"Ping {name} ({addr})" for name, addr in ping_targets]
    options.append('Пользовательский адрес')
    options.append('Назад')
    idx = 0

    while True:
        stdscr.clear()
        draw_banner(stdscr)
        stdscr.addstr(3, 2, "Меню Ping:")

        max_x = stdscr.getmaxyx()[1]
        for i, opt in enumerate(options):
            menu_line = opt.ljust(max_x - 8)
            if i == idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(5 + i, 4, menu_line)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(5 + i, 4, menu_line)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(options) - 1:
            idx += 1
        elif key in [10, 13]:
            if options[idx] == 'Назад':
                break
            elif options[idx] == 'Пользовательский адрес':
                addr = get_input_inline(stdscr, "Введите адрес:")
            else:
                addr = ping_targets[idx][1]

            res = run_command(f"ping -c 5 {addr}")
            ping_results.append(res)
            show_output(stdscr, res)

def mtr_screen(stdscr):
    addr = get_input_inline(stdscr, "Введите адрес для MTR:")
    res = run_command(f"sudo mtr -r -c 10 {addr}")
    mtr_results.append(res)
    show_output(stdscr, res)

def speedtest_simple(stdscr):
    stdscr.clear()
    draw_banner(stdscr)
    stdscr.addstr(3, 2, "Запуск Speedtest... Пожалуйста, подождите.")
    stdscr.refresh()

    cmd = "speedtest --accept-license --accept-gdpr --format=json"
    raw_output = run_command(cmd)

    try:
        data = json.loads(raw_output)
    except Exception as e:
        show_output(stdscr, f"Ошибка парсинга JSON:\n{e}\n\nИсходный вывод:\n{raw_output}")
        return

    server = data.get("server", {})
    isp = data.get("isp", "N/A")
    ping_latency = data.get("ping", {}).get("latency", 0)
    download_bandwidth = data.get("download", {}).get("bandwidth", 0)
    upload_bandwidth = data.get("upload", {}).get("bandwidth", 0)
    packet_loss = data.get("packetLoss", 0) or 0
    result_url = data.get("result", {}).get("url", "N/A")

    download_mbps = download_bandwidth * 8 / 1_000_000
    upload_mbps = upload_bandwidth * 8 / 1_000_000

    output = (
        "Speedtest by Ookla\n"
        f"Сервер: {server.get('name', 'N/A')} - {server.get('location', 'N/A')} (ID: {server.get('id', 'N/A')})\n"
        f"ISP: {isp}\n"
        f"Пинг: {ping_latency:.2f} мс\n"
        f"Скачивание: {download_mbps:.2f} Мбит/с\n"
        f"Загрузка: {upload_mbps:.2f} Мбит/с\n"
        f"Потеря пакетов: {packet_loss}%\n"
        f"URL результата: {result_url}\n"
    )

    speedtest_results.append(output)
    show_output(stdscr, output)

def traceroute_screen(stdscr):
    addr = get_input_inline(stdscr, "Введите адрес для traceroute:")
    res = run_command(f"traceroute {addr}")
    traceroute_results.append(res)
    show_output(stdscr, res)

def dns_lookup_screen(stdscr):
    domain = get_input_inline(stdscr, "Введите домен для DNS-запроса:")
    res = run_command(f"dig {domain} +noall +answer")
    if not res.strip():
        res = run_command(f"nslookup {domain}")
    dns_results.append(res)
    show_output(stdscr, res)

def arp_screen(stdscr):
    res = run_command("arp -a")
    arp_results.append(res)
    show_output(stdscr, res)

def iface_info_screen(stdscr):
    res = run_command("ifconfig")
    iface_results.append(res)
    show_output(stdscr, res)

def simple_port_scan(host, ports):
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception:
            sock.close()
    return open_ports

def port_scan_screen(stdscr):
    host = get_input_inline(stdscr, "Введите хост для сканирования портов:")
    common_ports = [21,22,23,25,53,80,110,143,443,465,587,993,995,3306,8080]
    open_ports = simple_port_scan(host, common_ports)
    res = f"Результаты сканирования портов для {host}:\n"
    if open_ports:
        res += "Открытые порты:\n" + ", ".join(str(p) for p in open_ports)
    else:
        res += "Открытые порты не найдены среди стандартных портов."
    portscan_results.append(res)
    show_output(stdscr, res)

def local_ports_screen(stdscr):
    res = run_command("netstat -tuln") or run_command("ss -tuln")
    local_ports_results.append(res)
    show_output(stdscr, res)

def check_service(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False

def service_check_screen(stdscr):
    host = get_input_inline(stdscr, "Введите хост для проверки сервисов:")
    ports_services = {22: "SSH", 80: "HTTP", 443: "HTTPS"}
    res = f"Проверка сервисов для {host}:\n"
    for port, name in ports_services.items():
        status = "ОТКРЫТ" if check_service(host, port) else "ЗАКРЫТ"
        res += f"  {name} (порт {port}): {status}\n"
    service_check_results.append(res)
    show_output(stdscr, res)

def clear_results_screen(stdscr):
    ping_results.clear()
    speedtest_results.clear()
    mtr_results.clear()
    traceroute_results.clear()
    dns_results.clear()
    arp_results.clear()
    iface_results.clear()
    portscan_results.clear()
    local_ports_results.clear()
    service_check_results.clear()

    show_output(stdscr, "Все сохраненные результаты очищены.")

def save_results(stdscr):
    try:
        # Убедимся, что директория существует
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("===== РЕЗУЛЬТАТЫ АУДИТА =====\n")
            f.write(f"Дата и время: {datetime.datetime.now()}\n\n")

            def write_section(title, results):
                f.write(f"====== {title} ======\n")
                for r in results:
                    f.write(r + "\n--------------------------\n")
                f.write("\n")

            write_section("РЕЗУЛЬТАТЫ PING", ping_results)
            write_section("РЕЗУЛЬТАТЫ SPEEDTEST", speedtest_results)
            write_section("РЕЗУЛЬТАТЫ MTR", mtr_results)
            write_section("РЕЗУЛЬТАТЫ TRACEROUTE", traceroute_results)
            write_section("РЕЗУЛЬТАТЫ DNS-ЗАПРОСОВ", dns_results)
            write_section("РЕЗУЛЬТАТЫ ARP ТАБЛИЦЫ", arp_results)
            write_section("ИНФОРМАЦИЯ О СЕТЕВЫХ ИНТЕРФЕЙСАХ", iface_results)
            write_section("РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ ПОРТОВ", portscan_results)
            write_section("РЕЗУЛЬТАТЫ ЛОКАЛЬНЫХ ПОРТОВ", local_ports_results)
            write_section("РЕЗУЛЬТАТЫ ПРОВЕРКИ СЕРВИСОВ", service_check_results)
        
        show_output(stdscr, f"Результаты успешно сохранены в {output_file}")
    except Exception as e:
        show_output(stdscr, f"Ошибка при сохранении результатов в {output_file}: {str(e)}")

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    options = [
        'Ping',
        'Speedtest',
        'MTR',
        'Traceroute',
        'DNS-запрос',
        'ARP-таблица',
        'Сетевые интерфейсы',
        'Сканирование портов',
        'Локальные открытые порты',
        'Проверка сетевых сервисов',
        'Очистить результаты',
        'Сохранить все результаты',
        'Выход'
    ]
    idx = 0

    while True:
        stdscr.clear()
        draw_banner(stdscr)
        stdscr.addstr(3, 2, "Главное меню:")

        max_x = stdscr.getmaxyx()[1]
        for i, opt in enumerate(options):
            menu_line = opt.ljust(max_x - 8)
            if i == idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(5 + i, 4, menu_line)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(5 + i, 4, menu_line)

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and idx > 0:
            idx -= 1
        elif key == curses.KEY_DOWN and idx < len(options) - 1:
            idx += 1
        elif key in [10, 13]:
            choice = options[idx]
            if choice == 'Выход':
                break
            elif choice == 'Ping':
                ping_screen(stdscr)
            elif choice == 'Speedtest':
                speedtest_simple(stdscr)
            elif choice == 'MTR':
                mtr_screen(stdscr)
            elif choice == 'Traceroute':
                traceroute_screen(stdscr)
            elif choice == 'DNS-запрос':
                dns_lookup_screen(stdscr)
            elif choice == 'ARP-таблица':
                arp_screen(stdscr)
            elif choice == 'Сетевые интерфейсы':
                iface_info_screen(stdscr)
            elif choice == 'Сканирование портов':
                port_scan_screen(stdscr)
            elif choice == 'Локальные открытые порты':
                local_ports_screen(stdscr)
            elif choice == 'Проверка сетевых сервисов':
                service_check_screen(stdscr)
            elif choice == 'Очистить результаты':
                clear_results_screen(stdscr)
            elif choice == 'Сохранить все результаты':
                save_results(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
