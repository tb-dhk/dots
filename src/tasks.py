import curses
import calendar
from datetime import datetime as dt, date, timedelta
import os
import toml

from modules import Task
from misc import display_borders

config = toml.load(os.path.join(os.path.expanduser("~"), ".dots", "config.toml"))

def all_subtasks_completed(task_key):
    """check if the task and all its subtasks are marked as completed."""
    task = Task.get_task(task_key)
    if not task.get('completed', False):  # check if the task itself is not completed
        return False

    # check recursively for all subtasks
    for subtask_key in task.get('subtasks', []):
        if not all_subtasks_completed(subtask_key):
            return False
    return True

def traverse_tasks(task_key, tasks, clean_list, hide_completed=False):
    """
    recursively traverse through the task and its subtasks, adding them to the clean list.
    if hide_completed is true, skip tasks where the task and all its subtasks are completed.
    """
    # skip the task if hide_completed is true and all subtasks are completed
    if hide_completed and tasks[task_key]["completed"]:
        return

    clean_list.append(task_key)  # add the parent task key

    # recursively add subtasks
    for subtask_key in tasks[task_key].get('subtasks', []):
        traverse_tasks(subtask_key, tasks, clean_list, hide_completed=hide_completed)

def get_task_list(hide_completed=False):
    """return a clean list of tasks and their subtasks in a structured order."""
    tasks = Task.load_tasks()  # load all tasks
    clean_list = []

    # find tasks without parents (root tasks)
    for task_key in tasks:
        if not tasks[task_key].get('parent'):
            traverse_tasks(task_key, tasks, clean_list, hide_completed=hide_completed)

    clean_list.sort(
        key=lambda x: (
            int(tasks[x]["completed"]),
            -dt.timestamp(dt.strptime(tasks[x]["due_date"], "%Y-%m-%d"))
        )
    )

    return clean_list

def check_migrated(history, to_date):
    """check if a task has been migrated."""
    for record in range(len(history)-1):
        if history[record][1] == history[record+1][0] and history[record][1] == to_date:
            return True
    return False

def tasks_for_day(day=None):
    """return tasks for a day."""
    if day is None:
        day = date.today().strftime("%Y-%m-%d")
    tasks = [
        task for _, task in Task.load_tasks().items() if (
            task['due_date'] == day
            or task['date_added'] == day
            or check_migrated(task['date_history'], day)
        )
    ]
    tasks.sort(key=lambda x: (
        int(x["completed"]),
        -dt.timestamp(dt.strptime(x["due_date"], "%Y-%m-%d"))
    ))
    return tasks

def tasks_for_days(start, end):
    """return tasks for several days."""
    tasks = []
    start = dt.strptime(start, "%Y-%m-%d")
    end = dt.strptime(end, "%Y-%m-%d")
    for day in range((end - start).days + 1):
        this_date = (start + timedelta(days=day)).strftime("%Y-%m-%d")
        for task in tasks_for_day(this_date):
            if task not in tasks:
                tasks.append(task)
    tasks.sort(key=lambda x: (
        int(x["completed"]),
        -dt.timestamp(dt.strptime(x["due_date"], "%Y-%m-%d"))
    ))
    return tasks

