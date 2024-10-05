import json
import uuid
import curses
from datetime import datetime, date

class Task:
    def __init__(self, title, description="", due_date=date.today().strftime("%Y%m%d"), priority="medium", tags=[], subtasks=[], parents=[]):
        self.id = str(uuid.uuid4())  # Unique identifier for the task
        self.title = title  # Task title
        self.description = description  # Task description
        self.due_date = due_date  # Task due date (string, could be a day/week/month-based format)
        self.priority = priority  # Priority: low, medium, high (default: medium)
        self.completed = False  # Task completion status (default: False)
        self.subtasks = subtasks if subtasks else []  # List of subtasks (empty by default)
        self.parents = parents if parents else []  # List of parent tasks (empty by default)
        self.tags = tags if tags else []  # Optional tags (default: empty list)
        self.migrations = []  # Keep a history of all migrations (dates task was moved forward)
        self.date_added = str(datetime.now().date())  # When the task was originally scheduled
        self.date_history = []  # Track any past due dates for this task

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
    def add_task(cls, title, description="", due_date="", priority="medium", tags=[], subtasks=[], parents=[]):
        """Create a new task and add it to the tasks dictionary."""
        task = cls(title, description, due_date, priority, tags, subtasks, parents)  # Create new task instance
        tasks = cls.load_tasks()  # Load existing tasks
        tasks[task.id] = vars(task)  # Add task to the dictionary
        cls.save_tasks(tasks)  # Save updated tasks to JSON
        return task.id  # Return the ID of the new task

    @classmethod
    def edit_task(cls, task_id, **kwargs):
        """Edit an existing task's attributes."""
        tasks = cls.load_tasks()  # Load existing tasks
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
        return tasks.get(task_id)  # Return the task if it exists, else None

def display_task(stdscr, task_key, selected, ls, indent=0):
    task = Task.load_tasks()[str(task_key)]
    # Display the task title with indentation
    stdscr.move(stdscr.getyx()[0] + 1, 2)
    stdscr.addstr(f"{'  ' * indent}- {task['title']}", curses.color_pair(1 + 4 * (stdscr.getyx()[0] - 1 == selected)))
    ls.append(task_key)
    # Display subtasks if any
    for subtask_key in task['subtasks']:
        display_task(stdscr, subtask_key, selected, ls, indent=indent + 1)

def tasks(stdscr, option, selected, text_input, text_box):
    match option:
        case 0:
            for y in range(3, stdscr.getmaxyx()[0] - 5):
                stdscr.addstr(y, 0, "║", curses.color_pair(1))
                stdscr.addstr(y, stdscr.getmaxyx()[1] - 1, "║", curses.color_pair(1))
            stdscr.addstr(2, 0, "╔" + "═" * (stdscr.getmaxyx()[1] - 2) + "╗")
            stdscr.addstr(stdscr.getmaxyx()[0] - 5, 0, "╚" + "═" * (stdscr.getmaxyx()[1] - 2) + "╝")

            stdscr.move(2, 0)
            tasks = Task.load_tasks()
            tasks_vertical = []
            for task_key in tasks:
                if tasks[task_key]['parents'] == []:
                    display_task(stdscr, task_key, selected, tasks_vertical)
            
            stdscr.addstr(stdscr.getmaxyx()[0] - 4, 0, "╔" + "═" * (stdscr.getmaxyx()[1] - 2) + "╗")
            stdscr.addstr(stdscr.getmaxyx()[0] - 3, 0, "║", curses.color_pair(1))
            stdscr.addstr(stdscr.getmaxyx()[0] - 3, 2, text_box, curses.color_pair(1))
            if text_input:
                stdscr.addstr(stdscr.getmaxyx()[0] - 3, len(text_box) + 2, " ", curses.color_pair(2))
                stdscr.addstr(stdscr.getmaxyx()[0] - 3, len(text_box) + 3, " " * (stdscr.getmaxyx()[1] - len(text_box) - 6), curses.color_pair(1))
            else:
                stdscr.addstr(stdscr.getmaxyx()[0] - 3, len(text_box) + 2, " ", curses.color_pair(1))
            stdscr.addstr(stdscr.getmaxyx()[0] - 3, stdscr.getmaxyx()[1]-1, "║", curses.color_pair(1))
            stdscr.addstr(stdscr.getmaxyx()[0] - 2, 0, "╚" + "═" * (stdscr.getmaxyx()[1] - 2) + "╝")
