import os
import platform
import socket 
import signal
import time
from textwrap import dedent 

from .tun import setup_tun_interface
from .tls_handler import start_tls_server
from .forwarder import start_forwarding
from .terminal import Terminal 
from .auth import Authentication
from .daemon import daemonize
from .status import Status
from .certgen import generate_self_signed_cert

class Server: 
    mode = "server"
    pid = os.getpid()
    connected_clients = 0
    host = socket.gethostname()
    host_ip = socket.gethostbyname(host)
    password_required = False
    active, status = Status.is_session_active(expected_mode="server")

    @staticmethod 
    def _check_platform():
        Terminal.append_animation("Checking platform")
        if platform.system() != 'Linux':
            Terminal.replace_animation("For now, Diablo proxy server (host mode) only works on Linux.", failure=True)
            exit()
        Terminal.replace_animation("Host has valid platform")
        return
    
    @staticmethod
    def _check_if_root():
        Terminal.append_animation("Checking if host has proper permissions")
        if Status.is_root():
            Terminal.replace_animation(f"Host is running as {Authentication.root_name}")
            return
        else:
            Terminal.error("You must run as root / administrator to host a Diablo server")

    @staticmethod
    def check_status():
        """ Check status of any background Diablo process, exits if one is running """
        Terminal.append_animation("Checking status of server")
        if Server.active:
            Terminal.replace_animation("You already have a server running", failure=True)
            exit()
        else: 
            Terminal.replace_animation("No current running servers. Proceeding.")

            Status.save_status({
                "mode": Server.mode,
                "pid": Server.pid,
                "host_ip": Server.host_ip,
                "connected_clients": Server.connected_clients,
                "password_required": Server.password_required
            })

    @staticmethod
    def start_server():
        Terminal.print_intro()

        starting_msg = Terminal.get_color_bold("Starting Server", "star")
        Terminal.newline(2)
        Terminal.loading_animation(starting_msg, marker_color="star")

        time.sleep(2)
        Terminal.append_animation(line="yo mama")
        Terminal.stop_animation()
        
        Server._check_platform()
        Server._check_if_root()
        Server.check_status()
        generate_self_signed_cert()
        Terminal.pause_animation()
        time.sleep(2)
        Terminal.resume_animation()
        Terminal.stop_animation()
        """
        tun = setup_tun_interface("10.8.0.1", "255.255.255.0")
        conn = start_tls_server(tun)
        start_forwarding(tun, conn)
        Status.save_status()
        """
    
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
            Status.clear_status()
        except ProcessLookupError:
            Terminal.warn("Process already dead. Cleaning up.")
            Status.clear_status()
        except Exception as e:
            Terminal.error(f"Failed to stop process: {e}")

        
