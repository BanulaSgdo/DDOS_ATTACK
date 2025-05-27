# MRLETUM DDoS Testing Tool

**MRLETUM** is a Python-based network testing script designed for **educational**, **controlled**, and **ethical use only**. It simulates packet flooding to test the resilience and response of systems under high traffic scenarios using **Tor anonymization**, **multi-target bursting**, and **customized threading**.

> 🚨 **Disclaimer:** This tool is strictly for authorized testing environments. Unauthorized use against networks you don't own or have permission to test is illegal and unethical.

---

## ⚙️ Features

- ✅ Multi-target IP and port attack support  
- ✅ Tor integration with dynamic identity renewal  
- ✅ User-agent randomization on every request  
- ✅ Export logs in **JSON** and **CSV**  
- ✅ Multi-threaded design for parallel packet sending  
- ✅ Burst mode with configurable intervals (e.g., every 10s)  
- ✅ Optional SOCKS proxy rotation  
- ✅ Clean ASCII banner branding ("MRLETUM")

---

## 🧠 Requirements

- Python 3.6+
- [stem](https://pypi.org/project/stem/) – for Tor control
- [PySocks](https://pypi.org/project/PySocks/) – for SOCKS5 proxy
- Tor installed and configured to run locally (default port `9050` for SOCKS, `9051` for control)

Install dependencies:

```bash
pip install stem PySocks
````

---

## 🚀 How to Run

```bash
python mrletum_ddos.py
```

### You’ll be prompted to enter:

- Target IP(s) (comma-separated)
- Port(s) (comma-separated, defaults: 80, 443)
- Packet rate (seconds between sends)
- Data size in bytes (default: 600)
- Number of threads (default: 20)
- Use Tor? (`y/n`)
- Enable burst mode? (`y/n`)
- Burst interval (in seconds, default: 10s)
- Export logs format (`json`, `csv`, or `both`)

---

## 📁 Output

- `ddos_attack.log`: Human-readable log file
- `ddos_log.json`: Machine-readable JSON log (if enabled)
- `ddos_log.csv`: CSV-formatted log (if enabled)

---

## ⚠️ Legal Usage

This project is for:

- **Red team simulation**
- **Pentesting labs**
- **Stress testing within your infrastructure**

Do **not** use against:

- External networks
- Public servers
- Any system without **explicit written consent**

---

## ❗ Licensing & Usage

This project is **not licensed for redistribution or reuse without explicit permission from the author**. Do not share, modify, or republish without consent.

---

```

Let me know if you want to add author credits, contact info, or contribution rules.
```
