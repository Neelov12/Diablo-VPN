
# Change this to any RGB you want:
rgb = (255, 25, 7)  # (R, G, B)
yellow = (255, 213, 0)

# Input/output files:
in_path = "./canvas.txt"
out_path = "./logo"
intro_path = "../diablo/assets/banner.txt"

# Build ANSI sequences
r, g, b = rgb
ANSI_FG = f"\x1b[38;2;{r};{g};{b}m"  # 24-bit (truecolor) foreground
r, g, b = yellow
ANSI_STAR = f"\x1b[38;2;{r};{g};{b}m"  # 24-bit (truecolor) foreground
ANSI_WHITE = f"\x1b[38;2;255;255;255m"
ANSI_RESET = "\x1b[0m"

def main():
    colored = "" 
    # 1) Read plain text
    with open(in_path, "r", encoding="utf-8") as f:
        plain = f.read()
        lines = plain.splitlines() 
        starlen = 0
        s = 0
        iswhite = False 
        isyellow = False
        for l in lines: 
            # Manage command 
            if l.startswith("!"):
                # Manage start of star 
                if l.startswith("!star"):
                    command = l.split()
                    starlen = int(command[1])
                    s = 0
                    continue
                elif l.startswith("!end"):
                    command = l.split()
                    if len(command) == 1:
                        break
                    else:
                        if command[1] == "white":
                            iswhite = False 
                        if command[1] == "yellow":
                            isyellow = False 
                        continue
                elif l.startswith("!white"):
                    iswhite = True
                    continue
                elif l.startswith("!yellow"):
                    isyellow = True
                    continue
            
            CURR_ANSI = ANSI_FG
            # If current line is a star 
            if starlen != 0:
                if s >= starlen:
                    starlen = 0 
                    s = 0
                else:
                    CURR_ANSI = ANSI_STAR
                    s+=1 
            if iswhite: 
                CURR_ANSI = ANSI_WHITE
            elif isyellow:
                CURR_ANSI = ANSI_STAR
                
            for c in l: 
                if starlen != 0 and s == starlen:
                    if c == '_' or c == ' ':
                        colored+= f"{ANSI_FG}{c}{ANSI_RESET}"
                        continue 

                colored+= f"{CURR_ANSI}{c}{ANSI_RESET}"

            colored+= f"{CURR_ANSI}\n{ANSI_RESET}"

    with open(out_path, "w") as f:
        f.write(colored)
    
    with open(intro_path, "w") as intro: 
        intro.write(colored)

    # Print the contents (shows colored text in a compatible terminal)
    with open(out_path, "r") as f:
        raw_logo = f.read()
        print(raw_logo, end="")

"""
    escaped_logo = raw_logo.encode('unicode_escape').decode('utf-8')
    
    with open("../diablo/logo.py", "w") as logo:
        logo.write(f'logo_ansi = "{escaped_logo}"\n')
"""

if __name__ == "__main__":
    main()