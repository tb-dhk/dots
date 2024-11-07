import curses
import re
from datetime import datetime as dt, date, timedelta
import calendar
import sys
import os
import toml

from tasks import *
from points import points
from habits import *
from misc import *

config = toml.load(os.path.join(os.path.expanduser("~"), ".dots", "config.toml"))

def check_date(string):
    try:
        dt.strptime(string, "%Y-%m-%d")
    except:
        return False
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
    task_id = task_list[selected[0] - 2]  # Task to edit
    task_name = Task.get_task(task_id)['name']

    if text_box.isdigit():
        new_parent_index = int(text_box)
        if 0 <= new_parent_index < len(task_list) and new_parent_index != selected[0] - 2:
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
    options = ["tasks", "habits", "lists", "journals"]
    stdscr.addstr(0, 0, " " * stdscr.getmaxyx()[1], curses.color_pair(2 + 4 * (selected[0] == 0)))
    stdscr.move(0, 0)
    for i, option in enumerate(options):
        stdscr.addstr(f" {option} ", curses.color_pair(1 + int(i != outer_option) + 4 * (selected[0] == 0)))

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
        stdscr.addstr(f" {option} ", curses.color_pair(1 + (i != inner_option) + 4 * (selected[0] == 1)))

def content(window, outer_option, inner_option, selected, text_input, text_mode, text_box, text_index, removing, day, map_settings, new_habit):
    if outer_option == 0:
        if inner_option == 0:
            display_tasks(window, selected, text_input, text_mode, text_box, text_index, removing)
        elif inner_option == 1:
            day_view(window, selected, day, text_input, text_box, text_index, removing)
        elif inner_option == 2:
            week_view(window, selected, day, text_input, text_box, text_index, removing)
        elif inner_option == 3:
            month_view(window, selected, day, text_input, text_box, text_index, removing)
        elif inner_option == 4:
            year_view(window, selected, day, text_input, text_box, text_index, removing)
    elif outer_option == 1:
        if inner_option == 0:
            duration_maps(window, selected, map_settings)
        elif inner_option == 1:
            progress_maps(window, selected, map_settings)
        elif inner_option == 2:
            heatmaps(window, selected, map_settings)
        elif inner_option == 3:
            manage_habits(window, selected, removing)
        elif inner_option == 4:
            add_new_habit(window, selected, new_habit)
    else:
        coming_soon(window)
    display_text_box(window, text_input, text_box, text_index)
    window.refresh()

