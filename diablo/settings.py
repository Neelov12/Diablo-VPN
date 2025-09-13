import json
import os
import platform
from textwrap import dedent
from pathlib import Path
from importlib.resources import files
from .terminal import Terminal 

class Settings: 
    # Windows for future development
    if platform.system() == "Windows":
        CONFIG_DIR = Path(os.getenv("APPDATA", "~/.config")).expanduser() / "diablo"
    else:
        CONFIG_DIR = Path.home() / ".config" / "diablo"

    CONFIG_PATH = CONFIG_DIR / "config.json"
    DEFAULT_CONFIG_PATH = files("diablo.defaults").joinpath("config.json")

    @staticmethod
    def _ensure_config_exists():
        if not Settings.CONFIG_PATH.exists():
            Settings.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target:
                f_target.write(f_default.read()) 

    @staticmethod
    def load_config():
        with open(Settings.CONFIG_PATH, "r") as f:
            return json.load(f)
        
    @staticmethod
    def save_config(config: dict):
        with open(Settings.CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)

    @staticmethod
    def update_config(new_values: dict):
        config = Settings.load_config()
        config.update(new_values)
        Settings.save_config(config)

    @staticmethod
    def check_config():
        """ Basic corruption check of config file """
        if not Settings.CONFIG_PATH.exists():
            Settings.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target:
                f_target.write(f_default.read())
            return True 
        
        with open(Settings.DEFAULT_CONFIG_PATH) as f:
            default_config = json.load(f)

        current_config = Settings.load_config()

        for key in current_config:
            if not key in default_config:
                warning_msg = dedent("""
                Corrupted configuration file found in user's workspace. Restoring user's settings to 
                default. If you are a developer experimenting with Diablo's configurations, change 
                'diablo/default/config.json' instead of config.json in user bin. The program updates
                the workspace config periodically based on the default configs, such as here. More 
                optimally, just run 'diablo settings -restore' after changing default config.json.                   
                """)
                Terminal.warn(warning_msg)
                with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target: 
                    f_target.write(f_default.read())
        
    
    @staticmethod
    def reset_to_default():
        Terminal.print_intro()
        warning_msg = dedent(f"""
        If you reset settings to default, all prior configurations will be erased and
        you will be restored to default settings. Do you wish to proceed?
        """)
        Terminal.warn(warning_msg)
        _, is_yes = Terminal.prompt_response(yes_no=True, mercy=False)     

        if not is_yes:
            return 
        
        with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target: 
            f_target.write(f_default.read())

        Terminal.newline()
        Terminal.success("Restored settings to default")

    @staticmethod
    def settings_menu():
        """ Launches terminal menu for user to change settings """

        Settings.check_config()
        """ Set setting options, non-specified default to yes/no """
        # None yes / no setting
        manual_options = {
            "log_level": ["debug", "info", "warning", "error"],
            "default_server_ip": ["10.8.0.1"],
            "max_clients": ["unlimited", "10", "15", "25", "100", "500"],
            "blocked_ports": [53, 67, 68],   
            "bind_interface": ["tun0"],
        }
        """ Set selection types, non-specified default to 'dropdown' """

        formatting = {
            "TYPES" : {
                "max_clients" : "text-ip",
                "default_server_ip" : "text-ip",
                "filtered_ports" : "list-int",
                "blocked_ports" : "list-int",
            },
            "WARNINGS" : {
                "required_password" : {
                    "no" : "Disabling this option leaves you unprotected to unknown connections."
                },
                "spoof_arp" : {
                    "yes" : "Only use this option on a network you own or are authorized to audit."
                },
                "spoof_arp" : {
                    "yes" : "Only use this option on a network you own or are authorized to audit."
                },
                "lockdown_mode" : {
                    "yes" : "Enabling lockdown mode will prevent any new connections."
                },
                "aggressive_auditing" : {
                    "yes" : "Only use this option on a network you own or are authorized to audit."
                },   
            },
            "RULES" : {
                "filtered_ports" : {
                    "min" : 0,
                    "max" : 65535
                },
                "blocked_ports" : {
                    "min" : 0,
                    "max" : 65535
                },
                "default_server_ip" : "ip_address",
            },
            "PARENTS" : {
                "monitor_arp_requests": {
                    "no" : ["block_arp_requests", "manipulate_arp_response"],
                },
                "block_arp_requests": {
                    "yes" : "monitor_arp_requests"
                },
                "manipulate_arp_response" : {
                    "yes" : "monitor_arp_requests"
                },
                "persistant_auditing" : {
                    "no" : ["spoof_arp", "lockdown_mode", "aggressive_auditing"],
                },
                "spoof_arp" : {
                    "yes": "persistant_auditing"
                },
                "lockdown_mode" : {
                    "yes": "persistant_auditing"
                },
                "aggressive_auditing" : {
                    "yes": "persistant_auditing"
                },
            },
        }
        
        # Infers yes / no settings based on if it's a bool 
        with open(Settings.DEFAULT_CONFIG_PATH) as f:
            default_config = json.load(f)

        options_map = {}
        for key, val in default_config.items():
            if key in manual_options:
                options_map[key] = manual_options[key]
            elif isinstance(val, bool):
                options_map[key] = ["yes", "no"]
            else:
                # Catch anything else that isn't explicitly handled
                options_map[key] = [str(val)]

        current_config = Settings.load_config()
        current = {}
        for key, val in current_config.items():
            if isinstance(val, bool):
                if val == True: 
                    current[key] = "yes"
                else: 
                    current[key] = "no"
            else:
                # Catch anything else that isn't explicitly handled
                current[key] = str(val)
        
        new_config_unconverted = Terminal.launch_menu("Settings", options_map, current, formatting)

        """
        # Convert readable config dictionary to an actual json 
        new_config = {}
        for key, val in new_config_unconverted.items():
            key = str(key)
            if isinstance(val, str):
                if val.lower() == "yes":
                    new_config[key] = True
                elif val.lower() == "no":
                    new_config[key] = False
                else:
                    new_config[key] = val      

        if current_config != new_config:
            Settings.save_config(new_config)
        """

        


