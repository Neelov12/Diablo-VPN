import json
import os
import platform
from textwrap import dedent
from pathlib import Path
from importlib.resources import files
from .terminal import Terminal 
import pprint

class Settings: 

    """ Read if wanting to making any changes to config.json """
    developer_warning = dedent(f"""
        POSSIBLE DEFAULT CONFIG CORRUPTION (Refer to Github: 'diablo/defaults/config.json' to restore): 
        If you are modifying the actual settings options that the Diablo program references, make your 
        changes to 'diablo/defaults/config.json', not local. Diablo automatically updates local based on your changes. 
        Don't delete any current options from install in 'diablo/defaults/config.json' unless you've made the appropriate 
        changes in source code. 
        If you are adding a settings option, and the available choices for it are True/False, no changes need to be made 
        in source code (handled automatically). If the available choices are not True/False, you must add them manually
        to 'Settings.none_bool_options' (in settings.py). If the user is allowed to enter text as an option, specify the 
        following in 'Settings.none_bool_options':
        \t'_.TEXT' : If input is string
        \t'_.TEXT_INT' : If input is int
        \t'_.TEXT_FLOAT' : If input is float
        \t'_.TEXT_IP_ADDRESS' : If input is an IP address
        \t'_.TEXT_PORT' : If input is a port
        \t'[ABOVE]:MAX:[maximum]' : To set a non-default max characters allowed for input (default is 24)
        \t'[ABOVE]:MIN:[minimum]' : To set a non-default min characters allowed for input (default is 0) 
        \t                          Can be combined, ie _.TEXT:MIN:3:MAX:5
        It is VERY important to use these naming conventions exactly. If you don't you could open up your modified Diablo
        program to security vulnerabilities. Also, DON'T make a custom setting option that starts with '_.'. The program 
        might do weird things.   
        If you want to give a user the option of several choices or a custom text input, you can add a list to 
        'Settings.none_bool_options' with:
        \t[ \"._DEFAULT:[Your default choice]\", \"._TEXT[Possible Type]\" ]                       
        If you want to give a user the option to enter a list, you can use:
        \t'_.LIST' : If input is string list              
        \t'_.LIST_INT : If input is int list
        \t'_.TEXT_FLOAT : If input is float list
        \t'_.LIST_IP_ADDRESS : If input is a list of IP addresses
        \t'_.LIST_PORT' : If input is a list of ports
        \t'[ABOVE]:MAX:[maximum]' : To set a max number of entries, ie '_.LIST_INT:MAX:50'
        \t'[ABOVE]MIN:[minimum]' : To set a min number of entries, similarly can be combined                        
        """
    )

    none_bool_options = {
        "name": "_.TEXT",
        "log_level": ["debug", "info", "warning", "error"],
        "default_server_ip": ["._DEFAULT:10.8.0.1", "._TEXT_IP_ADDRESS"],
        "max_clients": ["._DEFAULT:Unlimited", "._TEXT_INT"],
        "filtered_ports" : "_.LIST_PORT",
        "blocked_ports": "_.LIST_PORT",   
        "bind_interface": ["tun0"],
    }
    
    """ Windows for future development >:() """
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
    def reset_to_default():
        #Terminal.print_intro()
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

        # Infers yes / no settings based on if it's a bool 
        with open(Settings.DEFAULT_CONFIG_PATH) as f:
            default_config = json.load(f)

    @staticmethod
    def validate_config():
        """ Basic corruption check of config file """
        if not Settings.CONFIG_PATH.exists():
            Settings.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target:
                f_target.write(f_default.read()) 
        
        with open(Settings.DEFAULT_CONFIG_PATH) as f:
            default_config = json.load(f)

        current_config = Settings.load_config()

        option_added = False
        for key in default_config:
            if not key in current_config:
                option_added = True
                Terminal.warn(f"DEVELOPER WARNING: It seems like you've added \'{key}\' as a setting option.")
                """
                Terminal.warn(Settings.developer_warning)
                with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target: 
                    f_target.write(f_default.read())
                """

        if option_added:
            Terminal.warn(dedent(f"""
                DEVELOPER WARNING: You will need to add the logic for this option(s) to your modified Diablo code or 
                                   program will not work. Also, if your setting option is not a bool, you will need
                                   to adjust 'Settings.none_bool_options' accordingly. Reseting to defaults will add
                                   your custom setting option(s) to the program. 
                """))
            Settings.reset_to_default()
        
        for key in current_config:
            if not key in default_config:
                Terminal.warn(Settings.developer_warning)
                with open(Settings.DEFAULT_CONFIG_PATH, "r") as f_default, open(Settings.CONFIG_PATH, "w") as f_target: 
                    f_target.write(f_default.read())

    @staticmethod 
    def _validate_choice(choice, possible_choice):
        if possible_choice.startswith("_.TEXT"):
            text_rule = possible_choice
            if text_rule == "_.TEXT_INT":
                if not isinstance(choice, int):
                    return False
            elif text_rule == "_.TEXT_FLOAT":
                if not isinstance(choice, float):
                    return False    
            else: 
                if not isinstance(choice, str):
                    return False
        elif possible_choice.startswith("_.LIST"):
            text_rule = possible_choice
            if choice:
                if text_rule == "_.LIST_INT":
                    for c in choice:
                        if not isinstance(c, int):
                            return False
                elif text_rule == "_.LIST_FLOAT":
                    for c in choice:
                        if not isinstance(c, float):
                            return False    
                else: 
                    for c in choice:
                        if not isinstance(choice, str):
                            return False

        return True               

    @staticmethod
    def validate_default_choices(default_config):
       for setting, choice in default_config.items(): 
            if not setting in Settings.none_bool_options:
               if not isinstance(choice, bool):
                   print("bool")
                   Terminal.dev_error(Settings.developer_warning, exit=True)
            else: 
                if isinstance(choice, list):
                    continue
                if isinstance(Settings.none_bool_options[setting], list):
                    for possible_choice in Settings.none_bool_options[setting]:
                        if not Settings._validate_choice(choice, possible_choice):
                            print("list check")
                            Terminal.dev_error(Settings.developer_warning, exit=True)
                else:
                    if not Settings._validate_choice(choice, Settings.none_bool_options[setting]):
                        print("choice check")
                        Terminal.dev_error(Settings.developer_warning, exit=True)
    
    @staticmethod
    def reset_to_default():
        #Terminal.print_intro()
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

        # Infers yes / no settings based on if it's a bool 
        with open(Settings.DEFAULT_CONFIG_PATH) as f:
            default_config = json.load(f)

    @staticmethod
    def find_settings_options(current, choices):

        with open(Settings.DEFAULT_CONFIG_PATH) as f:
            default_config = json.load(f)

        Settings.validate_default_choices(default_config)

        for setting, choice in default_config.items():
            if setting in Settings.none_bool_options:
                choices[setting] = Settings.none_bool_options[setting]
            elif isinstance(choice, bool):
                choices[setting] = ["Yes", "No"]

        current_config = Settings.load_config()
        pprint.pprint(current_config)
        for setting, choice in current_config.items():
            if isinstance(choice, bool):
                if choice == True: 
                    current[setting] = "Yes"
                else: 
                    current[setting] = "No"
            else:
                # Catch anything else that isn't explicitly handled
                current[setting] = str(choice)

    @staticmethod
    def settings_menu():
        """ Launches terminal menu for user to change settings """
        from .menus import Menus
        import pprint

        Settings.validate_config()
        
        # Infers yes / no settings based on if it's a bool 
        with open(Settings.DEFAULT_CONFIG_PATH) as f:
            default_config = json.load(f)

        choices = {}
        current = {}
        Settings.find_settings_options(current, choices)
        original = choices.copy()
        #Terminal.launch_menu("Settings", choices, current, formatting)
        Menus.open_settings_menu(current, choices)
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

        