def tasks_for_week(day):
    """return tasks for a week."""
    start = (
        dt.strptime(day, "%Y-%m-%d") - timedelta(days=dt.strptime(day, "%Y-%m-%d").weekday()-1)
    ).strftime("%Y-%m-%d")
    end = (dt.strptime(start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
    tasks = tasks_for_days(start, end)
    return tasks

def tasks_for_month(day):
    """return tasks for a month."""
    start = dt.strptime(day, "%Y-%m-%d").replace(day=1).strftime("%Y-%m-%d")
    end = (dt.strptime(start, "%Y-%m-%d") + timedelta(days=31)).strftime("%Y-%m-%d")
    tasks = tasks_for_days(start, end)
    return tasks

def tasks_for_year(day):
    """return tasks for a year."""
    start = dt.strptime(day, "%Y-%m-%d").replace(month=1, day=1).strftime("%Y-%m-%d")
    end = dt.strptime(start, "%Y-%m-%d").replace(month=12, day=31).strftime("%Y-%m-%d")
    tasks = tasks_for_days(start, end)
    return tasks

def display_task(
    window,
    task_key, selected, task_list,
    text_mode,
    indent=0, split_x=0, box='wide',
    removing="", removing_subtask=False,
    hide_completed=False
):
    """display a task and its subtasks with indentation, adapted for two split boxes."""
    tasks = Task.load_tasks()
    task = tasks[str(task_key)]
    if not task:
        return  # skip if task not found

    if window.getyx()[0] <= window.getmaxyx()[0] - 7:
        task_number = get_task_list(hide_completed).index(task_key)

        # choose the starting column based on the box ('left' or 'right')
        start_col = 2 if box != 'right' else split_x + 3
        end_col = split_x - 13 if box == 'left' else window.getmaxyx()[1] - 13
        window.move(window.getyx()[0] + 1, start_col)
        completed = task['completed']
        symbol = '⨯' if completed else '•'
        important = "! " if task['priority'] == 3 else "  "

        if text_mode == "edit parent":
            number = len(task_list)
            window.addstr(
                window.getyx()[0], end_col - 1,
                f"({number})".rjust(12) if selected[0] != task_number + 2 else " " * 12
            )
        else:
            if task['due_type'] == "day":
                window.addstr(
                    window.getyx()[0], end_col - 1,
                    f"[{task['due_date'].ljust(10)}]", curses.color_pair(1)
                )
            elif task['due_type'] == "month":
                window.addstr(
                    window.getyx()[0], end_col - 1,
                    f"[{task['due_date'][:7].ljust(10)}]", curses.color_pair(1)
                )
            elif task['due_type'] == "year":
                window.addstr(
                    window.getyx()[0], end_col - 1,
                    f"[{task['due_date'][:4].ljust(10)}]", curses.color_pair(1)
                )
        window.move(window.getyx()[0], start_col)

        if task_number + 2 != selected[0] and task['completed']:
            task_color_pair = 4
        else:
            task_color_pair = 1 + 4 * (task_number + 2 == selected[0])

        window.addstr(important, curses.color_pair(8))

        if removing != task_key and not removing_subtask:
            window.addstr(f"{'  ' * indent}{symbol} ", curses.color_pair(task_color_pair))

            # wrap text if it exceeds the column width (end_col)
            task_name = task['name']
            available_width = end_col - window.getyx()[1] - 2  # account for space and '...'

            # check if truncation is needed
            if len(task_name) > available_width:
                truncated_name = task_name[:available_width - 3] + "..."  # truncate and add "..."
            else:
                truncated_name = task_name

            # print the truncated task name
            window.addstr(truncated_name, curses.color_pair(task_color_pair))

        else:
            window.addstr('  ' * indent)
            window.addstr(f"{symbol} ", curses.color_pair(7))
            window.addstr(
                "this subtask will be removed"
                if removing_subtask else "press r to confirm removal, esc to cancel",
                curses.color_pair(7)
            )

    task_list.append(task_key)
    for subtask_key in task['subtasks']:
        if not(tasks[subtask_key]["completed"] and hide_completed):
            display_task(
                window,
                subtask_key, selected, task_list,
                text_mode,
                indent + 1, split_x, box,
                removing, bool(removing == task_key),
                hide_completed=hide_completed
            )

def display_task_details(window, task_id, split_x, selected):
    """
    display the attributes of the selected task in the right box,
    with aligned colons and edit commands.
    """

    task = Task.load_tasks()[str(task_id)]
    if not task:
        return

    try:
        due_date = dt.strptime(task['due_date'], '%Y-%m-%d')
    except:
        passed = False
    else:
        passed = due_date.date() < dt.now().date()

    # define the edit commands for each task attribute
    edit_commands = {
        "name": "n",
        "completed": "x",
        "due date": "<" if passed else ">",
        "parent": "m",
        "priority": "p",
        "tags": "t",
        "recurrence": "c"
    }

    # define the task details with keys for alignment
    details = {
        "name": task['name'],
        "completed": 'yes' if task['completed'] else 'no ',
        "due date": task['due_date'],
        "parent": Task.load_tasks()[task['parent']]['name'] if task['parent'] else "none",
        "priority": ["low", "medium", "high"][int(task['priority']) - 1],
        "tags": ', '.join(task['tags']),
    }

    # calculate the maximum key length for proper alignment
    max_key_length = max(len(key) for key in details)
    max_width = window.getmaxyx()[1] - split_x - 7  # available space for wrapping

    # display each detail line with aligned colons and edit commands
    window.move(1, split_x + 3)
    count = 0
    for key, value in details.items():
        # construct the base line with key, edit command, and colon
        base_line = f"{key.ljust(max_key_length)} ({edit_commands[key]}) : "
        base_len = len(base_line)

        # split the value into lines if it exceeds the available width
        lines = []
        value_str = str(value)
        while len(value_str) > max_width - base_len:
            lines.append(value_str[:max_width - base_len].rstrip())
            value_str = value_str[max_width - base_len:].lstrip()
        lines.append(value_str)  # add the remaining part

        # display the first line with the base formatting
        window.addstr(base_line + lines[0], curses.color_pair(1 + (selected[1] == count)))
        window.move(window.getyx()[0] + 1, split_x + 3)

        # display any additional wrapped lines for the value
        for line in lines[1:]:
            window.addstr(" " * base_len + line, curses.color_pair(1 + (selected[1] == count)))
            window.move(window.getyx()[0] + 1, split_x + 3)

        # add extra spacing between each task detail
        window.move(window.getyx()[0] + 1, split_x + 3)
        count += 1

def display_tasks(window, selected, text_mode, removing, hide_completed):
    """main function to display tasks, with task details in the right box when selected."""
    max_x = window.getmaxyx()[1]
    display_borders(window, selected, split=True, task_list=get_task_list(hide_completed))
    tasks = Task.load_tasks()

    # group tasks by parent id
    tasks_by_parent = {}

    for task in tasks:
        parent_id = tasks[task]['parent']
        if parent_id and parent_id in list(tasks.keys()):
            tasks_by_parent.setdefault(parent_id, []).append(task)

    # filter tasks if hide_completed is true
    if hide_completed:
        tasks = {key: task for key, task in tasks.items()
                 if not task['completed'] or not all_subtasks_completed(task["id"])}

    tasks = dict(
                sorted(
                    tasks.items(),
                    key=lambda x: (
                        int(tasks[x[0]]["completed"]),
                        -dt.timestamp(dt.strptime(tasks[x[0]]["due_date"], "%Y-%m-%d"))
                    )
                )
            )

    split_x = max_x // 2 - 1 if selected[0] >= 2 else 0
    task_list = []

    if selected[0] >= 2 and selected[0] < len(get_task_list(hide_completed)) + 2:
        # display tasks in the left box
        window.move(0, 0)
        for task_key in tasks:
            if not tasks[task_key]['parent']:
                display_task(
                    window,
                    task_key, selected, task_list,
                    text_mode, split_x=split_x, box='left',
                    removing=removing, hide_completed=hide_completed
                )

        if window.getyx()[0] >= window.getmaxyx()[0] - 5:
            window.move(window.getmaxyx()[0] - 5, 4)
        else:
            window.move(window.getyx()[0] + 1, 4)

        new_task_msg = "+ press : to enter a new task"
        if len(new_task_msg) > split_x - 2:
            new_task_msg = new_task_msg[:split_x - 5] + "..."

        window.addstr(
            new_task_msg,
            curses.color_pair(
                4 + 1 * (selected[0] == len(get_task_list(hide_completed)) + 2)
            )
        )

        # find the selected task and display its details in the right box
        selected_task_key = task_list[selected[0] - 2]
        display_task_details(window, selected_task_key, split_x, selected)
    else:
        # single full-width box display
        window.move(0, 0)
        for task_key in tasks:
            if not tasks[task_key]['parent']:
                display_task(
                    window,
                    task_key, selected, task_list,
                    text_mode, hide_completed=hide_completed
                )

        if window.getyx()[0] >= window.getmaxyx()[0] - 5:
            window.move(window.getmaxyx()[0] - 5, 4)
        else:
            window.move(window.getyx()[0] + 1, 4)

        window.addstr("+ press : to enter a new task", curses.color_pair(
            4 + 1 * (selected[0] == len(get_task_list(hide_completed)) + 2)
        ))

def draw_task_table(window, data, start_y, start_x, selected, removing):
    """draw a table contaning info about the tasks"""
    # calculate the maximum width of each column
    column_widths = [
        max(len(str(item)) for item in column) + 2 for column in zip(*data)
    ][1:-1]

    # identify specific columns for prioritization
    headers = data[0][1:-1]

    # index of the name column (headers[1])
    name_column_index = 1  # adjusted for slicing [1:-1]

    table_width = sum(column_widths) + len(column_widths) + 5  # total width of the table
    max_width = window.getmaxyx()[1] - 10  # max width allowed for the table

    # if the table is wider than the maximum allowed width
    if table_width > max_width:
        # calculate how much the table exceeds the max width
        total_excess = table_width - max_width

        # reduce only the name column width
        min_name_width = len(headers[name_column_index]) + 3
        current_name_width = column_widths[name_column_index]

        # calculate the reduced width for the name column
        reduced_name_width = max(min_name_width, current_name_width - total_excess)

        # update the width for the name column
        column_widths[name_column_index] = reduced_name_width

        # recalculate the final table width
        final_table_width = sum(column_widths) + len(column_widths) + 5
        if final_table_width > max_width:
            # if still exceeding, further reduce the name column width
            total_excess = final_table_width - max_width
            column_widths[name_column_index] = max(
                min_name_width, column_widths[name_column_index] - total_excess
            )

    # draw table header
    for i, header in enumerate(data[0][1:-1]):
        window.addstr(
            start_y + 0, start_x + sum(column_widths[:i]) + i,
            ('╔' if not i else "╦") + '═' * column_widths[i]
        )
        window.addstr(
            start_y + 1, start_x + sum(column_widths[:i]) + i,
            "║ " + header.ljust(column_widths[i])
        )
        window.addstr(
            start_y + 2, start_x + sum(column_widths[:i]) + i,
            ('╠' if not i else "╬") + '═' * column_widths[i]
        )
        window.addstr(
            min(window.getmaxyx()[0] - 6, start_y + len(data) + 2),
            start_x + sum(column_widths[:i]) + i,
            ('╚' if not i else "╩") + '═' * column_widths[i]
        )
    for row in range(3):
        window.addstr(
            start_y + row, start_x + sum(column_widths) + 5,
            '║' if row % 2 else ('╗' if not row else '╣')
        )
    window.addstr(
        min(window.getmaxyx()[0] - 6, start_y + len(data) + 2),
        start_x + sum(column_widths) + 5,
        '╝'
    )

    # draw table rows
    for row_idx, row in enumerate(data[1:]):
        if start_y + row_idx + 3 <= window.getmaxyx()[0] - 7:
            for i, item in enumerate(row[1:-1]):
                window.addstr(
                    start_y + row_idx + 3, start_x + sum(column_widths[:i]) + i,
                    "║ "
                )

                # handle priority and completed columns
                if i == 0:
                    window.addstr(item[:2], curses.color_pair(8))
                else:
                    if data[0][i+1] == "priority":
                        item = ["low", "medium", "high"][item - 1]
                    elif data[0][i+1] == "completed":
                        item = "yes" if item else "no"
                    if item == "":
                        item = " " * (column_widths[i] - 2)

                    # handle removing subtasks
                    if row[-1] and i == 1:
                        if row[0] == removing:
                            item = "this task will be removed"
                        else:
                            item = "this subtask will be removed"

                    # truncate text and add ellipses if it exceeds column width
                    item_str = str(item)
                    if len(item_str) > column_widths[i]:
                        item_str = item_str[:column_widths[i] - 5] + "..."

                    window.addstr(
                        item_str[:column_widths[i] - 2],
                        curses.color_pair(
                            5 if ((selected[0] - 3) == row_idx and (selected[1] + 1) == i)
                            else (4 if (row[2][0] == "x") else 1)
                        ) if not row[-1] else curses.color_pair(7)
                    )

            window.addstr(start_y + row_idx + 3, start_x + sum(column_widths) + 5, '║')

def render_task_and_children(
    window, data,
    task, tasks_by_parent,
    indent, day,
    removing, hide_completed,
    bullets=False, removing_subtask=False
):
    """
    recursively render task and its children with appropriate indentation
    and hide completed tasks if required.
    """

    # if hide_completed is true and both the task and all its subtasks are completed, skip rendering
    if hide_completed and task['completed'] and all_subtasks_completed(task["id"]):
        return

    # mark task priority and bullet style
    important = "! " if task['priority'] == 3 else "  "
    if not bullets:
        bullet = "x" if task['completed'] else "•"
    elif check_migrated(task['date_history'], day):
        bullet = "<"
    elif task['due_date'] != task['date_added'] and task['date_added'] == day:
        bullet = ">"
    else:
        bullet = "x" if task['completed'] else "•"

    # prepare the parent name if it exists
    try:
        parent_name = Task.get_task(task['parent'])['name']
    except:
        parent_name = ""

    # append the task to the data list with appropriate indentation
    data.append([
        task['id'],
        important,
        '  ' * indent + bullet + " " + task['name'],  # indent for child tasks
        task['due_date'],
        task['priority'],
        parent_name,
        (removing == task['id']) or removing_subtask
    ])

    # recursively render child tasks
    if task['id'] in tasks_by_parent:
        for child in tasks_by_parent[task['id']]:
            render_task_and_children(
                window, data,
                child, tasks_by_parent,
                indent + 1, day,
                removing, hide_completed,
                bullets=bullets, removing_subtask=task['id'] == removing
            )

def day_view(window, selected, day, removing, hide_completed):
    """print the day view"""
    display_borders(window, selected)

    window.addstr(2, 5, "tasks for ")
    window.addstr(f"< {day} >", curses.color_pair(1 + 4 * (selected[0] == 2)))

    tasks = tasks_for_day(day)

    # group tasks by parent id
    tasks_by_parent = {}
    orphaned_tasks = []

    for task in tasks:
        parent_id = task['parent']
        if not parent_id or parent_id not in [t['id'] for t in tasks]:
            orphaned_tasks.append(task)  # task has no parent in today's tasks
        else:
            tasks_by_parent.setdefault(parent_id, []).append(task)

    # data table for display
    data = [['id', '', 'task', 'due', 'priority', 'part of', 'removing']]

    # recursively render orphaned tasks and their children
    for task in orphaned_tasks:
        render_task_and_children(
            window, data,
            task, tasks_by_parent,
            0, day,
            removing, hide_completed,
            bullets=True
        )

    # draw the table
    draw_task_table(window, data, 4, 5, selected, removing)

    # calculate and display completed tasks for today
    due_today = [task for task in tasks if task['due_date'] == day]
    completed_today = len([task for task in due_today if task['completed']])
    if removing:
        window.addstr(
            len(data) + 8, 5,
            "press r to confirm removal, esc to cancel",
            curses.color_pair(7)
        )
    else:
        window.addstr(
            len(data) + 8, 5,
            f"completed tasks due today: ({completed_today}/{len(due_today)}) " +
            f"({
                str(
                    round(completed_today / len(due_today) * 100, 2)
                ) + '%' if len(due_today) else 'n/a'
            })",
        )

