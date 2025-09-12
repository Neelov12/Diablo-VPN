import sys 
from datetime import datetime
import textwrap
import time
import threading
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

    line = "______________________________________ _____________ _________ _______ ___ __ _"
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
    def sectionheader(title, color="star"):
        title_ansi = Terminal._findansi(title, Terminal.preset[color])
        print(f"{title_ansi}\n{Terminal.line}")

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
        





        




