from .tun import setup_tun_interface
#from .tls_handler import start_tls_client
from .forwarder import start_forwarding
from .terminal import Terminal 
from .daemon import daemonize

def start_client():
    Terminal.print_intro()
    Terminal.connecting_animation()

    """
    tun = setup_tun_interface("10.8.0.2", "255.255.255.0")
    conn = start_tls_client(args.server_ip)
    start_forwarding(tun, conn)
    """