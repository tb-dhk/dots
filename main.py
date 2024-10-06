import curses
import re
import time
import datetime
from content import Task, display_task_details, display_tasks
from points import points

def traverse_tasks(task_key, tasks, clean_list):
    """Recursively traverse through the task and its subtasks, adding them to the clean list."""
    clean_list.append(task_key)  # Add the parent task key

    # Get the subtasks (children) of the current task
    try:
        for subtask_key in tasks[task_key]['subtasks']:
            traverse_tasks(subtask_key, tasks, clean_list)  # Recursively add subtasks
    except:
        pass

def get_task_list():
    """Return a clean list of tasks and their subtasks in a structured order."""
    tasks = Task.load_tasks()  # Load all tasks
    clean_list = []

    # Find tasks without parents (root tasks)
    for task_key in tasks:
        if not tasks[task_key]['parent']:
            traverse_tasks(task_key, tasks, clean_list)

    return clean_list

def check_date(string):
    try: 
        datetime.datetime.strptime(string, "%Y-%m-%d")
    except:
        return False
    else:
        return True

def center_string(window, string, color_pair, offset=(0, 0)):
    height, width = window.getmaxyx()
    x = width // 2 - len(string) // 2 + offset[0]
    y = height // 2 + offset[1]
    window.addstr(y, x, string, curses.color_pair(color_pair))

def change_task_parent(task_id, new_parent_id):
    """Change the parent of a task and update subtasks of both old and new parents."""
    tasks = Task.load_tasks()
    task = tasks[task_id]

    # If removing the parent (new_parent_id is None)
    if new_parent_id is None:
        # Remove the task from its current parent's subtasks
        for parent_id in tasks:
            if task_id in tasks[parent_id]["subtasks"]:
                Task.edit_task(parent_id, subtasks=list(set(tasks[parent_id]["subtasks"]) - {task_id}))
        Task.edit_task(task_id, parent=None)
    else:
        new_parent = tasks[new_parent_id]

        # Remove the task from its old parent if it had one
        if task["parent"]:
            for parent_id in tasks:
                if task_id in tasks[parent_id]["subtasks"]:
                    Task.edit_task(parent_id, subtasks=list(set(tasks[parent_id]["subtasks"]) - {task_id}))

        # Set the new parent and update its subtasks
        Task.edit_task(task_id, parent=new_parent_id)
        Task.edit_task(new_parent_id, subtasks=list(set(new_parent["subtasks"] + [task_id])))

def edit_task_parent(selected, text_box, task_list):
    """Process the input to edit the parent of the selected task."""
    task_id = task_list[selected - 2]  # Task to edit
    task_name = Task.get_task(task_id)['name']

    if text_box.isdigit():
        new_parent_index = int(text_box)
        if 0 <= new_parent_index < len(task_list) and new_parent_index != selected - 2:
            new_parent_id = task_list[new_parent_index]
            change_task_parent(task_id, new_parent_id)
            message = f"Parent of task '{task_name}' changed to '{Task.get_task(new_parent_id)['name']}'"
        else:
            message = "Invalid parent. Please try again!"
    elif text_box == "-1":
        # Remove the parent if text_box == "-1"
        change_task_parent(task_id, None)
        message = f"Parent of task '{task_name}' removed"
    else:
        message = "Invalid input. Please try again!"

    return message

def outer_navbar(stdscr, outer_option, selected):
    options = ["tasks", "lists", "trackers", "journals"]
    stdscr.addstr(0, 0, " " * stdscr.getmaxyx()[1], curses.color_pair(2 + 4 * (selected == 0)))
    stdscr.move(0, 0)
    for i, option in enumerate(options):
        stdscr.addstr(f" {option} ", curses.color_pair(1 + int(i != outer_option) + 4 * (selected == 0)))

def inner_options(outer_option):
    if outer_option == 0:
        return ["list", "day", "week", "month", "year"]
    elif outer_option == 4:
        return ["main"]
    else:
        return ["new"]

def inner_navbar(stdscr, outer_option, inner_option, selected):
    stdscr.addstr(1, 0, " " * stdscr.getmaxyx()[1], curses.color_pair(2 + 4 * (selected == 1)))
    stdscr.move(1, 0)
    options = inner_options(outer_option)
    for i, option in enumerate(options):
        stdscr.addstr(f" {option} ", curses.color_pair(1 + (i != inner_option) + 4 * (selected == 1)))

