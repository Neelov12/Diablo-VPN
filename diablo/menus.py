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
                print(option_name)
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
    def _set_style(side, state, type, color="star"):
        if type == "color" or "color-bold":
            style = {}
            style[type] = color
            Menus._add_cache(f"_.STYLE_{side}_{state}", style)
        else:
            Menus._add_cache(f"_.STYLE_{side}_{state}", type)

    @staticmethod
    def _get_style(msg, side, state):
        """ Obtain correct ansi of line in menu based on format specification, store in format as cache after first call """

        style = Menus._get_cache(f"_.STYLE.{side}.{state}")
        if not style: 
            return msg

        if isinstance(style, dict):
            if "color" in style:
                color = style["color"]
                styled_line = Terminal.get_color(msg, color)
            elif "color-bold" in style:
                color = style["color-bold"]
                styled_line = Terminal.get_color_bold(msg, color)
        else:
            style = str(style)
            if style == "bold":
                styled_line = Terminal.get_bold(msg)
            elif style == "dim":
                styled_line = Terminal.get_dim(msg)   
            elif style == "reverse-bold":
                styled_line = Terminal.get_reverse_bold(msg)

        return styled_line

    @staticmethod
    def _get_line(option_name, state, option_format=None, choice_format=None):
        var_name = f"_.LINE.{state}.{option_name}"
        line = Menus._get_cache(var_name)
        if line:
            return line
        left = Menus._get_style(option_format, "left", state)
        right = Menus._get_style(choice_format, "right", state)
        Menus._add_cache(var_name, f"{left} : {right}")
        return Menus._add_cache(var_name)

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
    def _draw_footer():
        footer_msg = Menus._get_cache("_.FOOTER")
        footer_len = Menus._get_cache("_.FOOTER_LEN", len)
        right_shift = Menus._get_cache("_.FOOTER_RSHIFT")

        cols, rows = shutil.get_terminal_size()
        if right_shift:
            start_col = max(1, cols - footer_len + 1)
        else:
            start_col = 0

        Terminal.write_at(rows, start_col, footer_msg)

    @staticmethod 
    def _dropdown(choosing, option_name, option_format, current_choice, options, lines):
        """ Simple dropdown option, user chooses from a set of options, starts at current option """
        choices = options[option_name]["choices"]
        choice_index = choices.index(current_choice)
        left_format = Menus._get_style(option_format, "left", "choosing")
        pad = " "*26

        for i in range(0, len(choices)):
            from_current_index = (i + choice_index) % len(choices)

            if choosing == from_current_index:
                left = left_format if i == 0 else pad
                lines.append(f"{left} : {Menus._get_style(choices[from_current_index], "right", "choosing")}")
            else: 
                left = left_format if i == 0 else pad
                lines.append(f"{left} : {choices[from_current_index]}")

    @staticmethod 
    def _draw_menu(hovering, choosing, options):
        """ Draw and clear memu accordingly to launch_menu """
        lines = []
        header_lines = Menus._get_cache("_.HEADER").split("\n")
        for line in header_lines:
            lines.append(line)
        options_list = list(options.keys())
        for i, option in enumerate(options_list):
            option_name = str(option)
            option_format = f"{option_name.replace('_', " ").capitalize():>26}"
            current_choice = str(options[option_name]["current"])
            
            if i == hovering:
                if not choosing:
                    lines.append(Terminal.get_reverse_bold(f"{option_format} : {current_choice}"))
                else: 
                    type = options[option_name]["type"]
                    if type == "dropdown":
                        Menus._dropdown(choosing, option_name, option_format, current_choice, options, lines)

            else: 
                if not choosing:
                    lines.append(Menus._get_line(option_name, "hovering", option_format, current_choice))
            
        for i in range(5):
            lines.append("")

        sys.stdout.write(format["_.CLEAR_SCREEN"] + format["_.MOVE_CURSOR_HOME"])
        Terminal.clear()
        Terminal.move_cursor_home()
        
        for line in lines: 
            Terminal.sys_write(f"{line}\n")

        Menus._draw_footer()
        
        Terminal.flush()

    
    @staticmethod
    def open_settings_menu(current, choices):
        options = {}
        Menus._setup_menu_environment(options, current=current, choices=choices)
        Menus._make_menu_header("Settings")
        Menus._update_instruction(color_bold_msg="[Esc] Quit", bold_msg=" | [←] Save", msg="| [Enter][→] Select | [↑][↓] Change")
        Menus._set_style("left", "hovering", "bold")
        Menus._set_style("left", "choosing", "color-bold")
        Menus._set_style("right", "choosing", "reverse")

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
                        options[option]["current"] = prev_choice
                        current[option] = prev_choice

                elif key == 'ESC':
                    if not exiting: 
                        break
                    if exiting:
                        break

        finally:
            sys.stdout.write(format["_.SHOW_CURSOR"] + format["_.EXIT_ALTERNATE_SCREEN"])
            Menus.close_menu()