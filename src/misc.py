import curses
from datetime import datetime as dt

from modules import Task, Habit

def display_borders(window, selected, split=False, task_list=[]):
    """
    Draw the border for the content window.
    If selected[0] >= 2, split the window in half.
    """

    max_y, max_x = window.getmaxyx()
    max_y -= 4

    if selected[0] >= 2 and selected[0] < len(task_list) + 2 and split:
        split_x = max_x // 2 - 1
        # Left box border
        window.addstr(0, 0, "╔" + "═" * (split_x - 2) + "╗" + " ")
        for y in range(1, max_y):
            window.addstr(y, 0, "║", curses.color_pair(1))
            window.addstr(y, split_x - 1, "║", curses.color_pair(1))
        window.addstr(max_y, 0, "╚" + "═" * (split_x - 2) + "╝" + " ")

        # Right box border
        window.addstr(0, split_x + 1, "╔" + "═" * (max_x - split_x - 3) + "╗")
        for y in range(1, max_y):
            window.addstr(y, split_x + 1, "║", curses.color_pair(1))
            window.addstr(y, max_x - 1, "║", curses.color_pair(1))
        window.addstr(max_y, split_x + 1, "╚" + "═" * (max_x - split_x - 3) + "╝")
    else:
        # Single full-width box
        window.addstr(0, 0, "╔" + "═" * (max_x - 2) + "╗")
        for y in range(1, max_y):
            window.addstr(y, 0, "║" + " " * (max_x - 2) + "║", curses.color_pair(1))
        window.addstr(max_y, 0, "╚" + "═" * (max_x - 2) + "╝")

def display_text_box(window, text_input, text_box, text_index):
    """Display the input text box at the bottom of the screen."""
    max_y, max_x = window.getmaxyx()

    window.addstr(max_y - 3, 0, "╔" + "═" * (max_x - 2) + "╗")
    window.addstr(max_y - 2, 0, "║" + " " * (max_x - 2) + "║", curses.color_pair(1))
    window.addstr(max_y - 1, 0, "╚" + "═" * (max_x - 3) + "╝")
    window.insstr(max_y - 1, 1, "═")

    if text_input:
        window.addstr(max_y - 2, 2, text_box, curses.color_pair(1))
        window.chgat(max_y - 2, 2 + text_index, 1, curses.color_pair(2))
        window.addstr(
            max_y - 2, len(text_box) + 3,
            " " * (max_x - len(text_box) - 6), curses.color_pair(1)
        )
    else:
        window.addstr(max_y - 2, len(text_box) + 2, " ", curses.color_pair(1))

def coming_soon(window):
    display_borders(window, [0, 0])
    window.addstr(2, 5, "coming soon...")

def status_bar(window, text_input, text_mode, message):
    window.addstr(window.getmaxyx()[0] - 1, 0, " " * (window.getmaxyx()[1] - 1))
    display = ""
    if (message or not text_input) and not text_mode:
        display = str(message)
    else:
        match text_mode:
            case "new task" | "edit task":
                display = "enter new task name"
            case "migrate":
                display = "enter due date to migrate to in the format yyyy-mm-dd"
            case "schedule":
                display = "enter due date to schedule for in the format yyyy-mm-dd"
            case "edit priority":
                display = "enter a number from 1 (low) to 3 (high)"
            case "edit tags":
                display = "enter + to add or - to remove, followed by tags (comma-separated)"
            case "edit parent":
                display = (
                    "enter the number to the right of the task"
                    + " you would like to set as the new parent (-1 for no parent)"
                )
            case "choose date":
                display = "enter the date in the format yyyy-mm-dd"
            case "habit name":
                display = "enter new habit name"
            case "habit unit":
                display = "enter habit unit (to provide singular and plural forms, separate with /)"
            case "habit target value":
                display = "enter target value for habit"
            case ["new duration record", selected_day, selected_habit, habits]:
                display = f"enter start and end for habit '{
                    habits[selected_habit]['name']
                }' on {selected_day}, in format yyyy-mm-dd-hh:mm,yyyy-mm-dd-hh:mm"
            case (
                ["new progress record", selected_day, selected_habit, habits]
                | ["new frequency record", selected_day, selected_habit, habits]
            ):
                display = f"enter value for habit '{
                    habits[selected_habit]['name']
                }' on {selected_day}"
            case ["add date", selected_habit]:
                display = "enter the date in the format yyyy-mm-dd"
            case ["edit habit", selected_habit, selected_header]:
                if selected_header in ["unit", "target value"]:
                    display = f"enter new {selected_header} for habit '{
                        Habit.load_habits()[selected_habit]['name']
                    }'"
                else:
                    display = f"enter new unit for habit '{
                        Habit.load_habits()[selected_habit]['name']
                    }' (to provide singular and plural forms, separate with /)"
            case _:
                display = str(message)
    display = display.lower()
    if display:
        if display[-1] not in ".!?":
            display += "."
    window.addstr(window.getmaxyx()[0] - 1, 0, display[:window.getmaxyx()[1] - 1])
    window.refresh()

