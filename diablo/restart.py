import os
import signal
from .status import is_session_active, clear_status
from .terminal import Terminal

def restart():
    active, status = is_session_active()
    if not active:
        Terminal.quick_message("No prior Diablo session found.")
        return

    Terminal.start_animation([Terminal.get_ansi("[+] Restarting last session", "light blue"),
                              Terminal.get_ansi("[+] Restarting last session", "light blue")])
    
    pid = status.get("pid")
    try:
        os.kill(pid, signal.SIGTERM)
        Terminal.log(f"Killed previous session (PID {pid})")
        clear_status()
    except Exception:
        pass

    mode = status.get("mode")
    if mode == "server":
        from .server import Server
        Server.start_server()
    elif mode == "client":
        from .client import start_client
        start_client()
    else:
        Terminal.error("Unknown session mode.")
