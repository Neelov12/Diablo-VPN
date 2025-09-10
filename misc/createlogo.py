
# Change this to any RGB you want:
rgb = (40, 255, 0)  # (R, G, B)

# Input/output files:
in_path = "logo.txt"
out_path = "./logo"

# Build ANSI sequences
r, g, b = rgb
ANSI_FG = f"\x1b[38;2;{r};{g};{b}m"  # 24-bit (truecolor) foreground
ANSI_RESET = "\x1b[0m"
print(f"{ANSI_FG}c{ANSI_RESET}")
def main():
    colored = "" 
    # 1) Read plain text
    with open(in_path, "r", encoding="utf-8") as f:
        plain = f.read()
        lines = plain.splitlines() 
        for l in lines: 
            for c in l: 
                colored+= f"{ANSI_FG}{c}{ANSI_RESET}"
            colored+= f"{ANSI_FG}\n{ANSI_RESET}"

    with open(out_path, "w") as f:
        f.write(colored)

    # Print the contents (shows colored text in a compatible terminal)
    with open(out_path, "r") as f:
        print(f.read(), end="")

if __name__ == "__main__":
    main()