import argparse

from .terminal import Terminal 
from .daemon import daemonize

from .settings import Settings
from .server import Server
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
    subparsers.add_parser("stop", help='Stop a running proxy server')
    """ restart """
    subparsers.add_parser("restart", help='Restart last session')
    """ disconnect """
    subparsers.add_parser("disconnect", help='Disconnect from current connection')
    """ settings """
    settings_parser = subparsers.add_parser("settings", help='Change configuration settings\n\'-restore\' to revert to default')
    settings_parser.add_argument('-restore', action='store_true', help='IP address of the Diablo proxy server') 
    """ set-password """
    pass_parser = subparsers.add_parser("set-password", help='Change password of Diablo server, this is the password clients must enter to connect to you') 

    return parser.parse_args()

def main():
    args = arguments()

    if args.command == 'host':
        Server.start_server()
    elif args.command == 'connect':
        start_client()
    elif args.command == 'stop':
        Server.stop_server()
    elif args.command == 'restart':
        from .restart import restart
        restart()
    elif args.command == 'settings':
        from .settings import Settings
        if args.restore:
            Settings.reset_to_default()
        else:
            Settings.settings_menu()
    elif args.command == 'set-password':
        from .auth import Authentication
        Authentication.setup_password()
