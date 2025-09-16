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
from importlib.resources import files

class Terminal: 

    preset = {
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "light blue": (26, 247, 253),
        "light yellow": (255, 213, 0),
        "diablo red": (255, 25, 7),
        "star": (255, 213, 0)
    }

    ansi_codes = {
        "ENTER_ALTERNATE_SCREEN" : "\x1b[?1049h",
        "EXIT_ALTERNATE_SCREEN" :"\x1b[?1049l",
        "HIDE_CURSOR" : "\x1b[?25l",
        "SHOW_CURSOR" : "\x1b[?25h",
        "CLEAR_SCREEN" : "\x1b[2J",
        "MOVE_CURSOR_HOME" : "\x1b[H",
    }

    version = "Version Beta 0.1"
    important_line = "______________________________________________ _________________ __________ _______ ___ __ _ "
    line = "___________________________ ____________ _______ ____ ___ __ _"
    intro_slogan = dedent("""An Open-Source VPN & LAN Protection Service""")

    BANNER_PATH = files("diablo.assets").joinpath("banner.txt")

    _animation_thread = None
    _stop_animation = threading.Event()

    """ Colored text helpers """
    @staticmethod
    def _findansi(msg, rgb):
        r, g, b = rgb
        ansi = "" 
        for c in msg:
            ansi+= f"\x1b[38;2;{r};{g};{b}m{c}\x1b[0m"
        return ansi
        
    @staticmethod
    def _get_ansi_b(msg):
        ansi = "" 
        #for c in msg:
        ansi+= f"\x1b[1m{msg}\x1b[0m"
        return ansi
    
    @staticmethod
    def _get_ansi_cb(msg, rgb):
        r, g, b = rgb
        ansi = "" 
        for c in msg:
            ansi+= f"\x1b[1m\x1b[38;2;{r};{g};{b}m{c}\x1b[0m"
        return ansi      

    @staticmethod
    def get_bold(msg):
        return f"\x1b[1m{msg}\x1b[0m"
    
    @staticmethod
    def get_reverse(msg):
        return f"\x1b[7m{msg}\x1b[0m"
    
    @staticmethod
    def get_reverse_bold(msg):
        return f"\x1b[1m\x1b[7m{msg}\x1b[0m"
    
    @staticmethod
    def get_dim(msg):
        return f"\x1b[2m{msg}\x1b[0m"
    
    @staticmethod
    def get_underline(msg):
        return f"\x1b[4m{msg}\x1b[0m"
    
    @staticmethod 
    def get_color(msg, color=None, rgb=None):
        if not color and not rgb:
            return Terminal._findansi(msg, Terminal.preset["white"])
        if color: 
            return Terminal._findansi(msg, Terminal.preset[color])
        elif rgb: 
            return Terminal._findansi(msg, rgb)   
        
    @staticmethod
    def get_color_bold(msg, color=None, rgb=None):
        if not color and not rgb:
            return Terminal._get_ansi_cb(msg, Terminal.preset["white"])
        if color: 
            return Terminal._get_ansi_cb(msg, Terminal.preset[color])
        elif rgb: 
            return Terminal._get_ansi_cb(msg, rgb)   

    """ Standard Output Management & Helpers """    
    @staticmethod
    def newline(lines=1):
        print("\n" * (lines-1))

    @staticmethod
    def print_intro():
        with open(Terminal.BANNER_PATH, "r") as f:
            logo = f.read()
        version = Terminal.get_color_bold(Terminal.version, "star")
        line = Terminal.get_bold(Terminal.important_line)
        slogan = Terminal.get_bold(Terminal.intro_slogan)
        intro = f"{logo}{version}\n{line}\n{slogan}"
        print(intro)
    
    @staticmethod
    def get_logo():
        with open(Terminal.BANNER_PATH, "r") as f:
            return f.read()

    @staticmethod
    def write(msg, color=None, rgb=None):
        if not color and not rgb:
            print(msg)
            return
        if color: 
            print(Terminal._findansi(msg, Terminal.preset[color]))
        elif rgb: 
            print(Terminal._findansi(msg, rgb))
    
    @staticmethod
    def sys_write(msg):
        sys.stdout.write(msg)
    
    @staticmethod
    def flush():
        sys.stdout.flush()
    
    @staticmethod
    def pretty(msg):
        pprint.pprint(msg)

    @staticmethod
    def log(msg):
        marker = Terminal._get_ansi_cb("[+]", Terminal.preset["light blue"])
        msg_coded = Terminal._findansi(msg, Terminal.preset["light blue"])
        print(f"{marker} {msg_coded}")
    
    @staticmethod
    def warn(msg):
        msg_type = Terminal._get_ansi_cb("[-] Warning:", Terminal.preset["light yellow"])
        msg_coded = Terminal._findansi(msg, Terminal.preset["light yellow"])
        print(f"{msg_type} {msg_coded}")

    @staticmethod
    def error(msg, exit=True):
        msg_type = Terminal._get_ansi_cb("[-] Error:", Terminal.preset["red"])
        msg_coded = Terminal._findansi(msg, Terminal.preset["red"])
        print(f"{msg_type} {msg_coded}")
        if exit: 
            sys.exit(1)
    
    @staticmethod
    def dev_error(msg, exit=True):
        msg_type = Terminal._get_ansi_cb("[-] Developer Error:", Terminal.preset["red"])
        msg_coded = Terminal._findansi(msg, Terminal.preset["white"])
        sys.stdout.write(f"{msg_type} {msg_coded}")
        if exit:
            sys.exit(1)

    @staticmethod
    def success(msg):
        msg_type = Terminal._get_ansi_cb("[+] Success:", Terminal.preset["green"])
        msg_coded = Terminal._findansi(msg, Terminal.preset["green"])
        print(f"{msg_type} {msg_coded}")

    @staticmethod
    def quick_message(msg):
        name = Terminal._findansi("Diablo: ", Terminal.preset["diablo red"])
        message = Terminal._findansi(msg, Terminal.preset["white"])
        print(f"{name}{message}")
    
    @staticmethod 
    def section_header(title, color="star", ret=False):
        title_ansi = Terminal._findansi(title, Terminal.preset[color])
        header = f"{title_ansi}\n{Terminal.line}"
        if not ret: 
            return header
        print(header)

    @staticmethod
    def animate(states, iter=6, final=None, pause=0.25):
        """ Single threaded animation"""
        for _ in range(iter):  # cycles through animation 3 times
            for state in states:
                sys.stdout.write(f"\r{state}")
                sys.stdout.flush()
                time.sleep(pause)

        if final: 
            sys.stdout.write(f"\r{final}\n")
            sys.stdout.flush()

    @staticmethod
    def _animate_loop(states, pause):
        """ Handler for multithreaded animation"""
        while not Terminal._stop_animation.is_set():
            for state in states:
                if Terminal._stop_animation.is_set():
                    break
                sys.stdout.write(f"\r{state}")
                sys.stdout.flush()
                time.sleep(pause)

    @staticmethod
    def start_animation(states, pause=0.25):
        """ Start animation thread """
        Terminal._stop_animation.clear()
        Terminal._animation_thread = threading.Thread(
            target=Terminal._animate_loop, args=(states, pause)
        )
        Terminal._animation_thread.daemon = True
        Terminal._animation_thread.start()

    @staticmethod
    def stop_animation(final=None):
        """ End animation thread """
        Terminal._stop_animation.set()
        if Terminal._animation_thread is not None:
            Terminal._animation_thread.join()
        if final:
            sys.stdout.write(f"\r{final}\n")
            sys.stdout.flush()

    @staticmethod
    def connecting_animation():
        """ Test """
        states = ["[+] Connecting", "[ ] Connecting"]
        for _ in range(6):  # cycles through animation 3 times
            for state in states:
                sys.stdout.write(f"\r{state}")
                sys.stdout.flush()
                time.sleep(0.25)

        # Once connected
        connected = Terminal._findansi("[Success] Connected", Terminal.preset["green"])
        sys.stdout.write(f"\r{connected}\n")
        sys.stdout.flush()
    
    """ Standard Input Managers & Helpers """
    @staticmethod
    def prompt_response(name=None, options=[], yes_no=False, yes_no_enter=False, mercy=True):
        """ Prompts a response from user, option to determine if reponse is valid, 
            can be used for custom command prompt"""
        prompt = ">> "
        valid = True
        yes = False 
        """ Ideally, don't set name and options to non-default together, works but weird syntax """
        if name: 
            prompt = f"{name}@diablo {prompt}"
        if options: 
            prompt = f"{options} {prompt}" 
        if yes_no or yes_no_enter: 
            if options: 
                Terminal.error("Don't call yesno and options together, just call yesno, prompt_response handles options for you")
                return
            options = ["yes", "no", "n", "y"]
            prompt = Terminal.get_bold("(yes/no)") + " >> "
            if yes_no_enter: 
                """ yesnoenter takes precedence if yesno called as well """
                options.append("")
                prompt = Terminal.get_bold("(y/n) or (Enter)") + " >> "

        response = input(prompt).strip()

        if options: 
            if not response in options: 
                valid = False       
            elif yes_no or yes_no_enter:
                yes_options = options
                yes_options.remove("n")
                yes_options.remove("no")
                if response in yes_options:
                    yes = True
                
        if not valid: 
            Terminal.warn(f"Invalid input. Your options are {options}")
            if mercy: 
                return Terminal.prompt_response(name, options)
        
        return response, yes
    
    """ Terminal Screen Control """
    @staticmethod
    def clear():
        sys.stdout.write("\x1b[2J")

    @staticmethod
    def launch_terminal():
        sys.stdout.write("\x1b[?1049h")
    
    @staticmethod
    def close_terminal():
        sys.stdout.write("\x1b[?1049l")

    """ Cursor Controls """
    @staticmethod 
    def hide_cursor():
        sys.stdout.write("\x1b[?25l")
    
    @staticmethod 
    def show_cursor():
        sys.stdout.write("\x1b[?25h")

    @staticmethod 
    def save_cursor():
        sys.stdout.write("\x1b 7") 

    @staticmethod 
    def restore_cursor():
        sys.stdout.wriet("\x1b 8")

    @staticmethod
    def move_cursor_home():
        sys.stdout.write("\x1b[H")  
    
    def move_cursor(line, col):
        sys.stdout.write(f"\x1b[{line};{col}H")

    @staticmethod 
    def move_cursor_up(lines=None):
        if lines:
            sys.stdout.write(f"\x1b[{lines}A")
        else:
            sys.stdout.write("\x1b[A")
            
    @staticmethod 
    def move_cursor_up(lines=None):
        if lines:
            sys.stdout.write(f"\x1b[{lines}B")
        else:
            sys.stdout.write("\x1b[B")   
            
    @staticmethod
    def write_at(row, col, msg):
        sys.stdout.write(f"\x1b[{row};{col}H{msg}\x1b[0m")
    
    """ Terminal UI - Menu Support """

    @staticmethod
    def read_control_key(other_keys=[],timeout=0.1):
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
                elif ch1 in other_keys:
                    return ch1
                else:
                    return None  
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    @staticmethod
    def _get_styled(key, msg, format, default=None):
        """ Obtain correct ansi of line in menu based on format specification, store in format as cache after first call """

        style_cache = f"_.TMP_STY_{key}"
        if style_cache in format: 
            return format[style_cache]
        
        key = str(key)
        groups = format["_STYLES"]
        style = None

        if key in groups:
            style = groups[key]
        elif default:
            if default in groups:
                style = groups[default]

        styled_line = msg
        if style: 
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

        format_cache = {}
        format_cache[style_cache] = styled_line
        format.update(format_cache)
        return styled_line

    @staticmethod
    def _draw_bottom(msg):
        cols, rows = shutil.get_terminal_size()
        start_col = max(1, cols - len(msg) + 1)
        sys.stdout.write(f"\x1b[{rows};{start_col}H{msg}\x1b[0m")
    
    @staticmethod
    def _draw_instruction(instr_menu_state, format):
        """ Draws formatted instructions to stdout, uses dict 'format' as cache to avoid performance constraint"""

        instr_cache = f"_.TMP_INS{instr_menu_state}"
        instr_size_cache = f"_.TMP_INS{instr_menu_state}_SIZE"
        if instr_cache in format and instr_size_cache in format: 
            inst = format[instr_cache]
            raw_size = int(format[instr_size_cache])
            cols, rows = shutil.get_terminal_size()
            start_col = max(1, cols - raw_size + 1)
            sys.stdout.write(f"\x1b[{rows};{start_col}H{inst}\x1b[0m")
            return
        
        instr_menu = format[instr_menu_state]

        if "_ORDER" in instr_menu:
            order = instr_menu["_ORDER"]
            instructions = []
            instr_raw = []
            for instr_name in order: 
                instr_name = str(instr_name)

                if instr_name in instr_menu: 
                    instr_unformatted = instr_menu[instr_name]
                elif instr_name in format["_DEFAULTS"]:
                    defaults = format["_DEFAULTS"]
                    instr_unformatted = defaults[instr_name]
                else:
                    sys.stdout.write(format["_.SHOW_CURSOR"] + format["_.EXIT_ALTERNATE_SCREEN"])
                    Terminal.dev_error(dedent(f"""Invalid formatting, '_draw_instructions' was expecting {instr_name} in instr_menu {instr_menu}, or 
                                        {instr_name} in {defaults}"""))
                    exit()

                if isinstance(instr_unformatted, dict):
                    if not "_" in instr_unformatted:
                        sys.stdout.write(format["_.SHOW_CURSOR"] + format["_.EXIT_ALTERNATE_SCREEN"])
                        Terminal.dev_error(dedent(f"""Invalid formatting, '_draw_instructions' was expecting \'_\' in {instr_menu}/{instr_unformatted}.
                                            If adding styling to instruction, make sure to reference the text of the instruction with \'_\'"""))
                        exit()   
                    instr_text = instr_unformatted["_"] 
                    instr_raw.append(instr_text)              
                    if "_STYLE" in instr_unformatted:
                        style = instr_unformatted["_STYLE"]
                        if isinstance(style, dict):
                            if "color-bold" in style:
                                color = style["color-bold"]
                                instructions.append(Terminal.get_color_bold(instr_text, color))
                            elif "color" in style:
                                color = style["color"]
                                instructions.append(Terminal.get_color(instr_text, color))
                            else: 
                                instructions.append(instr_text)
                        else: 
                            style = str(style)
                            if style == "bold":
                                instructions.append(Terminal.get_bold(instr_text))
                            elif style == "dim":
                                instructions.append(Terminal.get_bold(instr_text)) 
                            else: 
                                instructions.append(instr_text)
                    else: 
                        instructions.append(instr_text)
                else: 
                    instr_formatted = str(instr_unformatted)
                    instructions.append(instr_formatted)
                    instr_raw.append(instr_formatted)

            instr_statement = " | ".join(instructions)
            instr_raw_stmt = " | ".join(instr_raw)
            instr_raw_size = len(instr_raw_stmt)
            format_cache = {}
            format_cache[instr_cache] = instr_statement
            format_cache[instr_size_cache] = instr_raw_size
            format.update(format_cache)

            cols, rows = shutil.get_terminal_size()
            start_col = max(1, cols - instr_raw_size + 1)
            sys.stdout.write(f"\x1b[{rows};{start_col}H{instr_statement}\x1b[0m")

        else: 
            return

    @staticmethod 
    def _draw_dropdown(left, right, selected_option, options, hovering_suboption, lines):
        """ Simple dropdown option, user chooses from a set of options, starts at current option """
        sub_options = options[selected_option]
        current_idx = sub_options.index(right)
        left_selec = Terminal.get_color_bold(left, "star")
        pad = " "*26

        for i in range(0, len(sub_options)):
            from_current_idx = (i + current_idx) % len(sub_options)

            if hovering_suboption == from_current_idx:
                if i == 0:
                    lines.append(f"{left_selec} : {Terminal.get_reverse(sub_options[from_current_idx])}")
                else: 
                    lines.append(f"{pad} : {Terminal.get_reverse(sub_options[from_current_idx])}")
            else: 
                if i == 0:
                    lines.append(f"{left_selec} : {sub_options[from_current_idx]}")
                else:
                    lines.append(f"{pad} : {sub_options[from_current_idx]}")

    @staticmethod 
    def _draw_menu(hovering, selected_option, exiting, hovering_suboption, options, current, format):
        """ Draw and clear memu accordingly to launch_menu """
        lines = []
        header = format["_.HEADER"]
        header_lines = header.split("\n")
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
    def launch_menu(title, options : dict, original=None, user_format=None, buffer=15):
        """ Currently supports '1D' or '2D' options, as in menu of options, when selected, another menu of options if 2D """

        logo = Terminal.get_logo()
        menu_title = f"\n{Terminal.get_color_bold("Diablo", "diablo red")} {Terminal.get_color_bold(title, "star")}\n{Terminal.important_line}"
        header = logo + menu_title

        """ Initialize canvas """
        possible_types = {"dropdown", "text", "text-ip", "list", "list-int", "dropdown-text", "dropdown-text-int"}
        current = {}
        options_size_1d = len(options)
        total_canv_size = options_size_1d
        """ 'format' dictionary which enables flexible use of 'launch_menu' by editing 'user_format', doubles as
            reference memory & cache storage for 'draw_menu' """
        format = {
            "_.HEADER" : header,
            "_.ENTER_ALTERNATE_SCREEN" : "\x1b[?1049h",
            "_.EXIT_ALTERNATE_SCREEN" :"\x1b[?1049l",
            "_.HIDE_CURSOR" : "\x1b[?25l",
            "_.SHOW_CURSOR" : "\x1b[?25h",
            "_.CLEAR_SCREEN" : "\x1b[2J",
            "_.MOVE_CURSOR_HOME" : "\x1b[H",
            "_.POSSIBLE_TYPES" : possible_types,
            "_DEFAULTS" : {
                "_INSTRUCTION_LEFT" : {
                    "_" : "[←] Exit",
                    "_STYLE" : "bold"
                },
                "_INSTRUCTION_UP_DOWN" : "[↑][↓] Change",
                "_INSTRUCTION_ESCAPE" : "[Esc] Exit",
            },
            "_INSTRUCTION_HOME" : {
                "_ORDER" : ["_INSTRUCTION_LEFT", "_INSTRUCTION_ENTER", "_INSTRUCTION_RIGHT", "_INSTRUCTION_UP_DOWN"],
                "_INSTRUCTION_ENTER" : "[Enter]",
                "_INSTRUCTION_RIGHT" : "[→] Select",
            },
            "_INSTRUCTION_SELECTING" : {
                "_ORDER" : ["_INSTRUCTION_LEFT", "_INSTRUCTION_ENTER", "_INSTRUCTION_UP_DOWN"],
                "_INSTRUCTION_ENTER" : "[Enter] Select",
            },
            "_INSTRUCTION_CONFIRMING" : {
                "_ORDER" : ["_INSTRUCTION_LEFT", "_INSTRUCTION_ENTER"],
                "_INSTRUCTION_ENTER" : "[Enter] Confirm",
            },
            "_INSTRUCTION_EXITING": {
                "_ORDER" : ["_INSTRUCTION_LEFT", "INSTRUCTION_RIGHT"],
                "_INSTRUCTION_RIGHT" : "[→] Return"
            },
            "_STYLES" : {
                "_LEFT" : "bold"
            },
            "_OPTIONS" : {},
            "_TYPES" : {},
            "_WARNINGS" : {},
            "_RULES" : {},
            "_PARENTS" : {}
        }
        """ Validate correct use of user_format, 'launch_menu' follows a pretty exact structure """
        if user_format: 
            for key, _ in user_format.items(): 
                key = str(key)
                if key.startswith("_."):
                    Terminal.dev_error(dedent("""You are trying to modify a protected format value, demarked by '_.' at the start.
                                                 Modifying this value could cause the program to crash or behave unpredictably. Values
                                                 starting with '_' can be modified, and are declared as default format settings."""))
                    return
                if not key.isupper() or not key.startswith("_"):
                    Terminal.dev_error(dedent("""Invalid format value. All keys in format begin with '_' and are uppercase. However,
                                                 there are some values within the keys that are lowercased, and valid. Typically, 
                                                 these are user or config variables, or optional values that are not necessary for 
                                                 the program to run. For example, '_min' and '_max'. '_' at start is a senstive, 
                                                 & will be interpreted as a format var. Be careful not to name user created vars
                                                 like settings as such."""))
                    return
                if key not in format: 
                    Terminal.dev_error(dedent("""Unrecognized format value. All valid keys have been declared in launch_menu (terminal.py),
                                                 and are free to be modified, unless protected (starts with '_.'"""))
                    return
            format.update(user_format)

        idx = 0 
        type = {}
        for key, val in options.items():
            """ Save original layout of menu if specified (used especially for settings) """
            if isinstance(val, list):
                if original:
                    current[key] = original[key]
                else:
                    current[key] = str(val[0])
                dist_to_bottom = (idx + 1) + (len(val) - 1)
                if dist_to_bottom > total_canv_size:
                    total_canv_size = dist_to_bottom
            else: 
                if original:
                    current[key] = original[key]
                else: 
                    current[key] = str(val)
            """ Set options, defaults to (yes, no) if not specified """
            options_tmp = format["_OPTIONS"]
            if not key in options_tmp:
                options_tmp[key] = ["yes", "no"]
            """ Determine type of input for option field """
            type_tmp = format["_TYPES"]
            if not key in type_tmp:
                type_tmp[key] = "dropdown"

            idx+=1

        menu_size = options_size_1d
        buffer = (total_canv_size - menu_size) + buffer

        """ Listen for pressed keys and draw menu accordingly """
        hovering = 0 
        selecting = False
        exiting = False
        menu_size = options_size_1d
        selected_option = None
        hovering_suboption = 0
        changes_made = False
        key = None
        """ Launch alternate terminal instead of normal """
        #sys.stdout.write(format["_.ENTER_ALTERNATE_SCREEN"] + format["_.HIDE_CURSOR"])
        sys.stdout.write(format["_.ENTER_ALTERNATE_SCREEN"] )
        sys.stdout.write(format["_.HIDE_CURSOR"])
        try:
            while True: 
                Terminal._draw_menu(hovering, selected_option, exiting, hovering_suboption, options, current, format)
                key = Terminal.read_control_key()
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
            pprint.pprint(format)





            



        
        











        




