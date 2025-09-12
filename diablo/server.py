import os
import platform
import socket 
import signal
from textwrap import dedent 

from .tun import setup_tun_interface
from .tls_handler import start_tls_server
from .forwarder import start_forwarding
from .terminal import Terminal 
from .daemon import daemonize
from .status import is_session_active, save_status, clear_status

class Server: 
    mode = "server"
    pid = os.getpid()
    connected_clients = 0
    host = socket.gethostname()
    host_ip = socket.gethostbyname(host)
    password_required = False
    active, status = is_session_active(expected_mode="server")

    @staticmethod 
    def _check_platform():
        if platform.system() != 'Linux':
            Terminal.error("For now, Diablo proxy server (host mode) only works on Linux.")
            exit()
        return

    @staticmethod
    def check_status():
        """ Check status of any background Diablo process, exits if one is running """
        Terminal.start_animation([Terminal.get_ansi("[-] Checking Status", "light blue"),
                                Terminal.get_ansi("[+] Checking Status", "light blue") ])
        if Server.active:
            Terminal.stop_animation(final=Terminal.get_ansi("[-] You already have a server running", "red"))
            exit()
        else: 
            Terminal.stop_animation(final=Terminal.get_ansi("[-] No current running servers. Proceeding.", "green"))

            save_status({
                "mode": Server.mode,
                "pid": Server.pid,
                "host_ip": Server.host_ip,
                "connected_clients": Server.connected_clients,
                "password_required": Server.password_required
            })

    @staticmethod
    def start_server():
        Terminal.print_intro()

        Server._check_platform()
        Server.check_status()
            
        tun = setup_tun_interface("10.8.0.1", "255.255.255.0")
        conn = start_tls_server(tun)
        start_forwarding(tun, conn)
    
    @staticmethod
    def stop_server(): 
        """ Aqcuires running server info from server json, if it exists, otherwise exits """
        if not Server.active: 
            Terminal.quick_message("No active Diablo proxy server to stop")
            return  
        
        pid = Server.status.get("pid")
        mode = Server.status.get("mode")

        Terminal.print_intro()
        warning_msg = dedent(f"""
        If you stop the running Diablo server on pid {pid}, all current connections to it
        will abruptly close, and all client traffic will be interrupted. To check the 
        status of the server, including all current connections, run 'diablo status'
        """)
        Terminal.warn(warning_msg)
        _, is_yes = Terminal.prompt_response(yesnoenter=True)     
        if not is_yes:
            return 

        try:
            os.kill(pid, signal.SIGTERM)
            Terminal.success(f"{mode.capitalize()} (PID {pid}) stopped successfully.")
            clear_status()
        except ProcessLookupError:
            Terminal.warn("Process already dead. Cleaning up.")
            clear_status()
        except Exception as e:
            Terminal.error(f"Failed to stop process: {e}")

        
