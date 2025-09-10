import os
import platform
import subprocess
import fcntl
import struct
import sys

def setup_tun_interface(ip_addr, netmask, name=None):
    system = platform.system()

    if system == 'Linux':
        return setup_tun_linux(ip_addr, netmask, name or "tun0")
    elif system == 'Darwin':
        return setup_tun_macos(ip_addr, netmask)
    elif system == 'Windows':
        raise NotImplementedError("Windows TUN/TAP not yet implemented")
    else:
        raise Exception(f"Unsupported OS: {system}")

def setup_tun_linux(ip_addr, netmask, tun_name):
    TUNSETIFF = 0x400454ca
    IFF_TUN = 0x0001
    IFF_NO_PI = 0x1000

    tun_fd = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", tun_name.encode(), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun_fd, TUNSETIFF, ifr)

    # Assign IP and bring interface up
    subprocess.run(["ip", "addr", "add", f"{ip_addr}/24", "dev", tun_name], check=True)
    subprocess.run(["ip", "link", "set", tun_name, "up"], check=True)

    print(f"[+] Linux TUN device {tun_name} set up at {ip_addr}")
    return tun_fd

def setup_tun_macos(ip_addr, netmask):
    # macOS TUNs are /dev/utun[0-255]
    # Let OS pick next available
    for i in range(10):
        try:
            fd = os.open(f"/dev/utun{i}", os.O_RDWR)
            name = f"utun{i}"
            break
        except FileNotFoundError:
            continue
    else:
        raise RuntimeError("No available utun device")

    # ifconfig to set it up
    subprocess.run([
        "ifconfig", name, ip_addr, ip_addr, "netmask", netmask, "up"
    ], check=True)

    print(f"[+] macOS TUN device {name} set up at {ip_addr}")
    return fd

# TODO: Use Wintun.dll, or OpenVPN TAP, or Npcap


