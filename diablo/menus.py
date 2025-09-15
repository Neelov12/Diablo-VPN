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

    @staticmethod
    def _make_menu_footer(footer, len, right_shift=False):
        Menus._add_cache("_.FOOTER", footer)
        Menus._add_cache("_.FOOTER_LEN", len)
        Menus._add_cache("_.FOOTER_RSHIFT", right_shift)

    @staticmethod
    def _update_instruction(msg=None, color_bold_msg=None, color_msg=None, bold_msg=None, color="star", rshift=True):
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
        Menus._make_menu_footer(instr, instr_len, rshift)

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
    def _draw_menu(hovering, choosing, options):
        """ Draw and clear memu accordingly to launch_menu """
        lines = []
        header_lines = Menus._get_cache("_.HEADER").split("\n")
        for line in header_lines:
            lines.append(line)
        keys = list(current.keys())
        for i, option in enumerate(keys):
            option = str(option)
            left = f"{option.replace('_', " ").capitalize():>26}"
            sub_option = str(current[option])
            right = sub_option
            
            if i == hovering:
                if not selected_option:
                    lines.append(Terminal.get_reverse_bold(f"{left} : {right}"))
                elif selected_option == option: 
                    type_of = format["_TYPES"]
                    type = type_of[option]
                    if type == "dropdown":
                        Terminal._draw_dropdown(left, right, selected_option, options, hovering_suboption, lines)
                        for i in range(0, len(keys) - i):
                            lines.append("")

            else: 
                if not selected_option:
                    left = Terminal._get_styled(option, left, format, default="_LEFT")
                    right = Terminal._get_styled(sub_option, right, format, default="_RIGHT")
                    lines.append(f"{left} : {right}")
            
            
        for i in range(5):
            lines.append("")

        sys.stdout.write(format["_.CLEAR_SCREEN"] + format["_.MOVE_CURSOR_HOME"])
        
        for line in lines: 
            sys.stdout.write(f"{line}\n")

        if not selected_option:
            Terminal._draw_instruction("_INSTRUCTION_HOME", format)
        elif selected_option:
            Terminal._draw_instruction("_INSTRUCTION_SELECTING", format)
        sys.stdout.flush()

    
    @staticmethod
    def open_settings_menu(current, choices):
        options = {}
        Menus._setup_menu_environment(options, current=current, choices=choices)
        Menus._make_menu_header("Settings")
        Menus._update_instruction(color_bold_msg="[Esc] Quit", bold_msg=" | [←] Save", msg="| [Enter][→] Select | [↑][↓] Change")

        hovering = 0
        choosing = None
        exiting = False
        menu_size = len(choices)
        changed = {}
        try:
            while True: 
                Terminal._draw_menu(hovering, choosing, options)
                key = Terminal.read_control_key(other_keys=['u', 'U'])
                if not key: 
                    continue
                
                if key == 'UP':
                    if not choosing: 
                        hovering = (hovering - 1) % menu_size
                    else:
                        choosing = (choosing - 1) % len(chosen_choice)
                elif key == 'DOWN':
                    if not choosing:
                        hovering = (hovering + 1) % menu_size
                    else:
                        hovering_suboption = (hovering_suboption + 1) % len(chosen_choice)
                elif key == 'ENTER':
                    if not choosing:
                        selected_option = list(choices.keys())[hovering]
                        choosing = choices[selected_option].index(current[selected_option])
                    else:        
                        current_option = list(choices.keys())[hovering]
                        chosen_choice = choices[current_option][choosing]
                        original_choice = choices[current_option]
                        changed[current_option] = chosen_choice
                        Menus._actions.append(changed)
                        current[current_option] = chosen_choice

                        changes_made = True
                        choosing = None
                elif key == 'RIGHT':
                    if not choosing and not exiting: 
                        choosing = True
                    elif exiting:
                        exiting = False
                elif key == 'LEFT':
                    if not choosing and not exiting: 
                        exiting = True
                    elif choosing: 
                        choosing = False
                        selected_option = None 
                    elif exiting:
                        break 
                elif key == 'u' or 'U':
                    prev_change = Menus._actions.pop()
                    for option, prev_choice in prev_change:
                        current[option] = prev_choice

                elif key == 'ESC':
                    if not exiting: 
                        break
                    if exiting:
                        break

        finally:
            sys.stdout.write(format["_.SHOW_CURSOR"] + format["_.EXIT_ALTERNATE_SCREEN"])
            Menus.close_menu()