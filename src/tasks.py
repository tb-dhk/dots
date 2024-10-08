import json
import uuid
import curses
import calendar
from datetime import datetime as dt, date, timedelta
import toml

config = toml.load("config.toml")

class Task:
    def __init__(self, name, due_date=date.today().strftime("%Y-%m-%d"), priority=2, tags=[], subtasks=[], parent=[]):
        self.id = str(uuid.uuid4())  # Unique identifier for the task
        self.name = name  # Task name
        self.due_date = due_date  # Task due date (string, could be a day/week/month-based format)
        self.due_type = "day"
        self.priority = priority  # Priority: low, medium, high (default: medium)
        self.completed = False  # Task completion status (default: False)
        self.subtasks = subtasks if subtasks else []  # List of subtasks (empty by default)
        self.parent = None  # List of parent tasks (empty by default)
        self.tags = tags if tags else []  # Optional tags (default: empty list)
        self.date_added = str(dt.now().date())  # When the task was originally scheduled
        self.date_history = []  # Track any past due dates for this task
        self.recurrence = {
            "interval": None,
            "days": [],
        }

    @staticmethod
    def load_tasks(filename='data/tasks.json'):
        """Load tasks from a JSON file."""
        try:
            with open(filename, 'r') as file:
                return json.load(file)  # Load and return tasks as a dictionary
        except FileNotFoundError:
            return {}  # Return empty dict if file does not exist
        except json.JSONDecodeError:
            return {}  # Return empty dict if JSON is invalid

    @staticmethod
    def save_tasks(tasks, filename='data/tasks.json'):
        """Save tasks to a JSON file."""
        with open(filename, 'w') as file:
            json.dump(tasks, file, indent=4)  # Save tasks in a pretty format

    @classmethod
    def add_task(cls, name):
        """Create a new task and add it to the tasks dictionary."""
        task = cls(name)  # Create new task instance
        tasks = cls.load_tasks()  # Load existing tasks
        tasks[task.id] = vars(task)  # Add task to the dictionary
        cls.save_tasks(tasks)  # Save updated tasks to JSON
        return task.id  # Return the ID of the new task

    @classmethod
    def edit_task(cls, task_id, **kwargs):
        """Edit an existing task's attributes."""
        tasks = cls.load_tasks()  # Load existing tasks
        task_id = str(task_id)
        if task_id in tasks:  # Check if task exists
            task_data = tasks[task_id]  # Get task data
            # Update task attributes based on provided kwargs
            for key, value in kwargs.items():
                if key in task_data:
                    task_data[key] = value
            tasks[task_id] = task_data  # Update the task in the dictionary
            cls.save_tasks(tasks)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if task not found

    @classmethod
    def remove_task(cls, task_id):
        """Remove a task by its ID."""
        tasks = cls.load_tasks()  # Load existing tasks
        if task_id in tasks:  # Check if task exists
            del tasks[task_id]  # Remove the task from the dictionary
            cls.save_tasks(tasks)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if task not found

    @classmethod
    def get_task(cls, task_id):
        """Get a task by its ID."""
        tasks = cls.load_tasks()  # Load existing tasks
        return tasks[task_id]  # Return the task if it exists, else None

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

def check_migrated(history, date):
    for record in range(len(history)-1):
        if history[record][1] == history[record+1][0] and history[record][1] == date:
            return True
    return False

def tasks_for_day(day=None):
    if day is None:
        day = date.today().strftime("%Y-%m-%d")
    tasks = [task for _, task in Task.load_tasks().items() if task['due_date'] == day or task['date_added'] == day or check_migrated(task['date_history'], day)]
    return tasks

def tasks_for_days(start, end):
    tasks = []
    start = dt.strptime(start, "%Y-%m-%d")
    end = dt.strptime(end, "%Y-%m-%d")
    for day in range((end - start).days + 1):
        date = (start + timedelta(days=day)).strftime("%Y-%m-%d")
        for task in tasks_for_day(date):
            if task not in tasks:
                tasks.append(task)
    return tasks

