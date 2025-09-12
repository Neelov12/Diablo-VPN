import sys 
from datetime import datetime
import time
import threading
import json
import curses
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

    line = "____________________ _________ _______ ____ ___ __ _"
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
    def get_ansi(msg, color=None, rgb=None):
        if not color and not rgb:
            return Terminal._findansi(msg, Terminal.preset["white"])
        if color: 
            return Terminal._findansi(msg, Terminal.preset[color])
        elif rgb: 
            return Terminal._findansi(msg, rgb)   

    """ Standard Output Management & Helpers """    
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
    def prompt_response(name=None, options=[], yesno=False, yesnoenter=False, mercy=True):
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
        if yesno or yesnoenter: 
            if options: 
                Terminal.error("Don't call yesno and options together, just call yesno, prompt_response handles options for you")
                return
            options = ["yes", "no", "n", "y"]
            prompt = "(yes/no) >> "
            if yesnoenter: 
                """ yesnoenter takes precedence if yesno called as well """
                options.append("")
                prompt = "(y/n) or press Enter >> "

        response = input(prompt).strip()
        if options: 
            if not response in options: 
                valid = False       
            elif yesno or yesnoenter:
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
    def launch_menu(title, options, original):
        """ Launches terminal menu allowing user to navigate & select options using arrow keys and enter,
            takes as required arguments header (menu title), dictionary of options, and original options """
        header = Terminal.section_header(title, ret=True)
        options_map = options
        current = original.copy()
        code = 221
        header_size = 4
        changed = False

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
                        changed = True
                        break

        curses.wrapper(menu_logic)






        