def change_task_parent(task_id, new_parent_id):
    """Change the parent of a task and update subtasks of both old and new parents."""
    tasks = Task.load_tasks()
    task = tasks[task_id]

    # If removing the parent (new_parent_id is None)
    if new_parent_id is None:
        # Remove the task from its current parent's subtasks
        for parent_id in tasks:
            if task_id in tasks[parent_id]["subtasks"]:
                Task.edit_task(
                    parent_id, subtasks=list(set(tasks[parent_id]["subtasks"]) - {task_id})
                )
        Task.edit_task(task_id, parent=None)
    else:
        new_parent = tasks[new_parent_id]

        # Remove the task from its old parent if it had one
        if task["parent"]:
            for parent_id in tasks:
                if task_id in tasks[parent_id]["subtasks"]:
                    Task.edit_task(
                        parent_id, subtasks=list(set(tasks[parent_id]["subtasks"]) - {task_id})
                    )

        # Set the new parent and update its subtasks
        Task.edit_task(task_id, parent=new_parent_id)
        Task.edit_task(new_parent_id, subtasks=list(set(new_parent["subtasks"] + [task_id])))

def edit_task_parent(selected, text_box, task_list):
    """Process the input to edit the parent of the selected task."""
    task_id = task_list[selected[0] - 2]  # Task to edit
    task_name = Task.get_task(task_id)['name']

    if text_box.isdigit():
        new_parent_index = int(text_box)
        if 0 <= new_parent_index < len(task_list) and new_parent_index != selected[0] - 2:
            new_parent_id = task_list[new_parent_index]
            change_task_parent(task_id, new_parent_id)
            message = f"Parent of task '{task_name}' changed to '{
                Task.get_task(new_parent_id)['name']
            }'"
        else:
            message = "Invalid parent. Please try again!"
    elif text_box == "-1":
        # Remove the parent if text_box == "-1"
        change_task_parent(task_id, None)
        message = f"Parent of task '{task_name}' removed."
    else:
        message = "Invalid input. Please try again!"

    return message

def outer_navbar(stdscr, outer_option, selected):
    options = ["tasks", "habits", "lists", "log"]
    stdscr.addstr(0, 0, " " * stdscr.getmaxyx()[1], curses.color_pair(2 + 4 * (selected[0] == 0)))
    stdscr.move(0, 0)
    for i, option in enumerate(options):
        stdscr.addstr(
            f" {option} ",
            curses.color_pair(1 + int(i != outer_option) + 4 * (selected[0] == 0))
        )

def inner_options(outer_option):
    if outer_option == 0:
        return ["list", "day", "week", "month", "year"]
    if outer_option == 1:
        return ["duration", "progress", "heatmap", "manage", "+ new"]
    if outer_option == 4:
        return ["main"]
    return ["+ new"]

def inner_navbar(stdscr, outer_option, inner_option, selected):
    stdscr.addstr(1, 0, " " * stdscr.getmaxyx()[1], curses.color_pair(2 + 4 * (selected[0] == 1)))
    stdscr.move(1, 0)
    options = inner_options(outer_option)
    for i, option in enumerate(options):
        stdscr.addstr(
            f" {option} ",
            curses.color_pair(1 + (i != inner_option) + 4 * (selected[0] == 1))
        )

def change_color(special_color):
    base_value = 750
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

    return special_color

def init_colors():
    curses.start_color()
    curses.init_color(curses.COLOR_BLACK, 0, 0, 0)
    curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
    curses.init_color(curses.COLOR_RED, 1000, 0, 0)
    curses.init_color(20, 500, 500, 500)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Navbar colors
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, 69, curses.COLOR_BLACK)  # colored dots
    curses.init_pair(4, 20, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, 20)
    curses.init_pair(6, 20, curses.COLOR_WHITE)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)

def check_date(string):
    try:
        dt.strptime(string, "%Y-%m-%d")
    except:
        return False
    return True

def center_string(window, string, color_pair=0, offset=(0, 0)):
    height, width = window.getmaxyx()
    x = (width - len(string)) // 2 + offset[0]
    y = height // 2 + offset[1]
    window.addstr(y, x, string, curses.color_pair(color_pair))
