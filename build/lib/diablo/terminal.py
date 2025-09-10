import sys 
from datetime import datetime

class Terminal: 

    preset = {
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "light blue": (26, 247, 253),
        "light yellow": (255, 238, 140)
    }
    
    @staticmethod
    def _findansi(msg, rgb):
        r, g, b = rgb
        ansi = "" 
        for c in msg:
            ansi+= f"\x1b[38;2;{r};{g};{b}m{c}\x1b[0m"

        return ansi
    
    @staticmethod
    def write(msg, color=None, rgb=None):
        if not color and not rgb:
            print(msg)
            return
        if color: 
            print(Terminal._findansi(msg, Terminal.colors[color]))
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





