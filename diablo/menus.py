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
    def _get_cache(name):
        var_name = f".TMP.{name}"
        if var_name in Menus._cache:
            return Menus._cache[f".TMP.{name}"]
        else:
            return None
        
    @staticmethod
    def _delete_cache_group(var):
        for group in Menus._cache.keys():
            if group.startswith(var):
                Menus._cache.pop(var, None)
    
    @staticmethod
    def _print_cache():
        Terminal.write("\nSETTINGS CACHE", "star")
        Terminal.pretty(Menus._cache)
    
    @staticmethod
    def _setup_menu_environment(options, option_names=None, current=None, choices=None):
        if not option_names:
            if not current and not choices:
                Terminal.dev_error("Improper use of menu, if calling with current and choices, don't call option_names")
            
            for option_name, _choices in choices.items():
                options[option_name] = ""
                type = "dropdown"
                if isinstance(_choices, list):
                    type = "dropdown"
                    rules = {}
                    updated_choices = []
                    for possible_choice in _choices:
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
                        else:
                            updated_choices.append(possible_choice)

                    options[option_name] = {
                            "current" : current[option_name],
                            "choices" : updated_choices,
                            "type" : type,
                            "rules" : rules
                    }

                elif isinstance(_choices, str):
                    rules = {}
                    if _choices.startswith("_.TEXT"):
                        text_rule = _choices
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

                    elif _choices.startswith("_.LIST"):
                        list_rule = _choices
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
                    else:
                        Terminal.dev_error(f"Improper naming of choice rule '{_choices}'.")       
                    
                    options[option_name] = {
                            "current" : current[option_name],
                            "choices" : None,
                            "type" : type,
                            "rules" : rules
                    }
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
    def _draw_header(lines):
        header_lines = Menus._get_cache("_.HEADER")
        if header_lines is None:
            return
        else:
            header_lines = header_lines.split("\n")
            for line in header_lines:
                lines.append(line)
    
    @staticmethod
    def _draw_footer():
        footer_msg = Menus._get_cache("_.FOOTER")
        if footer_msg is None:
            return
        footer_len = Menus._get_cache("_.FOOTER_LEN")
        right_shift = Menus._get_cache("_.FOOTER_RSHIFT")

        cols, rows = shutil.get_terminal_size()
        if right_shift:
            start_col = max(1, cols - footer_len + 1)
        else:
            start_col = 0

        Terminal.write_at(rows, start_col, footer_msg)

    @staticmethod
    def _draw_line(option_name, mode, lines):
        var = f"{mode}.{option_name}"
        line = Menus._get_cache(var)
        if line is None:
            Terminal.warn(f"Tried to draw line for {option_name} but couldn't find cache.")
            return
        else:
            possible_lines = line.split("\n")
            for line in possible_lines:
                lines.append(line)

    @staticmethod
    def _update_instruction(color_bold_msg=None, color_msg=None, bold_msg=None, msg=None, color="star", rshift=True):
        instr = ""
        instr_len = 0
        if color_bold_msg is not None:
            instr_len += len(color_bold_msg)
            instr+= Terminal.get_color_bold(color_bold_msg, color)
        if color_msg is not None:
            instr_len += len(color_msg)
            instr+= Terminal.get_color(color_msg, color)
        if bold_msg is not None:
            instr_len += len(bold_msg)
            instr+= Terminal.get_bold(bold_msg)   
        if msg is not None:
            instr_len += len(msg)
            instr+= msg
        Menus._make_menu_footer(instr, instr_len, rshift)

    @staticmethod
    def _set_text_prompt(options, hovering, choosing, padding=10):
        option_name = list(options.keys())[hovering]
        current_opt_format = Terminal.get_color_bold(f"{option_name.replace('_', " ").capitalize():>{padding}}", "star")
        pad = " "*padding
        choices_list = list(options[option_name]["choices"])

        mode = "choosing-hovering"
        left = current_opt_format if i == choosing else pad
        #Menus._add_cache(f"{mode}.{option_name}.{i}", f"{left} : {Terminal.get_reverse_bold(choices_list[i])}")
        Menus._add_cache(f"{mode}.{option_name}.{i}", f"{left} : ")
        mode = "choosing"
        Menus._add_cache(f"{mode}.{option_name}.{i}", f"{left} : ")        

    @staticmethod 
    def _set_dropdown(options, hovering, choosing, padding=10):
        option_name = list(options.keys())[hovering]
        current_opt_format = Terminal.get_color_bold(f"{option_name.replace('_', " ").capitalize():>{padding}}", "star")
        pad = " "*padding
        choices_list = list(options[option_name]["choices"])
        for i in range(0, len(choices_list)):
            mode = "choosing-hovering"
            left = current_opt_format if i == choosing else pad
            Menus._add_cache(f"{mode}.{option_name}.{i}", f"{left} : {Terminal.get_reverse_bold(choices_list[i])}")
            mode = "choosing"
            Menus._add_cache(f"{mode}.{option_name}.{i}", f"{left} : {choices_list[i]}")

    @staticmethod 
    def _draw_menu(hovering, choosing, options):
        """ Draw and clear memu accordingly to launch_menu """
        lines = []
        Menus._draw_header(lines)

        options_list = list(options.keys())
        for i, option in enumerate(options_list):
            option_name = str(option)
            option_format = f"{option_name.replace('_', " ").capitalize():>26}"
            current_choice = str(options[option_name]["current"])
            
            if i == hovering:
                if choosing is None:
                    Menus._draw_line(option_name, "hovering", lines)
                else: 
                    choices_list = list(options[option_name]["choices"])
                    for j, choice in enumerate(choices_list):
                        if j == choosing:
                            Menus._draw_line(f"{option_name}.{j}", "choosing-hovering", lines)
                        else:
                            Menus._draw_line(f"{option_name}.{j}", "choosing", lines)
            else: 
                if choosing is None:
                    Menus._draw_line(option_name, "not-hovering", lines)
                else:
                    Menus._draw_line(option_name, "not-choosing-hovering", lines)
        for i in range(5):
            lines.append("")

        Terminal.clear()
        Terminal.move_cursor_home()
        for line in lines: 
            Terminal.sys_write(f"{line}\n")
        Menus._draw_footer()
        Terminal.flush()

    @staticmethod
    def open_menu():
        Terminal.launch_terminal()
        Terminal.hide_cursor()

    @staticmethod
    def close_menu():
        Terminal.close_terminal()
        Terminal.show_cursor()
        Menus._print_cache()
        Menus._clear_cache()

    @staticmethod
    def update_menu(type, options, hovering, choosing, padding=10):
        if type == "dropdown":
            Menus._set_dropdown(options, hovering, choosing, padding)
        elif type == "text":
            Menus._set_text_prompt(options, hovering, choosing, padding)

    @staticmethod
    def _set_settings_menu(options, padding=10):
        padding = 26
        options_list = list(options.keys())
        for i, option in enumerate(options_list):
            mode = "not-hovering"
            option_name = str(option)
            option_format = f"{option_name.replace('_', " ").capitalize():>{padding}}"
            current_choice = str(options[option_name]["current"])
            not_hovering_line = f"{Terminal.get_bold(option_format)} : {current_choice}"
            Menus._add_cache(f"{mode}.{option_name}", not_hovering_line)

            mode = "hovering"
            hovering_line = Terminal.get_reverse_bold(f"{option_format} : {current_choice}")
            Menus._add_cache(f"{mode}.{option_name}", hovering_line)

            mode = "choosing"
            Menus._add_cache(f"{mode}.{option_name}", "")

            mode = "choosing-hovering"
            Menus._add_cache(f"{mode}.{option_name}", "")

            mode = "not-choosing-hovering"
            Menus._add_cache(f"{mode}.{option_name}", "")
    
    @staticmethod
    def _update_settings_menu(options, option_name=None, mode=None, updated=""):
        if isinstance(options, dict) and option_name is None and mode is None:
            Menus._set_settings_menu(option_name)
            return
        if option_name is not None and mode is not None:
            Menus._add_cache(f".TMP.{mode}.{option_name}", updated)

    @staticmethod
    def open_settings_menu(current, choices):
        options = {}
        padding = 26
        Menus._setup_menu_environment(options, current=current, choices=choices)
        Menus._make_menu_header("Settings")
        Menus._update_instruction(color_bold_msg="[Esc] Quit", bold_msg=" | [←] Save | [Enter][→] Select", msg=" | [↑][↓] Change")
        Menus._set_settings_menu(options, padding)
        Menus.open_menu()

        hovering = 0
        choosing = None
        exiting = False
        possible_choices = None
        menu_size = len(choices)
        changed = {}
        try:
            while True: 
                Menus._draw_menu(hovering, choosing, options)
                key = Terminal.read_control_key(other_keys=['u', 'U'])
                if not key: 
                    continue
                
                if key == 'UP':
                    if choosing is None: 
                        hovering = (hovering - 1) % menu_size
                    else:
                        choosing = (choosing - 1) % len(possible_choices)
                elif key == 'DOWN':
                    if choosing is None:
                        hovering = (hovering + 1) % menu_size
                    else:
                        choosing = (choosing + 1) % len(possible_choices)
                elif key == 'ENTER' or key == 'RIGHT':
                    if choosing is None:
                        selected_option = list(options.keys())[hovering]
                        possible_choices = options[selected_option]["choices"]
                        choosing = possible_choices.index(options[selected_option]["current"])
                        type = options[selected_option]["type"]
                        Menus.update_menu(type, options, hovering, choosing, padding=padding)
                        Menus._update_instruction(color_bold_msg="[←] Back", bold_msg=" | [Enter][→] Select")
                    else:        
                        selected_option = list(options.keys())[hovering]
                        chosen_choice = options[selected_option]["choices"][choosing]
                        options[selected_option]["current"] = chosen_choice
                        changes_made = True
                        choosing = None
                        possible_choices = None
                        Menus._set_settings_menu(options, padding)
                        Menus._update_instruction(color_bold_msg="[Esc] Quit", bold_msg=" | [←] Save | [Enter][→] Select", msg=" | [↑][↓] Change")

                elif key == 'LEFT':
                    if choosing is None: 
                        break
                    elif choosing is not None: 
                        choosing = None
                        possible_choices = None
                        Menus._set_settings_menu(options, padding)
                        Menus._update_instruction(color_bold_msg="[Esc] Quit", bold_msg=" | [←] Save | [Enter][→] Select", msg=" | [↑][↓] Change")

                    elif exiting:
                        break 

                elif key == 'u' or 'U':
                    prev_change = Menus._actions.pop()
                    for option, prev_choice in prev_change:
                        options[option]["current"] = prev_choice
                        current[option] = prev_choice

                elif key == 'ESC':
                    if not exiting: 
                        exiting = True
                    elif exiting:
                        break

        finally:
            Menus.close_menu()