import argparse
import platform
from .tun import setup_tun_interface
from .tls_handler import start_tls_server, start_tls_client
from .forwarder import start_forwarding

import argparse
import platform
from .tun import setup_tun_interface
from .tls_handler import start_tls_server, start_tls_client
from .forwarder import start_forwarding
from .terminal import Terminal 

def main():
    parser = argparse.ArgumentParser(
        description="Diablo: LAN Proxy and Privacy"
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    host_parser = subparsers.add_parser('host', help='Run as proxy server (Linux only)')

    connect_parser = subparsers.add_parser('connect', help='Connect to proxy server')
    connect_parser.add_argument('--server-ip', required=True, help='IP address of the Diablo proxy server')

    args = parser.parse_args()

    if args.command == 'host':
        Terminal.print_intro()
        Terminal.warn("ayo dawg wtf")
        Terminal.log("jahh baby")
        """
        if platform.system() != 'Linux':
            print("[-] Diablo proxy server (host mode) only works on Linux.")
            return
        tun = setup_tun_interface("10.8.0.1", "255.255.255.0")
        conn = start_tls_server(tun)
        start_forwarding(tun, conn)
        """

    elif args.command == 'connect':
        tun = setup_tun_interface("10.8.0.2", "255.255.255.0")
        conn = start_tls_client(args.server_ip)
        start_forwarding(tun, conn)
