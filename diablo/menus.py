import sys 
from datetime import datetime
import time
import threading
import termios
import tty
import select
import shutil 
from textwrap import dedent
import pprint
import re
from importlib.resources import files
from collections import deque
from .terminal import Terminal 

class Menus: 

    _cache = {}
    _actions = deque(maxlen=25)

    @staticmethod
    def _clear_cache():
        Menus._cache.clear()
    @staticmethod
    def _add_cache(name, var):
        Menus._cache[f".TMP.{name}"] = var

    @staticmethod
    def _get_cache(name, var):
        return Menus._cache[f".TMP.{name}"]
    
    @staticmethod
    def _setup_menu_environment(options, option_names=None, current=None, choices=None):
        if not option_names:
            if not current and not choices:
                Terminal.dev_error("Improper use of menu, if calling with current and choices, don't call option_names")
            
            for option_name, choices in choices.items():
                options[option_name] = {"current" : current[option_name]}
                type = "dropdown"
                if isinstance(choices, list):
                    type = "dropdown"
                    updated_choices = []
                    for possible_choice in choices:
                        if possible_choice.startswith("_.TEXT"):
                            text_rule = possible_choice
                            if text_rule == "_.TEXT_INT":
                                type = "text-int"
                            elif text_rule == "_.TEXT_FLOAT":
                                type = "text-int" 
                            if text_rule == "_.TEXT_PORT":
                                type = "text-port"
                            elif text_rule == "_.TEXT_IP_ADDRESS":
                                type = "text-ip-address" 
                            else:
                                type = "text"
                                if ':' in text_rule:
                                    rules = {}
                                    params = text_rule.split(':')
                                    for i, p in enumerate(params):
                                        if p == "MAX":
                                            rules["MAX"] = params[i+1]
                                        elif p == "MIN":
                                            rules["MIN"] = params[i+1]
                                    options[option_name] = {"rules" : rules}

                        else:
                            updated_choices.append(possible_choice)
                    options[option_name] = {"choices" : updated_choices}
                    options[option_name] = {"type" : type}

                elif isinstance(choices, str):
                    if possible_choice.startswith("_.TEXT"):
                        text_rule = possible_choice
                        if text_rule == "_.TEXT_INT":
                            type = "text-int"
                        elif text_rule == "_.TEXT_FLOAT":
                            type = "text-int" 
                        if text_rule == "_.TEXT_PORT":
                            type = "text-port"
                        elif text_rule == "_.TEXT_IP_ADDRESS":
                            type = "text-ip-address" 
                        else:
                            type = "text"
                            if ':' in text_rule:
                                rules = {}
                                params = text_rule.split(':')
                                for i, p in enumerate(params):
                                    if p == "MAX":
                                        rules["MAX"] = params[i+1]
                                    elif p == "MIN":
                                        rules["MIN"] = params[i+1]
                                options[option_name] = {"rules" : rules}
                        options[option_name] = {"type" : type}

                    elif possible_choice.startswith("_.LIST"):
                        list_rule = possible_choice
                        if list_rule == "_.LIST_INT":
                            type = "list-int"
                        elif list_rule == "_.LIST_FLOAT":
                            type = "list-int" 
                        if list_rule == "_.LIST_PORT":
                            type = "list-port"
                        elif list_rule == "_.LIST_IP_ADDRESS":
                            type = "list-ip-address" 
                        else:
                            type = "text"
                            if ':' in list_rule:
                                rules = {}
                                params = text_rule.split(':')
                                for i, p in enumerate(params):
                                    if p == "MAX":
                                        rules["MAX"] = params[i+1]
                                    elif p == "MIN":
                                        rules["MIN"] = params[i+1]
                                options[option_name] = {"rules" : rules}  
                        options[option_name] = {"type" : type}
                    else:
                        Terminal.dev_error(f"Improper naming of choice rule '{possible_choice}'.")       
        else:
            for option_name in option_names:
                options[option_name] = {"rules" : rules}
    
    @staticmethod
    def _make_menu_header(title):
        logo = Terminal.get_logo()
        menu_title = f"\n{Terminal.get_color_bold("Diablo", "diablo red")} {Terminal.get_color_bold(title, "star")}\n{Terminal.important_line}"
        header = f"{logo}{menu_title}"
        Menus._add_cache("_.HEADER", header)

    def _make_menu_footer(msg, len):
        Menus._add_cache("_.HEADER", header)

    def create_instruction(msg=None, color_bold_msg=None, color_msg=None, bold_msg=None, color="star"):
        instr = ""
        instr_len = 0
        if color_bold_msg:
            instr_len += len(color_bold_msg)
            instr+= Terminal.get_color_bold(color_msg, color)
        if color_msg:
            instr_len += len(color_msg)
            instr+= Terminal.get_color(color_msg, color)
        if bold_msg:
            instr_len += len(bold_msg)
            instr+= Terminal.get_bold(bold_msg)   
        if msg:
            instr_len += len(msg)
            instr+= msg
        Menus._make_menu_footer(instr, instr_len)




    @staticmethod
    def open_menu():
        Terminal.launch_terminal()
        Terminal.hide_cursor()

    @staticmethod
    def close_menu():
        Menus._clear_cache()
        Terminal.close_terminal()
        Terminal.show_cursor()



    @staticmethod
    def read_control_key(timeout=0.1):
        """ Presently reads arrow keys up, down, left, right, esc, bckspc, & enter"""
        fd = sys.stdin.fileno()
        # Save old terminal read settings to restore, we are now reading raw bytes 
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            rlist, _, _ = select.select([fd], [], [], timeout)
            if rlist:
                ch1 = sys.stdin.read(1)
                if ch1 == '\x1b':  # ESC or arrow sequence
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        return {
                            'A': 'UP',
                            'B': 'DOWN',
                            'C': 'RIGHT',
                            'D': 'LEFT'
                        }.get(ch3, 'ESC')
                    return 'ESC'
                elif ch1 == '\r':
                    return 'ENTER'
                elif ch1 == '\x7f' or ch1 == '\x08':
                    return 'DELETE'
                elif ch1 == 'u' or 'U':
                    return 'UNDO'
                else:
                    return None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None
    
    @staticmethod
    def open_settings_menu(current, choices):
        options = {}
        Menus._setup_menu_environment(options, current=current, choices=choices)
        Menus.make_menu_header("Settings")
        instr = "[Esc] Quit"
        colored_len = len(instr)
        instr += " | [←] Save | [Enter][→] Select | [↑][↓] Change"
        ascii_len = 
        Menus.

        Menus.open_menu()

        logo = Terminal.get_logo()
        menu_title = f"\n{Terminal.get_color_bold("Diablo", "diablo red")} {Terminal.get_color_bold(title, "star")}\n{Terminal.important_line}"
        header = logo + menu_title
        try:
            while True: 
                Terminal._draw_menu(hovering, selected_option, exiting, hovering_suboption, options, current, format)
                key = Terminal.read_control_key(other_keys=['u', 'U'])
                if not key: 
                    continue
                
                if key == 'UP':
                    if not selecting: 
                        hovering = (hovering - 1) % menu_size
                    elif selecting:
                        hovering_suboption = (hovering_suboption - 1) % len(options[selected_option])
                elif key == 'DOWN':
                    if not selecting:
                        hovering = (hovering + 1) % menu_size
                    elif selecting:
                        hovering_suboption = (hovering_suboption + 1) % len(options[selected_option])
                elif key == 'ENTER':
                    if not selecting:
                        selecting = True
                        selected_option = list(options.keys())[hovering]
                        hovering_suboption = options[selected_option].index(current[selected_option])
                    elif selecting:        
                        current_option = list(options.keys())[hovering]
                        chosen_suboption = options[current_option][selected_option]
                        current[current_option] = chosen_suboption
                        changes_made = True
                        selecting = False
                        selected_option = None
                elif key == 'RIGHT':
                    if not selecting and not exiting: 
                        selecting = True
                    elif exiting:
                        exiting = False
                elif key == 'LEFT':
                    if not selecting and not exiting: 
                        exiting = True
                    elif selecting: 
                        selecting = False
                        selected_option = None 
                    elif exiting:
                        break 
                elif key == 'ESC':
                    if not selecting: 
                        return original
                    elif selecting:
                        current_option = list(options.keys())[hovering]
                        chosen_suboption = options[current_option][selected_option]
                        current[current_option] = chosen_suboption
                        changes_made = True
                        selecting = False
                        selected_option = None
        finally:
            sys.stdout.write(format["_.SHOW_CURSOR"] + format["_.EXIT_ALTERNATE_SCREEN"])
            Menus.close_menu()