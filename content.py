import json
import uuid
import curses
from datetime import datetime, date

class Task:
    def __init__(self, name, due_date=date.today().strftime("%Y%m%d"), priority=2, tags=[], subtasks=[], parent=[]):
        self.id = str(uuid.uuid4())  # Unique identifier for the task
        self.name = name  # Task name
        self.due_date = due_date  # Task due date (string, could be a day/week/month-based format)
        self.priority = priority  # Priority: low, medium, high (default: medium)
        self.completed = False  # Task completion status (default: False)
        self.subtasks = subtasks if subtasks else []  # List of subtasks (empty by default)
        self.parent = None  # List of parent tasks (empty by default)
        self.tags = tags if tags else []  # Optional tags (default: empty list)
        self.date_added = str(datetime.now().date())  # When the task was originally scheduled
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
    def add_task(cls, name, due_date="", priority="medium", tags=[], subtasks=[], parent=None):
        """Create a new task and add it to the tasks dictionary."""
        task = cls(name, due_date, priority, tags, subtasks, parent)  # Create new task instance
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

def display_text_box(window, text_input, text_mode, text_box):
    """Display the input text box at the bottom of the screen."""
    max_y, max_x = window.getmaxyx()
    if text_input:
        window.addstr(max_y - 2, 2, text_box, curses.color_pair(1))
        window.addstr(max_y - 2, len(text_box) + 2, " ", curses.color_pair(2))
        window.addstr(max_y - 2, len(text_box) + 3, " " * (max_x - len(text_box) - 6), curses.color_pair(1))
    else:
        window.addstr(max_y - 2, len(text_box) + 2, " ", curses.color_pair(1))

def display_borders(window, selected):
    """Draw the border for the task list. If selected[0] >= 2, split the window in half."""
    max_y, max_x = window.getmaxyx()
    
    if selected[0] >= 2:
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
        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
    except:
        passed = False
    else:
        passed = due_date.date() < datetime.now().date()
    
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
        "priority": ["low", "medium", "high"][task['priority'] - 1],
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
        display_borders(window, selected)
        tasks = Task.load_tasks()

        split_x = max_x // 2 - 1 if selected[0] >= 2 else 0 
        task_list = []

        if selected[0] >= 2:
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

            # Clear or avoid calling display_task_details() if selected[0] < 2
            window.move(1, split_x + 3)  # Ensure cursor is placed properly after task display
            
        display_text_box(window, text_input, text_mode, text_box)


def draw_table(window, data):
    # Clear screen
    window.clear()

    # Calculate the maximum width of each column
    max_lengths = [max(len(str(item)) for item in column) for column in zip(*data)]

    # Get the width of the window
    height, width = window.getmaxyx()

    # Calculate total width and scale column widths to fit within the terminal width
    total_length = sum(max_lengths) + len(max_lengths) - 1  # account for spaces between columns
    scale_factor = (width - 2) / total_length  # subtract for table borders

    # Calculate actual widths for each column
    column_widths = [int(length * scale_factor) for length in max_lengths]

    # Draw table header
    window.addstr(0, 0, '+' + '-' * (width - 2) + '+')
    for i, header in enumerate(data[0]):
        window.addstr(1, sum(column_widths[:i]) + i, header.ljust(column_widths[i]))
    window.addstr(2, 0, '+' + '-' * (width - 2) + '+')

    # Draw table rows
    for row_idx, row in enumerate(data[1:], start=3):
        window.addstr(row_idx, 0, '|')  # left border
        for i, item in enumerate(row):
            window.addstr(row_idx, sum(column_widths[:i]) + i + 1, str(item).ljust(column_widths[i]))
            window.addstr(row_idx, sum(column_widths[:i + 1]) + i + 1, '|')  # right border
        window.addstr(row_idx, 0, '+' + '-' * (width - 2) + '+')

    # Refresh the screen to display the table
    window.refresh()
    window.getch()  # Wait for user input


