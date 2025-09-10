import sys 
from datetime import datetime
import textwrap
from .logo import logo_ansi

class Terminal: 

    preset = {
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "light blue": (26, 247, 253),
        "light yellow": (255, 238, 140),
        "diablo red": (255, 25, 7),
        "star": (255, 213, 0)
    }

    barrier = "________________________________________________________ _________________ __________ _______ ___ __ _"
    greeting = textwrap.dedent('''
        An open-source LAN protection & VPN service.                                                                                            
        Spot any bugs or vulnerabilities, or want to become a collaborator? Email neelov12@gmail.com.                                           
        (Github: github.com/Neelov12/Diablo).                                                                                                   
    ''')

    @staticmethod
    def _findansi(msg, rgb):
        r, g, b = rgb
        ansi = "" 
        for c in msg:
            ansi+= f"\x1b[38;2;{r};{g};{b}m{c}\x1b[0m"
        return ansi
    
    @staticmethod 
    def return_ansi(msg, color=None, rgb=None):
        if not color and not rgb:
            return Terminal._findansi(msg, Terminal.preset["white"])
        if color: 
            return Terminal._findansi(msg, Terminal.preset[color])
        elif rgb: 
            return Terminal._findansi(msg, rgb)   
        
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
        line = f"[+] {msg}"
        print(Terminal._findansi(line, Terminal.preset["red"]))

    @staticmethod
    def success(msg):
        line = f"[+] Success: {msg}"
        print(Terminal._findansi(line, Terminal.preset["green"]))

    @staticmethod
    def print_intro():
        msg = f"\n{Terminal.barrier}{Terminal.greeting}{Terminal.barrier}\n"
        print(logo_ansi)
        #print(msg)
        