def tasks_for_week(day):
    start = (dt.strptime(day, "%Y-%m-%d") - timedelta(days=dt.strptime(day, "%Y-%m-%d").weekday()-1)).strftime("%Y-%m-%d")
    end = (dt.strptime(start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
    tasks = tasks_for_days(start, end)
    return tasks

def tasks_for_month(day):
    start = dt.strptime(day, "%Y-%m-%d").replace(day=1).strftime("%Y-%m-%d")
    end = (dt.strptime(start, "%Y-%m-%d") + timedelta(days=31)).strftime("%Y-%m-%d")
    tasks = tasks_for_days(start, end)
    return tasks

def tasks_for_year(day):
    start = dt.strptime(day, "%Y-%m-%d").replace(month=1, day=1).strftime("%Y-%m-%d")
    end = dt.strptime(start, "%Y-%m-%d").replace(month=12, day=31).strftime("%Y-%m-%d")
    tasks = tasks_for_days(start, end)
    return tasks

def display_text_box(window, text_input, text_mode, text_box):
    """Display the input text box at the bottom of the screen."""
    max_y, max_x = window.getmaxyx()
    if text_input:
        window.addstr(max_y - 2, 2, text_box, curses.color_pair(1))
        window.addstr(max_y - 2, len(text_box) + 2, " ", curses.color_pair(2))
        window.addstr(max_y - 2, len(text_box) + 3, " " * (max_x - len(text_box) - 6), curses.color_pair(1))
    else:
        window.addstr(max_y - 2, len(text_box) + 2, " ", curses.color_pair(1))

def display_borders(window, selected, split=False):
    """Draw the border for the task list. If selected[0] >= 2, split the window in half."""
    max_y, max_x = window.getmaxyx()
    
    if selected[0] >= 2 and selected[0] < len(get_task_list()) + 2 and split:
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

def display_task(window, task_key, selected, task_list, text_mode, indent=0, split_x=0, box='wide', removing="", removing_subtask=False):
    """Display a task and its subtasks with indentation, adapted for two split boxes."""
    task = Task.load_tasks()[str(task_key)]
    if not task:
        return  # Skip if task not found

    # Choose the starting column based on the box ('left' or 'right')
    start_col = 2 if box != 'right' else split_x + 3
    end_col = split_x - 1 if box == 'left' else window.getmaxyx()[1] - 2
    window.move(window.getyx()[0] + 1, start_col)
    completed = task['completed']
    symbol = 'x' if completed else '•'
    important = "! " if task['priority'] == 3 else "  "

    window.addstr(important, curses.color_pair(8))
    if removing != task_key and not removing_subtask:
        window.addstr(f"{'  ' * indent}{symbol} ", curses.color_pair(4 if window.getyx()[0] + 1 != selected[0] and task['completed'] else (1 + 4 * (window.getyx()[0] + 1 == selected[0]))))
        window.addstr(task['name'], curses.color_pair(4 if window.getyx()[0] + 1 != selected[0] and task['completed'] else (1 + 4 * (window.getyx()[0] + 1 == selected[0]))) | (curses.A_ITALIC if task['completed'] else 0))
    else:
        window.addstr('  ' * indent)
        window.addstr(f"{symbol} ", curses.color_pair(7))
        window.addstr("this subtask will be removed" if removing_subtask else "press r to remove, ESC to cancel", curses.color_pair(7))

    if text_mode == "edit parent":
        number = len(task_list)
        window.addstr(window.getyx()[0], end_col - 3 - len(str(number)), f"({number})", curses.color_pair(1))
    else:
        window.addstr(window.getyx()[0], end_col - 13, f"[{task['due_date'].ljust(10)}]", curses.color_pair(1))

    task_list.append(task_key)
    for subtask_key in task['subtasks']:
        display_task(window, subtask_key, selected, task_list, text_mode, indent + 1, split_x, box, removing, bool(removing == task_key))

def display_task_details(window, task_id, split_x, selected):
    """Display the attributes of the selected task in the right box, with aligned colons and edit commands."""
    task = Task.load_tasks()[str(task_id)]
    if not task:
        return

    try:
        due_date = dt.strptime(task['due_date'], '%Y-%m-%d')
    except:
        passed = False
    else:
        passed = due_date.date() < dt.now().date()
    
    # Define the edit commands for each task attribute
    edit_commands = {
        "name": "n",
        "completed": "x",
        "due date": "<" if passed else ">",
        "parent": "m",
        "priority": "p",
        "tags": "t",
        "recurrence": "c"
    }

    # Define the task details with keys for alignment
    details = {
        "name": task['name'],
        "completed": 'yes' if task['completed'] else 'no',
        "due date": task['due_date'],
        "parent": Task.load_tasks()[task['parent']]['name'] if task['parent'] else "none",
        "priority": ["low", "medium", "high"][int(task['priority']) - 1],
        "tags": ', '.join(task['tags']),
    }

    # Calculate the maximum key length for proper alignment
    max_key_length = max(len(key) for key in details.keys())
    
    # Display each detail line with aligned colons and edit commands
    window.move(1, split_x + 3)
    count = 0
    for key, value in details.items():
        # Format with right-aligned colons and edit commands
        line = f"{key.ljust(max_key_length)} ({edit_commands[key]}) : {value}"
        window.addstr(line, curses.color_pair(1 + (selected[1] == count) ))
        window.move(window.getyx()[0] + 2, split_x + 3)
        count += 1

def display_tasks(window, option, selected, text_input, text_mode, text_box, removing):
    """Main function to display tasks, with task details in the right box when selected."""
    if option == 0:
        max_y, max_x = window.getmaxyx()
        display_borders(window, selected, split=True)
        tasks = Task.load_tasks()

        split_x = max_x // 2 - 1 if selected[0] >= 2 else 0 
        task_list = []

        if selected[0] >= 2 and selected[0] < len(get_task_list()) + 2:
            # Display tasks in the left box
            window.move(0, 0)  # Changed to start at row 3
            for task_key in tasks:
                if not tasks[task_key]['parent']:
                    display_task(window, task_key, selected, task_list, text_mode, split_x=split_x, box='left', removing=removing)

            # Find the selected task and display its details in the right box
            selected_task_key = task_list[selected[0] - 2]
            display_task_details(window, selected_task_key, split_x, selected)
        else:
            # Single full-width box display
            window.move(0, 0)  # Changed to start at row 3
            for task_key in tasks:
                if not tasks[task_key]['parent']:
                    display_task(window, task_key, selected, task_list, text_mode)

        window.move(len(get_task_list()) + 1, 4)
        window.addstr("+ press : to enter a new task", curses.color_pair(4 + 1 * (selected[0] == len(get_task_list()) + 2)))
            
        display_text_box(window, text_input, text_mode, text_box)


def draw_table(window, data, start_y, start_x, selected, removing):
    # Calculate the maximum width of each column
    column_widths = [max(len(str(item)) for item in column) + 3 for column in zip(*data)][1:]

    # Draw table header
    for i, header in enumerate(data[0][1:]):
        window.addstr(start_y + 0, start_x + sum(column_widths[:i]) + i, '+' + '-' * column_widths[i])
        window.addstr(start_y + 1, start_x + sum(column_widths[:i]) + i, "| " + header.ljust(column_widths[i]))
        window.addstr(start_y + 2, start_x + sum(column_widths[:i]) + i, '+' + '-' * column_widths[i])
        window.addstr(start_y + len(data) + 2, start_x + sum(column_widths[:i]) + i, '+' + '-' * column_widths[i])
    for row in range(3):
        window.addstr(start_y + row, start_x + sum(column_widths) + 5, '|' if row % 2 else '+')
    window.addstr(start_y + len(data) + 2, start_x + sum(column_widths) + 5, '+')

    # Draw table rows
    for row_idx, row in enumerate(data[1:]):
        for i, item in enumerate(row[1:-1]):
            window.addstr(start_y + row_idx + 3, start_x + sum(column_widths[:i]) + i, "| ")
            if i == 0:
                window.addstr(item[:2], curses.color_pair(8))
                window.addstr(item[2:], curses.color_pair(1 + (selected[0] - 3) == row_idx))
            else:
                if data[0][i+1] == "priority":
                    item = ["low", "medium", "high"][item - 1]
                elif data[0][i+1] == "completed":
                    item = "yes" if item else "no"
                if item == "":
                    item = " " * (column_widths[i] - 2)
                if row[-1] and i == 1:
                    item = "press r to remove, ESC to cancel" if row[0] == removing else "this subtask will be removed"
                window.addstr(str(item), curses.color_pair((1 + 4 * ((selected[0] - 3) == row_idx and (selected[1] + 1) == i))) if not row[-1] else curses.color_pair(7))
        window.addstr(start_y + row_idx + 3, start_x + sum(column_widths) + 5, '|')

def render_task_and_children(window, data, task, tasks_by_parent, indent, day, removing, bullets=False, removing_subtask=False):
    """Recursively render task and its children with appropriate indentation."""
    important = "! " if task['priority'] == 3 else "  "
    if not bullets:
        bullet = "x" if task['completed'] else "•"
    elif check_migrated(task['date_history'], day):
        bullet = "<"
    elif task['due_date'] != task['date_added'] and task['date_added'] == day:
        bullet = ">"
    else:
        bullet = "x" if task['completed'] else "•"

    # Prepare the parent name if it exists
    try:
        parent_name = Task.get_task(task['parent'])['name']
    except:
        parent_name = ""

    # Append the task to the data list with appropriate indentation
    data.append([
        task['id'],
        important,
        '  ' * indent + bullet + " " + task['name'],  # indent for child tasks
        task['due_date'],
        task['priority'],
        parent_name,
        (removing == task['id']) or removing_subtask
    ])

    # Recursively render child tasks
    if task['id'] in tasks_by_parent:
        for child in tasks_by_parent[task['id']]:
            render_task_and_children(window, data, child, tasks_by_parent, indent + 1, day, removing, bullets=bullets, removing_subtask=task['id']==removing)

def day_view(window, selected, day, text_input, text_mode, text_box, removing):
    display_borders(window, selected)

    window.addstr(2, 5, f"tasks for ")
    window.addstr(f"< {day} >", curses.color_pair(1 + 4 * (selected[0] == 2)))

    tasks = tasks_for_day(day)
    
    # Group tasks by parent ID
    tasks_by_parent = {}
    orphaned_tasks = []

    for task in tasks:
        parent_id = task['parent']
        if not parent_id or parent_id not in [t['id'] for t in tasks]:
            orphaned_tasks.append(task)  # Task has no parent in today's tasks
        else:
            tasks_by_parent.setdefault(parent_id, []).append(task)

    # Data table for display
    data = [['id', '', 'task', 'due', 'priority', 'part of', 'removing']]

    # Recursively render orphaned tasks and their children
    for task in orphaned_tasks:
        render_task_and_children(window, data, task, tasks_by_parent, 0, day, removing, bullets=True)

    # Draw the table
    draw_table(window, data, 4, 5, selected, removing)

    # Calculate and display completed tasks for today
    due_today = [task for task in tasks if task['due_date'] == day]
    completed_today = len([task for task in due_today if task['completed']])
    window.addstr(
        len(data) + 8, 5, 
        f"completed tasks due today: ({completed_today}/{len(due_today)}) " +
        f"({str(round(completed_today / len(due_today) * 100, 2)) + '%' if len(due_today) else 'n/a'})"
    )

    # Display text box input (for text entry mode)
    display_text_box(window, text_input, text_mode, text_box)

def week_view(window, selected, day, text_input, text_mode, text_box, removing):
    display_borders(window, selected)

    start = (dt.strptime(day, "%Y-%m-%d") - timedelta(days=dt.strptime(day, "%Y-%m-%d").weekday() + 1)).strftime("%Y-%m-%d")
    end = (dt.strptime(start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")

    window.addstr(2, 5, f"tasks for ")
    window.addstr(f"< {start} - {end} >", curses.color_pair(1 + 4 * (selected[0] == 2)))

    tasks = tasks_for_week(day)

    # Group tasks by parent ID
    tasks_by_parent = {}
    orphaned_tasks = []

    for task in tasks:
        parent_id = task['parent']
        if not parent_id or parent_id not in [t['id'] for t in tasks]:
            orphaned_tasks.append(task)  # Task has no parent in today's tasks
        else:
            tasks_by_parent.setdefault(parent_id, []).append(task)

    # Data table for display
    data = [['id', '', 'task', 'due', 'priority', 'part of', 'removing']]

    # Recursively render orphaned tasks and their children
    for task in orphaned_tasks:
        render_task_and_children(window, data, task, tasks_by_parent, 0, day, removing)

    # Draw the table
    draw_table(window, data, 4, 5, selected, removing)

    # Calculate and display completed tasks for today
    due_today = [task for task in tasks if task['due_date'] == day]
    completed_today = len([task for task in due_today if task['completed']])
    window.addstr(
        len(data) + 8, 5, 
        f"completed tasks due today: ({completed_today}/{len(due_today)}) " +
        f"({str(round(completed_today / len(due_today) * 100, 2)) + '%' if len(due_today) else 'n/a'})"
    )

    # Display text box input (for text entry mode)
    display_text_box(window, text_input, text_mode, text_box)

def month_view(window, selected, day, text_input, text_mode, text_box, removing):
    display_borders(window, selected)

    start = dt.strptime(day, "%Y-%m-%d").replace(day=1).strftime("%Y-%m-%d")
    end = dt.strptime(start, "%Y-%m-%d").replace(day=calendar.monthrange(dt.strptime(day, "%Y-%m-%d").year, dt.strptime(day, "%Y-%m-%d").month)[1]).strftime("%Y-%m-%d")

    window.addstr(2, 5, f"tasks for ")
    window.addstr(f"< {start} - {end} >", curses.color_pair(1 + 4 * (selected[0] == 2)))

    tasks = tasks_for_month(day)
    
    tasks_by_parent = {}
    orphaned_tasks = []

    for task in tasks:
        if task['due_type'] == "month":
            task['due_date'] = task['due_date'][:7]
        elif task['due_type'] == "year":
            task['due_date'] = task['due_date'][:4]
        parent_id = task['parent']
        if not parent_id or parent_id not in [t['id'] for t in tasks]:
            orphaned_tasks.append(task)  # Task has no parent in today's tasks
        else:
            tasks_by_parent.setdefault(parent_id, []).append(task)

    # Data table for display
    data = [['id', '', 'task', 'due', 'priority', 'part of', 'removing']]

    # Recursively render orphaned tasks and their children
    for task in orphaned_tasks:
        render_task_and_children(window, data, task, tasks_by_parent, 0, day, removing)

    # Draw the table
    draw_table(window, data, 4, 5, selected, removing)

    # Calculate and display completed tasks for today
    due_today = [task for task in tasks if task['due_date'] == day]
    completed_today = len([task for task in due_today if task['completed']])
    window.addstr(
        len(data) + 8, 5, 
        f"completed tasks due today: ({completed_today}/{len(due_today)}) " +
        f"({str(round(completed_today / len(due_today) * 100, 2)) + '%' if len(due_today) else 'n/a'})"
    )

    # Display text box input (for text entry mode)
    display_text_box(window, text_input, text_mode, text_box)

def year_view(window, selected, day, text_input, text_mode, text_box, removing):
    display_borders(window, selected)

    start = dt.strptime(day, "%Y-%m-%d").replace(month=1, day=1).strftime("%Y-%m-%d")
    end = dt.strptime(start, "%Y-%m-%d").replace(month=12, day=31).strftime("%Y-%m-%d")

    window.addstr(2, 5, f"tasks for ")
    window.addstr(f"< {start} - {end} >", curses.color_pair(1 + 4 * (selected[0] == 2)))

    tasks = tasks_for_year(day)
    
    tasks_by_parent = {}
    orphaned_tasks = []

    for task in tasks:
        if task['due_type'] == "month":
            task['due_date'] = task['due_date'][:7]
        elif task['due_type'] == "year":
            task['due_date'] = task['due_date'][:4]
        parent_id = task['parent']
        if not parent_id or parent_id not in [t['id'] for t in tasks]:
            orphaned_tasks.append(task)  # Task has no parent in today's tasks
        else:
            tasks_by_parent.setdefault(parent_id, []).append(task)

    # Data table for display
    data = [['id', '', 'task', 'due', 'priority', 'part of', 'removing']]

    # Recursively render orphaned tasks and their children
    for task in orphaned_tasks:
        render_task_and_children(window, data, task, tasks_by_parent, 0, day, removing)

    # Draw the table
    draw_table(window, data, 4, 5, selected, removing)

    # Calculate and display completed tasks for today
    due_today = [task for task in tasks if task['due_date'] == day]
    completed_today = len([task for task in due_today if task['completed']])
    window.addstr(
        len(data) + 8, 5, 
        f"completed tasks due today: ({completed_today}/{len(due_today)}) " +
        f"({str(round(completed_today / len(due_today) * 100, 2)) + '%' if len(due_today) else 'n/a'})"
    )

    # Display text box input (for text entry mode)
    display_text_box(window, text_input, text_mode, text_box)

