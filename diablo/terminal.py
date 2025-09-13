import sys 
from datetime import datetime
import time
import threading
import curses
import termios
import tty
import select
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

    line = "___________________________ ____________ _______ ____ ___ __ _"
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
        for c in msg:
            ansi+= f"\x1b[1m{c}\x1b[0m"
        return ansi
    
    @staticmethod
    def _get_ansi_cb(msg, rgb):
        r, g, b = rgb
        ansi = "" 
        for c in msg:
            ansi+= f"\x1b[1m\x1b[38;2;{r};{g};{b}m{c}\x1b[0m"
        return ansi    
    
    @staticmethod
    def _get_ansi_r(msg):
        ansi = ""
        #for c in msg:
        ansi = f"\x1b[7m{msg}\x1b[0m"
        return ansi

    @staticmethod
    def get_bold(msg):
        return Terminal._get_ansi_b(msg)
    
    @staticmethod
    def get_reverse(msg):
        return Terminal._get_ansi_r(msg)
    
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
            intro = f.read()
        print(intro)
        
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
    def log(msg):
        line = f"[+] {msg}"
        print(Terminal._findansi(line, Terminal.preset["light blue"]))
    
    @staticmethod
    def warn(msg):
        line = f"[-] Warning: {msg}"
        print(Terminal._findansi(line, Terminal.preset["light yellow"]))

    @staticmethod
    def error(msg):
        line = f"[-] Error: {msg}"
        print(Terminal._findansi(line, Terminal.preset["red"]))

    @staticmethod
    def success(msg):
        line = f"[Success] {msg}"
        print(Terminal._findansi(line, Terminal.preset["green"]))

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
            prompt = "(yes/no) >> "
            if yes_no_enter: 
                """ yesnoenter takes precedence if yesno called as well """
                options.append("")
                prompt = "(y/n) or press Enter >> "

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
        
    """ Support for Terminal psuedo-UI """
    @staticmethod
    def _launch_menu(title, options, original):
        """ Launches terminal menu allowing user to navigate & select options using arrow keys and enter,
            takes as required arguments header (menu title), dictionary of options, and original options """
        options_map = options
        current = original.copy()
        code = 221
        header_size = 4

        def draw_menu(stdscr, selected, active_setting=None, active_choice=None, done=False):
            """ Outs menu options to terminal """
            stdscr.clear()
            stdscr.addstr(0, 1, "Diablo ", curses.A_BOLD | curses.color_pair(code))
            stdscr.addstr(title, curses.A_BOLD)      
            stdscr.addstr(1, 1, Terminal.line, curses.A_BOLD)      
            for idx, key in enumerate(options_map):
                value = current[key]
                line = f"{key.replace('_', ' ').capitalize():<25} : {value}"

                if idx == selected:
                    stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(idx + header_size, 2, line)
                    stdscr.attroff(curses.A_REVERSE)
                    
                    if active_setting == key:
                        choices = options_map[key]
                        for i, choice in enumerate(choices):
                            style = curses.A_BOLD | curses.color_pair(code) if i == active_choice else curses.A_DIM
                            stdscr.addstr(idx + header_size + 1 + i, 6, f"> {choice}", style)

                        stdscr.addstr(idx + header_size + 2 + len(choices), 6, f"{" "*15}[←] Go Back")
                else: 
                    if not active_setting:
                        stdscr.addstr(idx + header_size, 2, line)


            if not active_setting:
                if done: 
                    stdscr.addstr(len(options_map) + 5, 2, "Are you sure you want to save these changes? ", curses.A_BOLD | curses.color_pair(code))
                    stdscr.addstr("[←] or [Enter] Yes | [→] No, go back")
                else:
                    stdscr.addstr(len(options_map) + 5, 2, "[Esc] Exit without saving | [←] Save | [Enter] Edit | [↑][↓] Change", curses.A_DIM)


            stdscr.refresh()

        def menu_logic(stdscr):
            curses.curs_set(0)
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(code, code+1, -1)

            selected = 0
            active_setting = None
            active_choice = 0
            editing = False
            done = False
            changed = False

            while True:
                draw_menu(stdscr, selected, active_setting, active_choice if editing else None, done=done)
                key = stdscr.getch()

                if key == curses.KEY_UP and not editing:
                    selected = (selected - 1) % len(options_map)
                elif key == curses.KEY_DOWN and not editing:
                    selected = (selected + 1) % len(options_map)
                elif key == curses.KEY_LEFT:  
                    if editing:
                        editing = False
                        active_setting = None
                    elif done:
                        break 
                    else: 
                        if not changed: 
                            break
                        done = True
                elif key == curses.KEY_RIGHT: 
                    if not editing: 
                        if done: 
                            done = False

                elif key in [10, 13]:  # ENTER
                    if done: 
                        break
                    if editing:
                        setting = list(options_map.keys())[selected]
                        new_value = options_map[setting][active_choice]
                        current[setting] = new_value
                        changed = True
                        editing = False
                        active_setting = None
                    else:
                        editing = True
                        active_setting = list(options_map.keys())[selected]
                        active_choice = options_map[active_setting].index(current[active_setting])
                elif key == curses.KEY_DOWN and editing:
                    active_choice = (active_choice + 1) % len(options_map[active_setting])
                elif key == curses.KEY_UP and editing:
                    active_choice = (active_choice - 1) % len(options_map[active_setting])
                elif key == 27: # ESC
                    if not editing: 
                        exit()

        curses.wrapper(menu_logic)

        return current
    
    """ Terminal UI including full integrated menu framework """
    
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
                else:
                    return None  
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

    @staticmethod 
    def _draw_menu(lines):
        for line in lines: 
            Terminal.write(line)


    @staticmethod 
    def launch_menu(title, options : dict, current=None, selection_types=None, buffer=10, colorcode=True):
        """ Currently supports '1D' or '2D' options, as in menu of options, when selected, another menu of options if 2D """

        header = f"{Terminal.get_color_bold("Diablo", "diablo red")} {Terminal.get_color_bold("Settings", "star")}\n{Terminal.line}"
        Terminal.write(header)
        instruction = f"{Terminal.get_color("[Esc] Exit without saving", "star")} | [←] Save | [Enter] Edit | [↑][↓] Change"

        """ Initialize canvas of menu """
        types = {}
        possible_types = {"dropdown", "text", "list", "list-int", "dropdown-text", "dropdown-int"}
        original = {}
        options_size_1d = len(options)
        total_canv_size = options_size_1d
        lines = []
        idx = 0 
        for key, val in options.items():
            """ Selection_types are defaulted to dropdown, even if one is called, 
                if the key is not present it defaults to dropdown"""
            key = str(key)
            if not selection_types:
                types[key] = "dropdown"
            else:
                if key in selection_types:
                    specified_type = selection_types[key]
                    if not specified_type in possible_types:
                        Terminal.error(f"Developor Error: Your specified input type is not supported, the supported types are {possible_types}") 
                        return 
                    types[key] = selection_types[key]
                else:
                    types[key] = "dropdown"
            
            """ Fill original layout of menu if specified """
            if isinstance(val, list):
                if current:
                    original[key] = current[key]
                else:
                    original[key] = str(val[0])
                dist_to_bottom = (idx + 1) + (len(val) - 1)
                if dist_to_bottom > total_canv_size:
                    total_canv_size = dist_to_bottom
            else: 
                if current:
                    original[key] = current[key]
                else: 
                    original[key] = str(val)
            
            """ Initalize lines stored in menu """
            left = f"{key.replace('_', ' ').capitalize():<25}"
            left = Terminal.get_bold(left)

            if isinstance(original[key], list):
                right = ", ".join(original[key])
            else:
                right = str(original[key])

            if colorcode: 
                if right == "yes" or right == "True":
                    right = Terminal.get_color(right, "green")
                elif right == "no" or right == "False":
                    right = Terminal.get_color(right, "red")

            lines.append(f"{left} : {right}")

            idx+=1
        
        for s in range(0, buffer):
            lines.append(" ")
        total_canv_size += buffer 

        lines.append(instruction)
        total_canv_size = len(lines)

        Terminal._draw_menu(lines)



        
        











        




