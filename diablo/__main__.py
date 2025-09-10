import argparse
import platform
from .tun import setup_tun_interface
from .tls_handler import start_tls_server, start_tls_client
from .forwarder import start_forwarding

def main():
    parser = argparse.ArgumentParser(description="Diablo: LAN Privacy Proxy")
    parser.add_argument('--mode', choices=['client', 'server'], required=True)
    parser.add_argument('--server-ip', help='Server IP (client mode)')
    args = parser.parse_args()

    if args.mode == 'server':
        if platform.system() != 'Linux':
            print("Diablo server mode only supports Linux.")
            return
        tun = setup_tun_interface("10.8.0.1", "255.255.255.0")
        conn = start_tls_server(tun)
        start_forwarding(tun, conn)

    elif args.mode == 'client':
        tun = setup_tun_interface("10.8.0.2", "255.255.255.0")
        conn = start_tls_client(args.server_ip)
        start_forwarding(tun, conn)