def status_bar(window, text_input, text_mode, message):
    window.addstr(window.getmaxyx()[0] - 1, 0, " " * (window.getmaxyx()[1] - 1))
    if message or not text_input and not text_mode:
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
                display = "enter the number to the right of the task you would like to set as the new parent (-1 for no parent)"
            case "choose date":
                display = "enter the date in the format yyyy-mm-dd"
            case "habit name":
                display = "enter new habit name"
            case "habit unit":
                display = "enter habit unit (to provide singular and plural forms, separate with /)"
            case "habit target value":
                display = "enter target value for habit"
            case ["new duration record", selected_day, selected_habit, habits]:
                display = f"enter start and end for habit '{habits[selected_habit]['name']}' on {selected_day}, in format yyyy-mm-dd-hh:mm,yyyy-mm-dd-hh:mm"
            case ["new progress record", selected_day, selected_habit, habits] | ["new frequency record", selected_day, selected_habit, habits]:
                display = f"enter value for habit '{habits[selected_habit]['name']}' on {selected_day}"
            case ["add date", selected_habit]:
                display = "enter the date in the format yyyy-mm-dd"
            case ["edit habit", selected_habit, selected_header]:
                if selected_header in ["unit", "target value"]:
                    display = f"enter new {selected_header} for habit '{Habit.load_habits()[selected_habit]['name']}'"
                else:
                    display = f"enter new unit for habit '{Habit.load_habits()[selected_habit]['name']}' (to provide singular and plural forms, separate with /)"
            case _:
                display = str(message)
    window.addstr(window.getmaxyx()[0] - 1, 0, display[:window.getmaxyx()[1] - 1])
    window.refresh()

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
        curses.init_pair(3, 69, curses.COLOR_BLACK)  # colored dots
        curses.init_pair(4, 20, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, 20)
        curses.init_pair(6, 20, curses.COLOR_WHITE)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)

    # Initial states
    height, width = stdscr.getmaxyx()
    started = "-n" in sys.argv or "--no-home-screen" in sys.argv
    selected = [0, -1]
    outer_option = inner_option = 0
    text_input = False
    text_mode = ""
    text_box = ""
    text_index = 0
    message = ""
    removing = ""
    day = date.today().strftime("%Y-%m-%d")
    map_settings = {"based_on": 0, "index": 0, "index2": 0}
    new_habit = {"name": " ", "type": "progress", "unit": "", "target_value": 0}

    # Create a window for content
    content_height = height - 3  # Adjust based on your layout
    content_width = width
    content_window = curses.newwin(content_height, content_width, 2, 0)  # Starting from row 2

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

        curses.init_color(69, *special_color)

        # Draw screen
        if not started:
            for x in range(width):
                for y in range(height):
                    if (x - width // 2 + 26, y - height // 2 + 6) in points:
                        stdscr.addch(y, x, "•", curses.color_pair(3))
                    else:
                        try:
                            stdscr.addch(y, x, "•", curses.color_pair(4))
                        except:
                            pass #stdscr.insstr(y, x-1, "•", curses.color_pair(4))
            center_string(stdscr, " press SPACE to start ", 1, offset=(0, 10))
        else:
            outer_navbar(stdscr, outer_option, selected)
            inner_navbar(stdscr, outer_option, inner_option, selected)
            content(content_window, outer_option, inner_option, selected, text_input, text_mode, text_box, text_index, removing, day, map_settings, new_habit)
            status_bar(stdscr, text_input, text_mode, message)

        # fetch all habits, and add a log for today (unless type == duration)
        habits = Habit.load_habits()
        for habit_id in habits:
            habit = habits[habit_id]
            today = date.today().strftime("%Y-%m-%d")
            if habit["type"] == "progress":
                if today not in habit["data"]:
                    ProgressHabit.add_progress_record(habit_id, today, 0)
            elif habit["type"] == "frequency":
                if today not in habit["data"]:
                    FrequencyHabit.add_occurrence_record(habit_id, today, 0)

        # Non-blocking check for key input
        key = stdscr.getch()
        if key != -1:  # -1 means no key was pressed
            if removing:
                if key == ord("r"):
                    if outer_option == 0 and inner_option == 0:
                        parent = Task.get_task(removing)["parent"]
                        if parent:
                            Task.edit_task(parent, subtasks=list(set(Task.get_task(parent)["subtasks"]) - {removing}))
                        for subtask in Task.get_task(removing)["subtasks"]:
                            Task.remove_task(subtask)
                        Task.remove_task(removing)
                        removing = ""
                        content_window.clear()
                    elif outer_option == 1 and inner_option == 3:
                        Habit.remove_habit(removing)
                        removing = ""
                        content_window.clear()
                elif chr(key) in "123456789":
                    if outer_option == 1 and inner_option == 0:
                        if map_settings["based_on"] == 0:
                            habits = Habit.load_habits()
                            habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}
                            habit = list(habits.keys())[map_settings["index"]]
                            for_day = (date.today() + timedelta(days=map_settings["index"])).strftime("%Y-%m-%d")
                            records = {habit: [record for record in habits[habit]['data'] if record[0][:10] == for_day] for habit in habits}
                            record = records[habit][int(chr(key)) - 1]
                        else:
                            habits = Habit.load_habits()
                            habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}
                            habit = list(habits.keys())[map_settings["index"] % len(habits)]
                            for_day = list(get_records_from_habits(habits, map_settings["index"]).keys())[selected[0] - 4]
                            records = get_records_from_habits(habits, map_settings["index"])
                            record = records[for_day][int(chr(key)) - 1]
                        DurationHabit.remove_duration_record(habit, for_day, record)
                        removing = ""
                        content_window.clear()
                elif key == 27:
                    removing = ""
                    content_window.clear()
                elif key == ord("q"):
                    break
            elif text_input:
                if key == curses.KEY_BACKSPACE:
                    text_box = text_box[:text_index - 1] + text_box[text_index:]
                    text_index = max(0, text_index - 1)
                elif key == 27:  # ESC key
                    text_input = False
                    text_box = ""
                    text_mode = ""
                    if outer_option == 0 and inner_option == 0:
                        selected[1] = -1
                elif key == 13:  # Enter key
                    clear = True
                    if selected[0] >= 2:
                        task_id = ""
                        if outer_option == 0:
                            if inner_option == 0:
                                try:
                                    task_id = get_task_list()[selected[0] - 2]
                                except:
                                    task_id = ""
                            elif inner_option == 1:
                                task_id = tasks_for_day(day)[selected[0] - 3]["id"]
                            elif inner_option == 2:
                                task_id = tasks_for_week(day)[selected[0] - 3]["id"]
                            elif inner_option == 3:
                                task_id = tasks_for_month(day)[selected[0] - 3]["id"]
                            elif inner_option == 4:
                                task_id = tasks_for_year(day)[selected[0] - 3]["id"]
                        if task_id:
                            task_name = Task.get_task(task_id)["name"]
                        else:
                            task_name = ""
                        text_box = text_box.strip()
                        if text_box:
                            match text_mode:
                                case "new task":
                                    if inner_option < 2:
                                        Task.add_task(text_box)
                                    elif inner_option == 2:
                                        Task.add_task(text_box, due_date=(dt.strptime(day, "%Y-%m-%d") + timedelta(days=(5 - dt.strptime(day, "%Y-%m-%d").weekday()))).strftime("%Y-%m-%d"))
                                    elif inner_option == 3:
                                        Task.add_task(text_box, due_date=f"{day[:7]}-{calendar.monthrange(int(day[:4]), int(day[5:7]))[1]}", due_type="month")
                                    elif inner_option == 4:
                                        Task.add_task(text_box, due_date=f"{day[:4]}-12-31", due_type="year")
                                    message = f"new task '{text_box}' added"
                                case "edit task":
                                    Task.edit_task(task_id, name=text_box)
                                    message = f"name of task '{task_name}' changed to '{text_box}'"
                                case "migrate" | "schedule":
                                    if text_box and re.match(r"\d{4}-\d{2}-\d{2}", text_box) and check_date(text_box):
                                        move_day = text_box
                                    elif text_box and re.match(r"\d{4}-\d{2}", text_box) and int(text_box[-2:]) <= 12 and int(text_box[-2:]) >= 1:
                                        move_day = f"{text_box}-{calendar.monthrange(int(text_box[:4]), int(text_box[-2:]))[1]}"
                                    elif text_box and re.match(r"\d{4}", text_box):
                                        move_day = f"{text_box}-12-31"
                                    elif not text_box:
                                        move_day = ""
                                    else:
                                        move_day = ""

                                    task_due_date = dt.strptime(move_day, "%Y-%m-%d")
                                    try:
                                        parent_due_date = dt.strptime(Task.get_task(Task.get_task(task_id)["parent"])["due_date"], "%Y-%m-%d")
                                    except:
                                        parent_due_date = task_due_date

                                    if move_day and task_due_date <= parent_due_date:
                                        Task.edit_task(task_id, due_date=move_day)
                                        Task.edit_task(task_id, date_history=Task.get_task(task_id)["date_history"] + [(date.today().strftime("%Y-%m-%d"), move_day)])
                                        message = f"task '{task_name}' scheduled for {move_day}"
                                    elif not move_day:
                                        if not text_box:
                                            Task.edit_task(task_id, due_date=None)
                                            message = f"task '{task_name}' unscheduled"
                                        else:
                                            message = "invalid date format. try again!"
                                            clear = False
                                    else:
                                        message = f"task due date cannot be later than parent's ({Task.get_task(Task.get_task(task_id)['parent'])['due_date']}). try again!"
                                        clear = False
                                case "edit priority":
                                    if text_box in ["1", "2", "3"]:
                                        Task.edit_task(task_id, priority=int(text_box))
                                        message = f"priority of task '{task_name}' changed to {text_box}"
                                    else:
                                        message = "invalid priority. try again!"
                                        clear = False
                                case "edit tags":
                                    original_tags = list(set(Task.load_tasks()[get_task_list()[selected[0] - 2]]["tags"]))
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
                                        Task.edit_task(task_id, tags=new_tags)
                                    else:
                                        message = "invalid tag operation. try again!"
                                        clear = False
                                case "edit parent":
                                    message = edit_task_parent(selected, text_box, get_task_list())
                                case "choose date":
                                    if text_box and re.match(r"\d{4}-\d{2}-\d{2}", text_box) and check_date(text_box):
                                        day = text_box
                                        message = f"moved to date {text_box}"
                                    elif text_box and re.match(r"\d{4}-\d{2}", text_box) and int(text_box[-2:]) <= 12 and int(text_box[-2:]) >= 1:
                                        day = f"{text_box}-{calendar.monthrange(int(text_box[:4]), int(text_box[-2:]))[1]}"
                                        message = f"moved to month {text_box}"
                                    elif text_box and re.match(r"\d{4}", text_box) and check_date(text_box):
                                        day = f"{text_box}-12-31"
                                        message = f"moved to year {text_box}"
                                    else:
                                        message = "invalid date format. try again!"
                                        clear = False
                                case "habit name":
                                    new_habit["name"] = text_box
                                    message = f"habit name set to '{text_box}'"
                                case "habit unit":
                                    new_habit["unit"] = text_box
                                    message = f"habit unit set to '{text_box}'"
                                case "habit target value":
                                    try:
                                        new_habit["target_value"] = int(text_box)
                                    except: 
                                        message = "invalid target value. try again!"
                                        clear = False
                                    else:
                                        message = "habit target value updated"
                                case ["new duration record", selected_day, selected_habit, habits]:
                                    try:
                                        start, end = text_box.split(",")[:2]
                                        dt.strptime(start, "%Y-%m-%d-%H:%M")
                                        dt.strptime(end, "%Y-%m-%d-%H:%M") 
                                    except:
                                        message = "invalid time format. try again!"
                                        clear = False
                                    else:
                                        DurationHabit.add_duration_record(selected_habit, selected_day, [[start, end]])
                                        message = f"new duration record for habit '{habits[selected_habit]['name']}' on {selected_day} added"
                                case ["new progress record", selected_day, selected_habit, habits]:
                                    if not text_box.isdigit():
                                        message = "invalid value. try again!"
                                        clear = False
                                    elif int(text_box) < 0 or int(text_box) > habits[selected_habit]["target_value"]:
                                        message = f"value must be between 0 and {habits[selected_habit]['target_value']}. try again!"
                                        clear = False
                                    else:
                                        ProgressHabit.add_progress_record(selected_habit, selected_day, int(text_box))
                                        message = f"new progress record for habit '{habits[selected_habit]['name']}' on {selected_day} added"
                                case ["new frequency record", selected_day, selected_habit, habits]:
                                    if not text_box.isdigit():
                                        message = "invalid value. try again!"
                                        clear = False
                                    elif int(text_box) < 0:
                                        message = "value must be greater than 0. try again!"
                                        clear = False
                                    else:
                                        FrequencyHabit.add_occurrence_record(selected_habit, selected_day, int(text_box))
                                        message = f"new frequency record for habit '{habits[selected_habit]['name']}' on {selected_day} added"
                                case ["add date", selected_habit]:
                                    if text_box and re.match(r"\d{4}-\d{2}-\d{2}", text_box) and check_date(text_box):
                                        ProgressHabit.add_progress_record(selected_habit, text_box, 0)
                                    else:
                                        message = "invalid date format. try again!"
                                        clear = False
                                case ["edit habit", selected_habit, selected_header]:
                                    if selected_header in ["name", "unit"]:
                                        valid = True
                                    else:
                                        if text_box.isdigit():
                                            valid = int(text_box) >= 0
                                            text_box = int(text_box)
                                        else:
                                            valid = False
                                    if valid:
                                        Habit.edit_habit(selected_habit, **{selected_header: text_box})
                                        message = f"habit {selected_header} changed to '{text_box}'"
                                    else:
                                        message = f"invalid {selected_header}. try again!"
                            if clear:
                                text_input = False
                                text_box = ""
                                text_mode = ""
                                if outer_option == 0 and inner_option == 0:
                                    selected[1] = -1
                    content_window.clear()
                elif key == curses.KEY_LEFT:
                    text_index = max(0, text_index - 1)
                elif key == curses.KEY_RIGHT:
                    text_index = min(len(text_box), text_index + 1)
                elif key == curses.KEY_DOWN:
                    text_index = len(text_box)
                elif key == curses.KEY_UP:
                    text_index = 0
                else:
                    if chr(key) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+-=[]{}|;':,.<>/? ":
                        text_box = text_box[:text_index] + chr(key) + text_box[text_index:]
                        text_index = min(len(text_box), text_index + 1)
            elif key == curses.KEY_UP:
                content_window.clear()
                selected[0] -= 1
                if selected[0] == -1:
                    if outer_option == 0:
                        if inner_option == 0:
                            selected[0] = 2 + len(get_task_list())
                        elif inner_option == 1:
                            selected[0] = len(tasks_for_day(day)) + 2
                        elif inner_option == 2:
                            selected[0] = len(tasks_for_week(day)) + 2
                        elif inner_option == 3:
                            selected[0] = len(tasks_for_month(day)) + 2
                        elif inner_option == 4:
                            selected[0] = len(tasks_for_year(day)) + 2
                    elif outer_option == 1:
                        if inner_option < 2:
                            habits = Habit.load_habits()
                            if habits:
                                if map_settings["based_on"] == 0: 
                                    habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}
                                    selected[0] = 3 + len(habits)
                                else:
                                    habit = list(habits.keys())[map_settings["index"] % len(habits)]
                                    selected[0] = 4 + len(habits[habit]["data"])
                        elif inner_option == 2:
                            habits = Habit.load_habits()
                            selected[0] = 4 + (len(habits) if map_settings["based_on"] != 4 else 7)
                        elif inner_option == 3:
                            selected[0] = 2 + len(Habit.load_habits())
                        elif inner_option == 4:
                            selected[0] = 6
                else:
                    if selected[0] == -1:
                        selected[0] = 2
            elif key == curses.KEY_DOWN:
                content_window.clear()
                selected[0] += 1
                if outer_option == 0:
                    if inner_option == 0:
                        if selected[0] == 3 + len(get_task_list()):
                            selected[0] = 0
                    elif inner_option == 1:
                        if selected[0] == len(tasks_for_day(day)) + 3:
                            selected[0] = 0
                    elif inner_option == 2:
                        if selected[0] == len(tasks_for_week(day)) + 3:
                            selected[0] = 0
                    elif inner_option == 3:
                        if selected[0] == len(tasks_for_month(day)) + 3:
                            selected[0] = 0
                    elif inner_option == 4:
                        if selected[0] == len(tasks_for_year(day)) + 3:
                            selected[0] = 0
                elif outer_option == 1:
                    if inner_option < 2:
                        habits = Habit.load_habits()
                        if habits:
                            if map_settings["based_on"] == 0:
                                habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}
                                if selected[0] == 4 + len(habits):
                                    selected[0] = 0
                            else:
                                habit = list(habits.keys())[map_settings["index"] % len(habits)]
                                if selected[0] == 5 + len(habits[habit]["data"]):
                                    selected[0] = 0
                    elif inner_option == 2:
                        habits = Habit.load_habits()
                        if selected[0] == 5 + (len(habits) if map_settings["based_on"] != 4 else 7):
                            selected[0] = 0
                    elif inner_option == 3:
                        if selected[0] == 2 + len(Habit.load_habits()):
                            selected[0] = 0
                    elif inner_option == 4:
                        if selected[0] == 7:
                            selected[0] = 0
                else:
                    if selected[0] == 3:
                        selected[0] = 0
            elif key == curses.KEY_END:
                if outer_option == 0:
                    if inner_option == 0:
                        selected[0] = 2 + len(get_task_list())
                else:
                    selected[0] = 3
            elif key == curses.KEY_LEFT:
                if selected[0] == 0:
                    outer_option -= 1
                    if outer_option == -1:
                        outer_option = 3
                    inner_option = 0
                elif selected[0] == 1:
                    inner_option -= 1
                    if inner_option == -1:
                        inner_option = len(inner_options(outer_option)) - 1
                    map_settings["index"] = 0
                    map_settings["index2"] = 0
                elif outer_option == 0:
                    if selected[0] == 2:
                        if inner_option == 1:
                            day = (dt.strptime(day, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                        elif inner_option == 2:
                            day = (dt.strptime(day, "%Y-%m-%d") - timedelta(weeks=1)).strftime("%Y-%m-%d")
                        elif inner_option == 3:
                            day = (dt.strptime(day, "%Y-%m-%d") - timedelta(days=calendar.monthrange(int(day[:4]), int(day[5:7]))[1])).strftime("%Y-%m-%d")
                        elif inner_option == 4:
                            day = (dt.strptime(day, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
                    else:
                        selected[1] -= 1
                        if selected[1] == -1:
                            selected[1] = len(config["tasks"]["day"]["details"]) - 1
                elif outer_option == 1:
                    if inner_option < 2:
                        habits = Habit.load_habits()
                        habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}
                        if selected[0] == 2:
                            map_settings["based_on"] -= 1 
                        elif selected[0] == 3:
                            map_settings["index"] -= 1
                    elif inner_option == 2:
                        if selected[0] == 2:
                            if habits:
                                map_settings["based_on"] -= 1
                            else:
                                map_settings["based_on"] = 0
                        elif selected[0] == 3:
                            map_settings["index"] -= 1
                        elif selected[0] == 4:
                            if inner_option != 2:
                                map_settings["index2"] = max(map_settings["index2"] - 1, map_settings["index"])
                            else:
                                map_settings["index2"] -= 1
                        elif selected[0] > 4:
                            selected[1] -= 1
                    elif inner_option == 3:
                        selected[1] -= 1
                    elif inner_option == 4: 
                        if selected[0] == 3:
                            types = ["progress", "duration", "frequency"]
                            new_habit["type"] = types[(types.index(new_habit["type"]) - 1) % 3]
                            if new_habit["type"] == "duration":
                                new_habit["unit"] = "hours"
                            elif new_habit["unit"] == "hours" and new_habit["type"] != "duration":
                                new_habit["unit"] = ""
                        elif selected[0] == 5:
                            new_habit["target_value"] -= 1
                            if new_habit["target_value"] < 0:
                                new_habit["target_value"] = 0
                if selected[0] < 2:
                    if outer_option == 0:
                        if inner_option == 0:
                            selected[1] = -1
                        elif inner_option in [1, 2]:
                            selected[1] = 0
            elif key == curses.KEY_RIGHT:
                if selected[0] == 0:
                    outer_option += 1
                    if outer_option == 4:
                        outer_option = 0
                    inner_option = 0
                elif selected[0] == 1:
                    inner_option += 1
                    if inner_option == len(inner_options(outer_option)):
                        inner_option = 0
                    map_settings["index"] = 0
                    map_settings["index2"] = 0
                elif outer_option == 0:
                    if selected[0] == 2:
                        if inner_option == 1:
                            day = (dt.strptime(day, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
                        elif inner_option == 2:
                            day = (dt.strptime(day, "%Y-%m-%d") + timedelta(weeks=1)).strftime("%Y-%m-%d")
                        elif inner_option == 3:
                            day = (dt.strptime(day, "%Y-%m-%d") + timedelta(days=calendar.monthrange(int(day[:4]), int(day[5:7]))[1])).strftime("%Y-%m-%d")
                        elif inner_option == 4:
                            day = (dt.strptime(day, "%Y-%m-%d") + timedelta(days=365)).strftime("%Y-%m-%d")
                    else:
                        selected[1] += 1
                        if selected[1] == len(config["tasks"]["day"]["details"]):
                            selected[1] = 0
                elif outer_option == 1:
                    if inner_option < 2:
                        habits = Habit.load_habits()
                        habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}
                        if selected[0] == 2:
                            if habits:
                                map_settings["based_on"] += 1
                            else:
                                map_settings["based_on"] = 0
                        elif selected[0] == 3:
                            map_settings["index"] += 1
                    elif inner_option == 2:
                        if selected[0] == 2:
                            map_settings["based_on"] += 1
                        elif selected[0] == 3:
                            if inner_option != 2:
                                map_settings["index"] = min(map_settings["index"] + 1, map_settings["index2"])
                            else:
                                map_settings["index"] += 1
                        elif selected[0] == 4:
                            map_settings["index2"] += 1
                        elif selected[0] > 4:
                            selected[1] += 1
                    elif inner_option == 3:
                        selected[1] += 1
                    elif inner_option == 4:
                        if selected[0] == 3:
                            types = ["progress", "duration", "frequency"]
                            new_habit["type"] = types[(types.index(new_habit["type"]) + 1) % 3]
                            if new_habit["type"] == "duration":
                                new_habit["unit"] = "hours"
                            elif new_habit["unit"] == "hours" and new_habit["type"] != "duration":
                                new_habit["unit"] = ""
                        elif selected[0] == 5:
                            new_habit["target_value"] += 1
                if selected[0] < 2:
                    if outer_option == 0:
                        if inner_option == 0:
                            selected[1] = -1
                        else:
                            selected[1] = 0
                    else:
                        selected[1] = 0
            elif chr(key) == "q" or key == 27:
                break
            elif not started:
                match chr(key):
                    case " ":
                        started = True
                        stdscr.clear()
            elif selected[0] >= 2:
                if outer_option == 0:
                    if inner_option == 0:
                        try:
                            task = get_task_list()[selected[0] - 2]
                        except:
                            if key == ord(":"):
                                text_input = True
                                text_mode = "edit task"
                        else:
                            task_name = Task.get_task(task)["name"]
                            text_modes = {
                                ":": "new task",
                                "n": "edit task",
                                ">": "migrate",
                                "<": "schedule",
                                "t": "edit tags",
                                "m": "edit parent",
                            }
                            if chr(key) in text_modes:
                                text_input = True
                                text_mode = text_modes[chr(key)]
                            if chr(key) in "xn.123><tmr":
                                content_window.clear()
                            match chr(key):
                                case "x":
                                    Task.edit_task(task, completed=not Task.get_task(str(task))["completed"])
                                case "n":
                                    selected[1] = 0
                                case ".":
                                    Task.edit_task(task, due_date=date.today().strftime("%Y-%m-%d"))
                                    message = f"task '{task_name}' scheduled for today"
                                case "1" | "2" | "3":
                                    Task.edit_task(task, priority=int(chr(key)))
                                case ">":
                                    selected[1] = 2
                                case "<":
                                    selected[1] = 2
                                case "t":
                                    selected[1] = 5
                                case "m":
                                    selected[1] = 3
                                case "r":
                                    removing = task
                                    content_window.clear()
                    elif inner_option in [1, 2, 3, 4]:
                        task = [tasks_for_day, tasks_for_week, tasks_for_month, tasks_for_year][inner_option - 1](day)[selected[0] - 3]
                        task_name = task["name"]
                        match chr(key):
                            case "v":
                                outer_option = 0
                                inner_option = 0
                                selected[0] = 2 + get_task_list().index(task["id"])
                                selected[1] = -1
                                content_window.clear()
                            case "e":
                                text_input = True
                                content_window.clear()
                                try:
                                    due_date = task["due_date"].strftime("%Y-%m-%d")
                                except:
                                    passed = False
                                else:
                                    passed = due_date < date.today().strftime("%Y-%m-%d")
                                match config["tasks"]["day"]["details"][selected[1]]:
                                    case "name":
                                        text_mode = "edit task"
                                    case "due_date":
                                        text_mode = "migrate" if passed else "schedule"
                                    case "priority":
                                        text_mode = "edit priority"
                                    case "tags":
                                        text_mode = "edit tags"
                                    case _:
                                        text_input = False
                            case ":":
                                text_input = True
                                text_mode = "edit task"
                            case "x":
                                Task.edit_task(task["id"], completed=not task["completed"])
                                content_window.clear()
                            case "1" | "2" | "3":
                                Task.edit_task(task["id"], priority=int(chr(key)))
                                content_window.clear()
                            case "d":
                                if selected[0] == 2:
                                    text_input = True
                                    text_mode = "choose date"
                            case ".":
                                Task.edit_task(task, due_date=date.today().strftime("%Y-%m-%d"))
                                message = f"task '{task_name}' scheduled for today"
                            case "r":
                                removing = task["id"]
                                content_window.clear()
                elif outer_option == 1:
                    habits = Habit.load_habits()
                    habits = dict(sorted(habits.items(), key=lambda x: x[0]))
                    if inner_option < 2:
                        index = map_settings["index"]
                        if inner_option == 0:
                            allowed_types = ["duration"]
                        elif inner_option == 1:
                            if map_settings["based_on"] == 1:
                                allowed_types = ["frequency", "progress"]
                            else:
                                allowed_types = ["progress"]
                        habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] in allowed_types}
                        habits = dict(sorted(habits.items(), key=lambda x: x[0]))
                        if selected[0] >= 4:
                            if chr(key) == "e":
                                if inner_option == 0:
                                    if map_settings["based_on"] == 0:
                                        selected_day = (date.today() + timedelta(days=index)).strftime("%Y-%m-%d")
                                        selected_habit = list(habits.keys())[selected[0] - 4]
                                    else:
                                        selected_habit = list(habits.keys())[index % len(habits)]
                                        daylist = list(get_records_from_habits(habits, index).keys())
                                        selected_day = daylist[selected[0] - 4]
                                else:
                                    if map_settings["based_on"] == 0:
                                        selected_day = (date.today() + timedelta(days=index)).strftime("%Y-%m-%d")
                                        selected_habit = list(habits.keys())[selected[0] - 4] 
                                    else:
                                        selected_habit = list(habits.keys())[index % len(habits)]
                                        daylist = list(sorted(habits[selected_habit]["data"].keys()))
                                        selected_day = daylist[selected[0] - 4]
                                text_input = True
                                mode = f"new {habits[selected_habit]['type']} record"
                                text_mode = [mode, selected_day, selected_habit, habits]
                            elif chr(key) == ":" and map_settings["based_on"] == 1 and inner_option == 1:
                                text_input = True
                                text_mode = ["add date", list(habits.keys())[index % len(habits)]]
                            elif chr(key) == "r" and inner_option == 0:
                                if map_settings["based_on"] == 0:
                                    removing = list(habits.keys())[selected[0] - 4]
                                else:
                                    selected_habit = list(habits.keys())[index % len(habits)]
                                    daylist = list(get_records_from_habits(habits, index).keys())
                                    removing = daylist[selected[0] - 4]
                                content_window.clear()
                    elif inner_option == 2:
                        if selected[0] >= 5:
                            if chr(key) == "e":
                                if map_settings["based_on"] == 0:
                                    based_on, index, index2 = "day", map_settings["index"], map_settings["index2"]
                                    start_day, end_day = get_bounds(based_on, index, index2)
                                    selected_habit = list(habits.keys())[selected[0] - 5]
                                    selected_day = get_dates(start_day, end_day, based_on, index, index2)[selected[1]].strftime("%Y-%m-%d")[:10]
                                    text_input = True
                                    text_mode = [f"new {habits[selected_habit]['type']} record", selected_day, selected_habit, habits]
                                else:
                                    selected_habit = list(habits.keys())[map_settings["index2"] % len(habits)]
                                    this_year = date.today().year
                                    start_day = get_sunday(f"{this_year}-01-01")
                                    selected_day = dt.strptime(start_day, "%Y-%m-%d") + timedelta(weeks=selected[1]) + timedelta(days=selected[0] - 5)
                                    selected_day = selected_day.strftime("%Y-%m-%d")
                                    if selected_day[:4] == str(this_year):
                                        text_input = True
                                        text_mode = [f"new {habits[selected_habit]['type']} record", selected_day, selected_habit, habits]
                    elif inner_option == 3:
                        if chr(key) == "e":
                            headers = ["name", "type", "unit", "target_value"]
                            selected_header = headers[selected[1] % len(headers)]
                            if selected_header != "type":
                                text_input = True
                                text_mode = ["edit habit", list(habits.keys())[selected[0] - 2], selected_header.replace("_", " ")] 
                        elif chr(key) == "r":
                            removing = list(habits.keys())[selected[0] - 2]
                            content_window.clear()
                    elif inner_option == 4:
                        text_modes = {
                            2: "habit name",
                            4: "habit unit",
                            5: "habit target value",
                        }
                        if selected[0] in text_modes and chr(key) == "e" and not (selected[0] == 4 and new_habit["type"] == "duration") and not (selected[0] == 5 and new_habit["type"] == "frequency"):
                            text_input = True
                            text_mode = text_modes[selected[0]]
                        elif selected[0] == 6 and key == 13:
                            Habit.add_habit(new_habit["name"], new_habit["type"], new_habit["unit"], target_value=new_habit["target_value"])
                            message = f"new habit '{new_habit['name']}' added"
                            new_habit = {"name": " ", "type": "progress", "unit": " ", "target_value": 0}
            else:
                pass

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
