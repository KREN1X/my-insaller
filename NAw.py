#!/usr/bin/env python3

######################################
# KRENIX NETWORK AUDIT TOOL - WINDOWS
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

# Set the output file path to the Desktop
output_file = os.path.join(os.path.expanduser("~"), "Desktop", "audit_results.txt")

ping_targets = [
    ('GW MikroTik', '172.16.1.254'),
    ('google.com', 'google.com'),
    ('mail.ru', 'mail.ru')
]

def run_command(cmd):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        # Используем Windows кодировку консоли, чтобы не было кракозябр
        return output.decode('cp866', errors='replace')
    except subprocess.CalledProcessError as e:
        return e.output.decode('cp866', errors='replace')

def draw_banner(stdscr):
    stdscr.addstr(1, 2, "KRENIX NETWORK AUDIT TOOL (Windows)", curses.A_BOLD)

def show_output(stdscr, text):
    lines = text.split('\n')
    max_y, max_x = stdscr.getmaxyx()
    offset = 0

    while True:
        stdscr.clear()
        draw_banner(stdscr)
        for idx, line in enumerate(lines[offset:offset + max_y - 4]):
            stdscr.addstr(idx + 3, 2, line[:max_x - 4])
        stdscr.addstr(max_y - 1, 2, "Press UP/DOWN to scroll, 'q' to go back.")
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
    options.append('Custom address')
    options.append('Back')
    idx = 0

    while True:
        stdscr.clear()
        draw_banner(stdscr)
        stdscr.addstr(3, 2, "Ping Menu:")

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
            if options[idx] == 'Back':
                break
            elif options[idx] == 'Custom address':
                addr = get_input_inline(stdscr, "Enter address:")
            else:
                addr = ping_targets[idx][1]

            res = run_command(f"ping -n 15 {addr}")
            ping_results.append(res)
            show_output(stdscr, res)

def traceroute_screen(stdscr):
    addr = get_input_inline(stdscr, "Enter address for traceroute:")
    res = run_command(f"tracert {addr}")
    traceroute_results.append(res)
    show_output(stdscr, res)

def dns_lookup_screen(stdscr):
    domain = get_input_inline(stdscr, "Enter domain for DNS lookup:")
    res = run_command(f"nslookup {domain}")
    dns_results.append(res)
    show_output(stdscr, res)

def arp_screen(stdscr):
    res = run_command("arp -a")
    arp_results.append(res)
    show_output(stdscr, res)

def iface_info_screen(stdscr):
    res = run_command("ipconfig /all")
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
    host = get_input_inline(stdscr, "Enter host for port scan:")
    common_ports = [21,22,23,25,53,80,110,143,443,465,587,993,995,3306,8080]
    open_ports = simple_port_scan(host, common_ports)
    res = f"Port scan results for {host}:\n"
    if open_ports:
        res += "Open ports:\n" + ", ".join(str(p) for p in open_ports)
    else:
        res += "No open ports found on common ports."
    portscan_results.append(res)
    show_output(stdscr, res)

def local_ports_screen(stdscr):
    res = run_command("netstat -ano")
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
    host = get_input_inline(stdscr, "Enter host for service check:")
    ports_services = {22: "SSH", 80: "HTTP", 443: "HTTPS"}
    res = f"Service check for {host}:\n"
    for port, name in ports_services.items():
        status = "OPEN" if check_service(host, port) else "CLOSED"
        res += f"  {name} (port {port}): {status}\n"
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

    show_output(stdscr, "All stored results have been cleared.")

def save_results(stdscr):
    try:
        desktop_path = os.path.expanduser("~/Desktop")
        os.makedirs(desktop_path, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("===== AUDIT RESULTS =====\n")
            f.write(f"Date and time: {datetime.datetime.now()}\n\n")

            def write_section(title, results):
                if results:
                    f.write(f"====== {title} ======\n")
                    for i, r in enumerate(results, 1):
                        f.write(f"Result {i}:\n{r}\n--------------------------\n")
                    f.write("\n")

            write_section("PING RESULTS", ping_results)
            write_section("TRACEROUTE RESULTS", traceroute_results)
            write_section("DNS LOOKUP RESULTS", dns_results)
            write_section("ARP TABLE RESULTS", arp_results)
            write_section("INTERFACE INFO RESULTS", iface_results)
            write_section("PORT SCAN RESULTS", portscan_results)
            write_section("LOCAL PORTS RESULTS", local_ports_results)
            write_section("SERVICE CHECK RESULTS", service_check_results)
        
        show_output(stdscr, f"Results successfully saved to {output_file}")
    except PermissionError:
        show_output(stdscr, f"Permission denied: Cannot write to {output_file}. Try running with admin rights.")
    except Exception as e:
        show_output(stdscr, f"Error saving results to {output_file}: {str(e)}")

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    options = [
        'Ping',
        'Traceroute',
        'DNS Lookup',
        'ARP Table',
        'Network Interfaces',
        'Port Scan',
        'Local Open Ports',
        'Check Network Services',
        'Clear Results',
        'Save all results',
        'Exit'
    ]
    idx = 0

    while True:
        stdscr.clear()
        draw_banner(stdscr)
        stdscr.addstr(3, 2, "Main Menu:")

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
            if choice == 'Exit':
                break
            elif choice == 'Ping':
                ping_screen(stdscr)
            elif choice == 'Traceroute':
                traceroute_screen(stdscr)
            elif choice == 'DNS Lookup':
                dns_lookup_screen(stdscr)
            elif choice == 'ARP Table':
                arp_screen(stdscr)
            elif choice == 'Network Interfaces':
                iface_info_screen(stdscr)
            elif choice == 'Port Scan':
                port_scan_screen(stdscr)
            elif choice == 'Local Open Ports':
                local_ports_screen(stdscr)
            elif choice == 'Check Network Services':
                service_check_screen(stdscr)
            elif choice == 'Clear Results':
                clear_results_screen(stdscr)
            elif choice == 'Save all results':
                save_results(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)