def days_view(window, selected, day, removing, hide_completed, view_type):
    """print a view spanning several days."""
    display_borders(window, selected)

    # determine start and end dates based on the view type
    if view_type == "week":
        start = (
            dt.strptime(day, "%Y-%m-%d") - timedelta(
                days=dt.strptime(day, "%Y-%m-%d").weekday() + 1
            )
        ).strftime("%Y-%m-%d")
        end = (dt.strptime(start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
        tasks = tasks_for_week(day)
    elif view_type == "month":
        start = dt.strptime(day, "%Y-%m-%d").replace(day=1).strftime("%Y-%m-%d")
        end = dt.strptime(start, "%Y-%m-%d").replace(
            day=calendar.monthrange(
                dt.strptime(day, "%Y-%m-%d").year, dt.strptime(day, "%Y-%m-%d").month
            )[1]
        ).strftime("%Y-%m-%d")
        tasks = tasks_for_month(day)
    elif view_type == "year":
        start = dt.strptime(day, "%Y-%m-%d").replace(month=1, day=1).strftime("%Y-%m-%d")
        end = dt.strptime(start, "%Y-%m-%d").replace(month=12, day=31).strftime("%Y-%m-%d")
        tasks = tasks_for_year(day)
    else:
        raise ValueError("Invalid view type")

    window.addstr(2, 5, "tasks for ")
    window.addstr(f"< {start} - {end} >", curses.color_pair(1 + 4 * (selected[0] == 2)))

    tasks_by_parent = {}
    orphaned_tasks = []

    # process tasks
    for task in tasks:
        if view_type in ["month", "year"]:
            if task['due_type'] == "month":
                task['due_date'] = task['due_date'][:7]
            elif task['due_type'] == "year":
                task['due_date'] = task['due_date'][:4]
        parent_id = task['parent']
        if not parent_id or parent_id not in [t['id'] for t in tasks]:
            orphaned_tasks.append(task)
        else:
            tasks_by_parent.setdefault(parent_id, []).append(task)

    # data table for display
    data = [['id', '', 'task', 'due', 'priority', 'part of', 'removing']]

    # recursively render orphaned tasks and their children
    for task in orphaned_tasks:
        render_task_and_children(
            window, data,
            task, tasks_by_parent,
            0, day, removing, hide_completed
        )

    # draw the table
    draw_task_table(window, data, 4, 5, selected, removing)

    # calculate and display completed tasks
    due_tasks = [task for task in tasks if start <= task['due_date'] <= end]
    completed_tasks = len([task for task in due_tasks if task['completed']])
    completion_percentage = (
        str(round(completed_tasks / len(due_tasks) * 100, 2)) + "%"
        if len(due_tasks) else "n/a"
    )
    window.addstr(
        len(data) + 8, 5,
        (
            f"completed tasks due this {view_type}: "
            + f"({completed_tasks}/{len(due_tasks)}) ({completion_percentage})"
        )
    )

def week_view(*args):
    days_view(*args, "week")

def month_view(*args):
    days_view(*args, "month")

def year_view(*args):
    days_view(*args, "year")
