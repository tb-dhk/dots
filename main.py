import curses
import time

from content import Task, tasks
from points import points

def center_string(stdscr, string, color_pair, offset=(0, 0)):
    height, width = stdscr.getmaxyx()
    x = width // 2 - len(string) // 2 + offset[0]
    y = height // 2 + offset[1]
    stdscr.addstr(y, x, string, curses.color_pair(color_pair))

def outer_navbar(stdscr, outer_option, selected):
    options = ["tasks", "lists", "trackers", "journals"]
    stdscr.addstr(0, 0, " " * stdscr.getmaxyx()[1], curses.color_pair(2 + 4 * (selected == 0)))
    stdscr.move(0, 0)
    for x in range(len(options)):
        stdscr.addstr(" " + options[x] + " ", curses.color_pair(1 + int(x != outer_option) + 4 * (selected == 0)))

def inner_options(outer_option):
    if outer_option:
        options = ["new"]
    elif outer_option == 4:
        options = ["main"]
    else:
        options = ["list", "day", "week", "month", "year"]
    return options

def inner_navbar(stdscr, outer_option, inner_option, selected):
    stdscr.addstr(1, 0, " " * stdscr.getmaxyx()[1], curses.color_pair(2 + 4 * (selected == 1)))
    stdscr.move(1, 0)
    options = inner_options(outer_option)
    for x in range(len(options)):
        stdscr.addstr(" " + options[x] + " ", curses.color_pair(1 + (x != inner_option) + 4 * (selected == 1)))

def content(stdscr, outer_option, inner_option, selected, tasks_vertical, text_input, text_box):
    match outer_option:
        case 0:
            tasks(stdscr, inner_option, selected, tasks_vertical, text_input, text_box)
    return

def status_bar(stdscr):
    return

def main(stdscr):
    # Clear screen
    stdscr.clear()
    stdscr.nodelay(1)
    stdscr.keypad(1)

    # Turn off the cursor
    curses.curs_set(0)
    curses.nonl()

    special_color = [1000, 0, 0]

    # Set up color pairs (if terminal supports color)
    if curses.has_colors():
        curses.start_color()

        curses.init_color(curses.COLOR_BLACK, 0, 0, 0)
        curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
        curses.init_color(20, 500, 500, 500)

        # Define color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Navbar colors
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, 100, curses.COLOR_BLACK)  # colored dots
        curses.init_pair(4, 20, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, 20)
        curses.init_pair(6, 20, curses.COLOR_WHITE)

    # Get screen dimensions
    height, width = stdscr.getmaxyx()

    started = False

    outer_option = inner_option = selected = 0

    text_input = False
    text_mode = []
    text_box = ""

    tasks_vertical = []

    for x in range(width):
        for y in range(height):
            try:
                stdscr.addch(y, x, "•", curses.color_pair(4))
            except:
                stdscr.insstr(y, x-1, "•", curses.color_pair(4))

    while True:
        # Update the special color based on conditions
        base_value = 500
        color_offset = 100 
        if special_color[0] == 1000:
            if special_color[2] > base_value:
                special_color[2] -= color_offset
            elif special_color[1] < 1000:
                special_color[1] += color_offset
            else:
                special_color[0] -= color_offset
        elif special_color[1] == 1000:
            if special_color[0] > base_value:
                special_color[0] -= color_offset
            elif special_color[2] < 1000:
                special_color[2] += color_offset
            else:
                special_color[1] -= color_offset
        elif special_color[2] == 1000:
            if special_color[1] > base_value:
                special_color[1] -= color_offset
            elif special_color[0] < 1000:
                special_color[0] += color_offset
            else:
                special_color[2] -= color_offset

        # Update the color in curses
        curses.init_color(100, *special_color)  # Update the custom color

        # Draw points
        if not started:
            for x in range(width):
                for y in range(height):
                    if (x - width / 2 + 26, y - height / 2 + 6) in points:
                        stdscr.addch(y, x, "•", curses.color_pair(3))
            center_string(stdscr, " press SPACE to start ", 1, offset=(0, 10))
        else:
            outer_navbar(stdscr, outer_option, selected)
            inner_navbar(stdscr, outer_option, inner_option, selected)
            content(stdscr, outer_option, inner_option, selected, tasks_vertical, text_input, text_box)
            status_bar(stdscr)

        # Non-blocking check for key input
        key = stdscr.getch()
        if key != -1:  # -1 means no key was pressed
            if key == curses.KEY_DOWN:
                selected += 1
                if outer_option == 0:
                    if inner_option == 0:
                        if selected == 2 + len(Task.load_tasks()):
                            selected = 0
                else:
                    if selected == 3:
                        selected = 0
            elif key == curses.KEY_UP:
                selected -= 1
                if selected == -1:
                    selected = 2
            elif key == curses.KEY_END:
                if outer_option == 0:
                    if inner_option == 0:
                        selected = 2
                else:
                    selected = 3
            elif key == curses.KEY_LEFT:
                if selected == 0:
                    outer_option -= 1
                    if outer_option == -1:
                        outer_option = 3
                    inner_option = 0
                elif selected == 1:
                    inner_option -= 1
                    if inner_option == -1:
                        inner_option = len(inner_options(outer_option)) - 1
            elif key == curses.KEY_RIGHT:
                if selected == 0:
                    outer_option += 1
                    if outer_option == 4:
                        outer_option = 0
                    inner_option = 0
                elif selected == 1:
                    inner_option += 1
                    if inner_option == len(inner_options(outer_option)):
                        inner_option = 0
            elif text_input:
                if key == curses.KEY_BACKSPACE:
                    text_box = text_box[:-1]
                elif key == 27:
                    text_input = False
                elif key == 13:
                    if outer_option == 0:
                        if inner_option == 0:
                            if text_mode == "new task":
                                Task.add_task(text_box)
                                text_box = ""
                else:
                    text_box += chr(key)
            elif chr(key) == "q":
                break
            elif not started:
                match chr(key):
                    case " ":
                        started = True
                        stdscr.clear()
            elif outer_option == 0:
                if inner_option == 0 and selected >= 2:
                    task = tasks_vertical[selected - 2]
                    match chr(key):
                        case ":":
                            text_input = True
                            text_mode = "new task"
                        case "x":
                            Task.edit_task(task, completed=not Task.load_tasks()[str(task)]["completed"])
                        case ">":
                            text_input = True
                            text_mode = "migrating"
                        case "<":
                            text_input = True
                            text_mode = "scheduling"
            else:
                pass

        stdscr.refresh()
        time.sleep(0.001)  # Optional delay for CPU usage control

if __name__ == "__main__":
    curses.wrapper(main)

