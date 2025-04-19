import psutil
import platform
from datetime import datetime
import subprocess

def get_size(bytes, suffix="B"):
    """Scale bytes to its proper format."""
    factor = 1024
    for unit in ["","K","M","G","T","P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def system_info():
    print("="*10, "System Information", "="*10)
    u = platform.uname()
    print(f"System: {u.system}")
    print(f"Node Name: {u.node}")
    print(f"Release: {u.release}")
    print(f"Version: {u.version}")
    print(f"Machine: {u.machine}")
    print(f"Processor: {u.processor}\n")

def boot_time():
    print("="*10, "Boot Time", "="*10)
    bt = datetime.fromtimestamp(psutil.boot_time())
    print(f"Boot Time: {bt.strftime('%Y-%m-%d %H:%M:%S')}\n")

def cpu_info():
    print("="*10, "CPU Info", "="*10)
    print("Physical cores:", psutil.cpu_count(logical=False))
    print("Total cores:", psutil.cpu_count(logical=True))
    freq = psutil.cpu_freq()
    print(f"Max Frequency: {freq.max:.2f}Mhz")
    print(f"Min Frequency: {freq.min:.2f}Mhz")
    print(f"Current Frequency: {freq.current:.2f}Mhz")
    print("CPU Usage per Core:")
    for i, pct in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"  Core {i}: {pct}%")
    print("Total CPU Usage:", psutil.cpu_percent(), "%\n")

def memory_usage():
    print("="*10, "Memory Usage", "="*10)
    mem = psutil.virtual_memory()
    print(f"Total: {get_size(mem.total)}")
    print(f"Available: {get_size(mem.available)}")
    print(f"Used: {get_size(mem.used)}")
    print(f"Percent: {mem.percent}%\n")

def disk_usage():
    print("="*10, "Disk Usage", "="*10)
    for p in psutil.disk_partitions():
        print(f"Device: {p.device}  Mountpoint: {p.mountpoint}  Type: {p.fstype}")
        try:
            usage = psutil.disk_usage(p.mountpoint)
        except PermissionError:
            continue
        print(f"  Total: {get_size(usage.total)}")
        print(f"  Used: {get_size(usage.used)}")
        print(f"  Free: {get_size(usage.free)}")
        print(f"  Percent: {usage.percent}%\n")
    io = psutil.disk_io_counters()
    print(f"Disk I/O — Read: {get_size(io.read_bytes)}  Write: {get_size(io.write_bytes)}\n")

def gpu_usage():
    print("="*10, "GPU Usage", "="*10)
    try:
        out = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=name,utilization.gpu,memory.total,memory.used",
            "--format=csv,noheader,nounits"
        ]).decode().strip().splitlines()
        for line in out:
            name, util, tot, used = [x.strip() for x in line.split(",")]
            print(f"Name: {name}")
            print(f"Utilization: {util}%")
            print(f"Memory Total: {tot} MiB")
            print(f"Memory Used: {used} MiB\n")
    except Exception:
        print("nvidia-smi not found or failed. Skipping GPU info.\n")

def network_info():
    print("="*10, "Network Information", "="*10)
    addrs = psutil.net_if_addrs()
    for iface, addr_list in addrs.items():
        print(f"Interface: {iface}")
        for addr in addr_list:
            fam = addr.family.name if hasattr(addr.family, 'name') else addr.family
            print(f"  {fam}  Addr: {addr.address}  Netmask: {addr.netmask}  Broadcast: {addr.broadcast}")
    io = psutil.net_io_counters()
    print(f"\nTotal Bytes Sent: {get_size(io.bytes_sent)}")
    print(f"Total Bytes Recv: {get_size(io.bytes_recv)}\n")

if __name__ == "__main__":
    system_info()
    boot_time()
    cpu_info()
    memory_usage()
    disk_usage()
    gpu_usage()
    network_info()
