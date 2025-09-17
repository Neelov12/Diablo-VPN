import sys 
from datetime import datetime
import time
import threading
import termios
import tty
import select
import shutil 
import re
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
    _animation_frames = []
    _animation_lines = []
    _animation_states = []
    _animation_pause = 0.25

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
    def print(msg, color=None, rgb=None, color_bold=None, bold=False):
        if bold:
            print(Terminal._get_ansi_b(msg))
        elif color is not None: 
            print(Terminal._findansi(msg, Terminal.preset[color]))
        elif rgb is not None: 
            print(Terminal._findansi(msg, rgb))
        elif color_bold is not None:
            print(Terminal._get_ansi_cb(msg, Terminal.preset[color_bold]))
        else:
            print(msg)
        return
    
    @staticmethod
    def write(msg, color=None, rgb=None, color_bold=None, bold=False):
        if bold:
            sys.stdout.write(Terminal._get_ansi_b(msg))
        elif color is not None: 
            sys.stdout.write(Terminal._findansi(msg, Terminal.preset[color]))
        elif rgb is not None: 
            sys.stdout.write(Terminal._findansi(msg, rgb))
        elif color_bold is not None:
            sys.stdout.write(Terminal._get_ansi_cb(msg, Terminal.preset[color_bold]))
        else:
            sys.stdout.write(msg)
        return
    
    @staticmethod
    def write_at(row, col, msg):
        sys.stdout.write(f"\x1b[{row};{col}H{msg}\x1b[0m")

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
        print(Terminal._get_ansi_cb(f"[+] {msg}", Terminal.preset["green"]))

    @staticmethod
    def proceed(msg):
        filler = '.' if not msg.endswith('.') else ''
        print(Terminal._get_ansi_cb(f"[+] {msg}{filler} Proceeding.", Terminal.preset["light blue"]))

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
        Terminal.hide_cursor()
        for line in Terminal._animation_lines:
            Terminal.write(f"{line}\n")
        Terminal.move_cursor_up(len(Terminal._animation_lines)+1)
        Terminal.flush()

        while not Terminal._stop_animation.is_set():
            for state in states:
                if Terminal._stop_animation.is_set():
                    break
                Terminal.clear_line()
                Terminal.move_line_start()
                Terminal.write(state)
                Terminal.flush()
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
        Terminal._animation_lines = []
        Terminal._animation_states = []
        Terminal._animation_pause = 0.25
        Terminal.show_cursor()
        if Terminal._animation_thread is not None:
            Terminal._animation_thread.join()
        if final is not None:
            sys.stdout.write(f"\r{final}\n")
            sys.stdout.flush()
    
    @staticmethod
    def pause_animation():
        Terminal.move_down(1)
        Terminal._stop_animation.set()
        if Terminal._animation_thread is not None:
            Terminal._animation_thread.join()

    @staticmethod
    def resume_animation():
        Terminal.move_down(len(Terminal._animation_states))
        Terminal.start_animation(Terminal._animation_states, Terminal._animation_pause)

    @staticmethod
    def append_animation(line=""):
        Terminal.move_down(1)
        Terminal._stop_animation.set()
        if Terminal._animation_thread is not None:
            Terminal._animation_thread.join()
        Terminal._animation_lines.append(line)
        Terminal.start_animation(Terminal._animation_states, Terminal._animation_pause)

    @staticmethod
    def replace_animation(line=""):
        Terminal.move_down(1)
        Terminal._stop_animation.set()
        if Terminal._animation_thread is not None:
            Terminal._animation_thread.join()
        Terminal._animation_lines.pop()
        Terminal._animation_lines.append(line)
        Terminal.start_animation(Terminal._animation_states, Terminal._animation_pause)

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
    
    @staticmethod
    def loading_animation(msg="", marker_color="light blue"):
        states = ['[-]', '[/]', '[|]', '[\\]']
        for i, s in enumerate(states):
            colored_marker = Terminal.get_color_bold(s, marker_color)
            states[i] = f"{colored_marker} {msg}"
        Terminal._animation_states = states
        Terminal._animation_pause = 0.15
        Terminal.start_animation(Terminal._animation_states, pause=Terminal._animation_pause)  

    @staticmethod
    def append_loading_animation(msg="", marker_color="light blue", line=""):
        states = ['[-]', '[/]', '[|]', '[\\]']
        for i, s in enumerate(states):
            colored_marker = Terminal.get_color_bold(s, marker_color)
            states[i] = f"{colored_marker} {msg}"
        Terminal.append_animation(states, pause=0.15, line=line)

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

        try:
            response = input(prompt).strip()
        except KeyboardInterrupt:
            sys.exit(1)

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
    def read_key(timeout=0.1):
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
                    return ch1  
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None
    
    """ Terminal Screen Control using ANSI """
    @staticmethod
    def clear():
        sys.stdout.write("\x1b[2J")
    
    @staticmethod
    def clear_line():
        sys.stdout.write("\x1b[2K")

    @staticmethod
    def move_up(lines=1):
        for l in range(lines):
            Terminal.clear_line()
            sys.stdout.write(f"\x1b[F")
        Terminal.clear_line()

    @staticmethod
    def move_down(lines=1):
        for l in range(lines):
            Terminal.clear_line()
            sys.stdout.write(f"\x1b[E")
        Terminal.clear_line()

    @staticmethod
    def launch_terminal():
        sys.stdout.write("\x1b[?1049h")
    
    @staticmethod
    def close_terminal():
        sys.stdout.write("\x1b[?1049l")

    """ Cursor Controls """
    @staticmethod
    def get_cursor_position():
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()

        # Temporarily change terminal mode to raw
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            response = ''
            while True:
                ch = sys.stdin.read(1)
                response += ch
                if ch == 'R':
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        # Parse the response: ESC[row;colR
        match = re.match(r'\x1b\[(\d+);(\d+)R', response)
        if match:
            row, col = map(int, match.groups())
            return row, col
        else:
            return None, None

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
    def move_cursor_up(lines=1, exact=False):
        """ Allows cursor to be moved up at exact current column or at beginning of previous line"""
        if exact:
            sys.stdout.write(f"\x1b[{lines}A")
        else:
            sys.stdout.write(f"\x1b[{lines}F")
    
    @staticmethod
    def move_cursor_down(lines=1, exact=False):
        """ Allows cursor to be moved down at exact current column or at beginning of next line"""
        if exact:
            sys.stdout.write(f"\x1b[{lines}B")
        else:
            sys.stdout.write(f"\x1b[{lines}E")
    
    @staticmethod
    def move_line_start():
        Terminal.move_cursor_down()
        Terminal.move_cursor_up()
    



        
        











        




