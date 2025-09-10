import argparse
import platform
from .tun import setup_tun_interface
from .tls_handler import start_tls_server, start_tls_client
from .forwarder import start_forwarding
import time
import random

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
    connect_parser.add_argument('server_ip', nargs='?', default='127.0.0.1', help='IP address of the Diablo proxy server')
    status_parser = subparsers.add_parser('status', help='Check status of connection or proxy')

    args = parser.parse_args()

    if args.command == 'host':
        Terminal.print_intro()
        Terminal.start_animation([Terminal.get_ansi("[-] Starting Server", "light blue"),
                                  Terminal.get_ansi("[+] Starting Server", "light blue") ])

        time.sleep(2)
        Terminal.stop_animation()

        Terminal.start_animation([Terminal.get_ansi("[-] Sucking dick", "light blue"),
                                  Terminal.get_ansi("[+] Sucking dick", "light blue") ])
        time.sleep(4)
        ran = random.randint(0,3)
        if ran == 1:
            Terminal.stop_animation(final=Terminal.get_ansi("[-] Stopped Server", "red"))
        else:
            Terminal.stop_animation(final=Terminal.get_ansi("[+] Proxy started  ", "green"))
        
        if platform.system() != 'Linux':
            Terminal.error("For now, Diablo proxy server (host mode) only works on Linux.")
            return
        tun = setup_tun_interface("10.8.0.1", "255.255.255.0")
        conn = start_tls_server(tun)
        start_forwarding(tun, conn)
        
        
    elif args.command == 'connect':
        Terminal.print_intro()
        Terminal.connecting_animation()
        """
        tun = setup_tun_interface("10.8.0.2", "255.255.255.0")
        conn = start_tls_client(args.server_ip)
        start_forwarding(tun, conn)
        """
