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

    _ensure_config_exists()  # Ensure config is initialized

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
    def reset_to_default():
        Terminal.print_intro()
        warning_msg = dedent(f"""
        If you reset settings to default, all prior configurations will be erased and
        you will be restored to default settings. Do you wish to proceed?
        """)
        Terminal.warn(warning_msg)
        _, is_yes = Terminal.prompt_response(yesno=True, mercy=False)     

        if not is_yes:
            return 
        
        with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target: 
            f_target.write(f_default.read())

    @staticmethod
    def settings_menu():
        return

