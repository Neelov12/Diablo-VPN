import os
import json
import platform
import ctypes
from pathlib import Path
from .terminal import Terminal

STATUS_FILE = Path.home() / ".local/share/diablo/status.json"

class Status:

    @staticmethod
    def load_status():
        """Load session status from disk."""
        if not STATUS_FILE.exists():
            return {}
        try:
            with open(STATUS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def save_status(data):
        """Save current session status."""
        os.makedirs(STATUS_FILE.parent, exist_ok=True)
        with open(STATUS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def clear_status():
        """Clear saved status file."""
        if STATUS_FILE.exists():
            STATUS_FILE.unlink()

    @staticmethod
    def is_session_active(expected_mode=None):
        """
        Returns:
            (bool, dict): (True, status) if session is active, otherwise (False, None)
        """
        status = Status.load_status()
        if not status:
            return False, None

        pid = status.get("pid")
        mode = status.get("mode")

        # Check if PID is still alive
        if pid and os.path.exists(f"/proc/{pid}"):
            if expected_mode is None or mode == expected_mode:
                return True, status
        else:
            # Clean up zombie status file
            Status.clear_status()
            
        return False, None
    
    @staticmethod
    def is_root():
        system = platform.system()

        if system == 'Linux' or system == 'Darwin':
            if os.geteuid() != 0:
                return False
        elif system == 'Windows':
            try:
                return ctypes.wind11.shell32.IsUserAnAdmin()
            except:
                return False
        return True

