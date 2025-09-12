# Determine a curses color code that you like

import curses

def color(stdscr):
    for i in range(0, 256):
        curses.curs_set(0)
        curses.start_color()
        #curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.use_default_colors()
        curses.init_pair(i, i, -1)
        stdscr.addstr(i, 1, str(i), curses.A_BOLD | curses.color_pair(i))

curses.wrapper(color)