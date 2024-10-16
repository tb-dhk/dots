import curses

def display_borders(window, selected, split=False, task_list=[]):
    """Draw the border for the task list. If selected[0] >= 2, split the window in half."""
    max_y, max_x = window.getmaxyx()

    if selected[0] >= 2 and selected[0] < len(task_list) + 2 and split:
        split_x = max_x // 2 - 1
        # Left box border
        window.addstr(0, 0, "╔" + "═" * (split_x - 2) + "╗" + " ")
        for y in range(1, max_y - 3):
            window.addstr(y, 0, "║", curses.color_pair(1))
            window.addstr(y, split_x - 1, "║", curses.color_pair(1))
        window.addstr(max_y - 4, 0, "╚" + "═" * (split_x - 2) + "╝" + " ")

        # Right box border
        window.addstr(0, split_x + 1, "╔" + "═" * (max_x - split_x - 3) + "╗")
        for y in range(1, max_y - 3):
            window.addstr(y, split_x + 1, "║", curses.color_pair(1))
            window.addstr(y, max_x - 1, "║", curses.color_pair(1))
        window.addstr(max_y - 4, split_x + 1, "╚" + "═" * (max_x - split_x - 3) + "╝")
    else:
        # Single full-width box
        window.addstr(0, 0, "╔" + "═" * (max_x - 2) + "╗")
        for y in range(1, max_y - 3):
            window.addstr(y, 0, "║" + " " * (max_x - 2) + "║", curses.color_pair(1))
        window.addstr(max_y - 4, 0, "╚" + "═" * (max_x - 2) + "╝")

    # Single full-width box
    window.addstr(max_y - 3, 0, "╔" + "═" * (max_x - 2) + "╗")
    window.addstr(max_y - 2, 0, "║" + " " * (max_x - 2) + "║", curses.color_pair(1))
    window.addstr(max_y - 1, 0, "╚" + "═" * (max_x - 3) + "╝")
    window.insstr(max_y - 1, 1, "═")

def display_text_box(window, text_input, text_box, text_index):
    """Display the input text box at the bottom of the screen."""
    max_y, max_x = window.getmaxyx()
    if text_input:
        window.addstr(max_y - 2, 2, text_box, curses.color_pair(1))
        window.chgat(max_y - 2, 2 + text_index, 1, curses.color_pair(2))
        window.addstr(max_y - 2, len(text_box) + 3, " " * (max_x - len(text_box) - 6), curses.color_pair(1))
    else:
        window.addstr(max_y - 2, len(text_box) + 2, " ", curses.color_pair(1))
