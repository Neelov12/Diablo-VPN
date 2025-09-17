import os
import sys
import time
import getpass
import platform
import ctypes
from textwrap import dedent
from pathlib import Path
from argon2 import PasswordHasher
from .settings import Settings
from .terminal import Terminal 

class Authentication:

    CONFIG_KEY = "password_hash"
    ph = PasswordHasher()
    root_name = "administrator" if platform.system() == "Windows" else "root"

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
    
    @staticmethod
    def is_password_required():
        config = Settings.load_config()
        return config.get("require_password", False)

    @staticmethod
    def is_password_set():
        config = Settings.load_config()
        return bool(config.get(Authentication.CONFIG_KEY, "").strip())

    @staticmethod
    def change_password(warn=False):
        if warn:
            Terminal.warn(dedent("""
                                    If you change your server password, clients will not be able to connect without knowing
                                    your changed password. Do you wish to continue?
                                 """))
            _, is_yes = Terminal.prompt_response(yes_no=True)

            if not is_yes:
                sys.exit(0)
                
            Terminal.newline()

        Terminal.print("Password Setup", color_bold="star")
        try:
            while True:
                passw = getpass.getpass(Terminal.get_bold("Create a new server password: "))
                confirm = getpass.getpass(Terminal.get_bold("Confirm password: "))
                if passw != confirm:
                    Terminal.write("Passwords did not match", color_bold="red")
                    Terminal.flush()
                    time.sleep(1.5)
                    Terminal.move_up(2)
                    Terminal.flush()
                elif len(passw) < 4:
                    Terminal.write("[!] Passwords must be at least 4 characters", color_bold="star")
                    Terminal.flush()
                    time.sleep(1.5)
                    Terminal.move_up(2)
                    Terminal.flush()
                else:
                    Terminal.move_up(3)
                    Terminal.flush()
                    break
        except KeyboardInterrupt:
            sys.exit(1)
        
        hash = Authentication.ph.hash(passw)
        config = Settings.load_config()
        config[Authentication.CONFIG_KEY] = hash
        Settings.save_config(config)
        Terminal.success("Password successfully created")
    
    @staticmethod
    def prompt_password(allowed_attempts=3, exit=True):
        try:
            attempts = 0
            while True:
                if attempts < allowed_attempts:
                    passw = getpass.getpass(Terminal.get_bold("Enter password: "))
                    if Authentication.verify_password(passw):
                        Terminal.move_up(1)
                        Terminal.flush()
                        Terminal.print("[Autheniticated]", color_bold="green")
                        return True
                    else:
                        Terminal.write("Incorrect password", color_bold="red")
                        Terminal.flush()
                        time.sleep(2.5)
                        Terminal.move_up(1)
                        Terminal.flush()
                else:
                    if exit:
                        sys.exit(1)
                    else:
                        Terminal.move_up(1)
                        Terminal.flush()
                        Terminal.print("[Autheniticated Failed]", color_bold="red")
                        return False
                    
                attempts += 1

        except KeyboardInterrupt:
            sys.exit(1)

    @staticmethod
    def verify_password(attempt: str) -> bool:
        try:
            hash = Settings.load_config().get(Authentication.CONFIG_KEY, "")
            Authentication.ph.verify(hash, attempt)
            return True
        except Exception:
            return False
        
    @staticmethod
    def setup_password():
        if Authentication.is_password_set():
            if Authentication.is_root():
                Authentication.change_password(warn=True)
            else:
                Terminal.write("To change your password, confirm your previous password", color_bold="star")
                Terminal.write(f" (or run as {Authentication.root_name})", bold=True)
                Terminal.flush()
                if Authentication.prompt_password():
                    Authentication.change_password(warn=True)
                else:
                    sys.exit()
        else:
            Authentication.change_password()