def content(window, outer_option, inner_option, selected, text_input, text_mode, text_box, removing):
    if outer_option == 0:
        display_tasks(window, inner_option, selected, text_input, text_mode, text_box, removing)
        if selected >= 2:
            display_task_details(window, get_task_list()[selected - 2], window.getmaxyx()[1] // 2 - 1 if selected >= 2 else None)
    window.refresh()

def status_bar(stdscr, outer_option, inner_option, selected, text_mode, message):
    match text_mode:
        case "new task" | "edit task":
            display = "enter new task name"
        case "migrating":
            display = "enter due date to migrate to in the format yyyy-mm-dd"
        case "scheduling":
            display = "enter due date to schedule for in the format yyyy-mm-dd"
        case "edit priority":
            display = "enter a number from 1 (low) to 3 (high)"
        case "edit tags":
            display = "enter + to add or - to remove, followed by tags (comma-separated)"
        case "edit parent":
            display = "enter the number to the right of the task you would like to set as the new parent (-1 for no parent)"
        case _:
            display = str(message)
    stdscr.addstr(stdscr.getmaxyx()[0] - 1, 0, display)  # Placeholder for future status bar implementation

def main(stdscr):
    # Screen setup
    stdscr.clear()
    stdscr.nodelay(1)
    stdscr.keypad(1)
    curses.curs_set(0)  # Hide cursor
    curses.nonl()

    # Color configuration
    special_color = [1000, 0, 0]
    if curses.has_colors():
        curses.start_color()
        curses.init_color(curses.COLOR_BLACK, 0, 0, 0)
        curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
        curses.init_color(curses.COLOR_RED, 1000, 0, 0)
        curses.init_color(20, 500, 500, 500)
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Navbar colors
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, 100, curses.COLOR_BLACK)  # colored dots
        curses.init_pair(4, 20, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, 20)
        curses.init_pair(6, 20, curses.COLOR_WHITE)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)

    # Initial states
    height, width = stdscr.getmaxyx()
    started = False
    outer_option = inner_option = selected = 0
    text_input = False
    text_mode = ""
    text_box = ""
    message = ""
    removing = "" 

    # Create a window for content
    content_height = height - 3  # Adjust based on your layout
    content_width = width
    content_window = curses.newwin(content_height, content_width, 2, 0)  # Starting from row 2

    # Initial screen design (before starting)
    for x in range(width):
        for y in range(height):
            try:
                stdscr.addch(y, x, "•", curses.color_pair(4))
            except:
                stdscr.insstr(y, x - 1, "•", curses.color_pair(4))

    while True:
        # Update special color
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

        curses.init_color(100, *special_color)

        # Draw screen
        if not started:
            for x in range(width):
                for y in range(height):
                    if (x - width / 2 + 26, y - height / 2 + 6) in points:
                        stdscr.addch(y, x, "•", curses.color_pair(3))
            center_string(stdscr, " press SPACE to start ", 1, offset=(0, 10))
        else:
            outer_navbar(stdscr, outer_option, selected)
            inner_navbar(stdscr, outer_option, inner_option, selected)
            content(content_window, outer_option, inner_option, selected, text_input, text_mode, text_box, removing)
            status_bar(stdscr, outer_option, inner_option, selected, text_mode, message)

        # Non-blocking check for key input
        key = stdscr.getch()
        if key != -1:  # -1 means no key was pressed
            if started:
                stdscr.clear()
            if removing:
                if key == ord("r"):
                    parent = Task.get_task(removing)["parent"]
                    if parent:
                        Task.edit_task(parent, subtasks=list(set(Task.get_task(parent)["subtasks"]) - {removing}))
                    for subtask in Task.get_task(removing)["subtasks"]:
                        Task.remove_task(subtask)
                    Task.remove_task(removing)
                    removing = ""
                    content_window.clear()
                elif key == 27:
                    removing = ""
                elif key == ord("q"):
                    break
            elif text_input:
                if key == curses.KEY_BACKSPACE:
                    text_box = text_box[:-1]
                elif key == 27:  # ESC key
                    text_input = False
                    text_box = ""
                    text_mode = ""
                elif key == 13:  # Enter key
                    if outer_option == 0 and inner_option == 0 and selected >= 2:
                        clear = True
                        task_name = Task.load_tasks()[get_task_list()[selected - 2]]["name"] if selected >= 2 else None
                        text_box = text_box.strip()
                        if text_box:
                            if text_mode == "new task":
                                Task.add_task(text_box)
                                message = f"new task '{text_box}' added"
                            elif text_mode == "edit task":
                                Task.edit_task(get_task_list()[selected - 2], name=text_box)
                                message = f"name of task '{task_name}' changed to '{text_box}'"
                            elif text_mode in ["migrate", "schedule"]:
                                if text_box and re.match(r"\d{4}-\d{2}-\d{2}", text_box) and check_date(text_box):
                                    Task.edit_task(get_task_list()[selected - 2], due_date=text_box)
                                    message = f"task '{task_name}' scheduled for {text_box}"
                                else:
                                    message = "invalid date format. try again!"
                                    clear = False
                            elif text_mode == "edit priority":
                                if text_box in ["1", "2", "3"]:
                                    Task.edit_task(get_task_list()[selected - 2], priority=int(text_box))
                                    message = f"priority of task '{task_name}' changed to {text_box}"
                                else:
                                    message = "invalid priority. try again!"
                                    clear = False
                            elif text_mode == "edit tags":
                                original_tags = list(set(Task.load_tasks()[get_task_list()[selected - 2]]["tags"]))
                                if text_box[0] in ["+", "-"]:
                                    tags = [tag.strip() for tag in text_box[1:].split(",")]
                                    if text_box[0] == "+":
                                        new_tags = list(set(original_tags + tags))
                                        message = f"tags {', '.join(tags)} added to task '{task_name}'"
                                    else:
                                        existing_tags = [i for i in tags if i in original_tags]
                                        non_existing_tags = [i for i in tags if i not in original_tags]
                                        new_tags = [i for i in original_tags if i not in tags]
                                        message = f"tags {', '.join(existing_tags)} removed from task '{task_name}' (tags {', '.join(non_existing_tags)} not found)"
                                    Task.edit_task(get_task_list()[selected - 2], tags=new_tags)
                                else:
                                    message = "invalid tag operation. try again!"
                                    clear = False
                            elif text_mode == "edit parent":
                                message = edit_task_parent(selected, text_box, get_task_list())
                  
                        if clear:
                            text_input = False
                            text_box = ""
                            text_mode = ""
                    content_window.clear()
                else:
                    text_box += chr(key)
            elif key == curses.KEY_DOWN:
                content_window.clear()
                selected += 1
                if outer_option == 0:
                    if inner_option == 0:
                        if selected == 2 + len(get_task_list()):
                            selected = 0
                else:
                    if selected == 3:
                        selected = 0
            elif key == curses.KEY_UP:
                content_window.clear()
                selected -= 1
                if selected == -1:
                    selected = 2
            elif key == curses.KEY_END:
                if outer_option == 0:
                    if inner_option == 0:
                        selected = 2 + len(get_task_list())
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
            elif chr(key) == "q":
                break
            elif not started:
                match chr(key):
                    case " ":
                        started = True
                        stdscr.clear()
            elif outer_option == 0 and inner_option == 0 and selected >= 2:
                task = get_task_list()[selected - 2]
                task_name = Task.get_task(task)["name"] 
                match chr(key):
                    case ":":
                        text_input = True
                        text_mode = "new task"
                    case "x":
                        Task.edit_task(task, completed=not Task.get_task(str(task))["completed"])
                    case "n":
                        text_input = True
                        text_mode = "edit task"
                    case ".":
                        Task.edit_task(task, due_date=datetime.date.today().strftime("%Y-%m-%d"))
                        message = f"task '{task_name}' scheduled for today"
                    case "p":
                        text_input = True
                        text_mode = "edit priority"
                    case ">":
                        text_input = True
                        text_mode = "migrate"
                    case "<":
                        text_input = True
                        text_mode = "schedule"
                    case "t":
                        text_input = True
                        text_mode = "edit tags"
                    case "m":
                        text_input = True
                        text_mode = "edit parent"
                    case "r":
                        removing = task
                        content_window.clear()
            else:
                pass

        stdscr.refresh()
        time.sleep(0.001)  # Optional delay for CPU usage control

if __name__ == "__main__":
    curses.wrapper(main)

