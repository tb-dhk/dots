from habits import Habit

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
            case "new list":
                display = "enter the list name"
            case ["edit list name", *_]:
                display = "enter the list name"
            case [("new list item" | "edit list item"), *_]:
                display = "enter the item name"
            case "new log":
                display = "enter the log name"
            case ["edit log name", *_]:
                display = "enter the log name"
            case [("new log entry" | "edit log entry"), *_]:
                display = "enter the entry name"
            case _:
                display = str(message)
    display = display.lower()
    if display:
        if display[-1] not in ".!?":
            display += "."
    window.addstr(window.getmaxyx()[0] - 1, 0, display[:window.getmaxyx()[1] - 1])
    window.refresh()
