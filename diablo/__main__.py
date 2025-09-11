import argparse

from .terminal import Terminal 
from .daemon import daemonize

from .server import start_server
from .client import start_client

def arguments():
    """ Create commands (as subparsers) and arguments """
    parser = argparse.ArgumentParser(
        description="Diablo: LAN Proxy and Privacy"
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    """ host """
    host_parser = subparsers.add_parser('host', help='Run as proxy server (Linux only)')
    host_parser.add_argument('-hang', action='store_true', help='Keep terminal open')
    """ connect """
    connect_parser = subparsers.add_parser('connect', help='Connect to proxy server')
    connect_parser.add_argument('server_ip', nargs='?', default='127.0.0.1', help='IP address of the Diablo proxy server')
    connect_parser.add_argument('-hang', action='store_true', help='Keep terminal open')
    """ status """
    status_parser = subparsers.add_parser('status', help='Check status of connection or proxy')
    """ stop """
    subparsers.add_parser("stop", help="Stop a running proxy server")
    """ restart """
    subparsers.add_parser("restart", help="Restart last session")
    """ disconnect """
    subparsers.add_parser("disconnect", help="Disconnect from current connection")

    return parser.parse_args()

def main():
    args = arguments()

    if args.command == 'host':
        start_server()
        
    elif args.command == 'connect':
        start_client()
