import time
import random
import platform

from .tun import setup_tun_interface
from .tls_handler import start_tls_server
from .forwarder import start_forwarding
from .terminal import Terminal 
from .daemon import daemonize

def start_server():
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