import psutil
import platform
from datetime import datetime
import subprocess

def get_size(bytes, suffix="B"):
    """Scale bytes to a human‑readable string."""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def gather():
    report = []

    # --- System Information ---
    report.append("===== System Information =====")
    u = platform.uname()
    report += [
        f"System: {u.system}",
        f"Node Name: {u.node}",
        f"Release: {u.release}",
        f"Version: {u.version}",
        f"Machine: {u.machine}",
        f"Processor: {u.processor}",
        ""
    ]

    # --- Boot Time ---
    report.append("===== Boot Time =====")
    bt = datetime.fromtimestamp(psutil.boot_time())
    report.append(f"Boot Time: {bt.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # --- CPU Info ---
    report.append("===== CPU Info =====")
    report.append(f"Physical cores: {psutil.cpu_count(logical=False)}")
    report.append(f"Total cores:    {psutil.cpu_count(logical=True)}")
    freq = psutil.cpu_freq()
    report += [
        f"Max Frequency: {freq.max:.2f}Mhz",
        f"Min Frequency: {freq.min:.2f}Mhz",
        f"Current Frequency: {freq.current:.2f}Mhz",
        "CPU Usage per Core:"
    ]
    for i, pct in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        report.append(f"  Core {i}: {pct}%")
    report.append(f"Total CPU Usage: {psutil.cpu_percent()}%")
    report.append("")

    # --- Memory Usage ---
    report.append("===== Memory Usage =====")
    m = psutil.virtual_memory()
    report += [
        f"Total:     {get_size(m.total)}",
        f"Available: {get_size(m.available)}",
        f"Used:      {get_size(m.used)}",
        f"Percent:   {m.percent}%",
        ""
    ]

    # --- Disk Usage ---
    report.append("===== Disk Usage =====")
    for part in psutil.disk_partitions():
        report.append(f"[{part.device} mounted on {part.mountpoint} ({part.fstype})]")
        try:
            du = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        report += [
            f"  Total: {get_size(du.total)}",
            f"  Used:  {get_size(du.used)}",
            f"  Free:  {get_size(du.free)}",
            f"  Percent: {du.percent}%",
            ""
        ]
    io = psutil.disk_io_counters()
    report.append(f"Disk I/O — Read: {get_size(io.read_bytes)}, Write: {get_size(io.write_bytes)}")
    report.append("")

    # --- GPU Usage ---
    report.append("===== GPU Usage =====")
    try:
        out = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=name,utilization.gpu,memory.total,memory.used",
            "--format=csv,noheader,nounits"
        ]).decode().splitlines()
        for line in out:
            name, util, tot, used = [x.strip() for x in line.split(",")]
            report += [
                f"Name:        {name}",
                f"Utilization: {util}%",
                f"Memory:      {used}/{tot} MiB",
                ""
            ]
    except Exception:
        report.append("nvidia-smi not available or failed; skipping GPU info.")
        report.append("")

    # --- Network Info (omitted for security) ---
    report.append("===== Network Information =====")
    report.append("**omitted due to security restrictions**")
    report.append("")

    return "\n".join(report)

def main():
    data = gather()
    # print to console
    print(data)
    # write to file
    with open("system_report.txt", "w") as f:
        f.write(data)

if __name__ == "__main__":
    main()
