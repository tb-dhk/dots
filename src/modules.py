import os
import uuid
import json

from datetime import date, timedelta, datetime as dt

def load_items(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)  # Load and return tasks as a dictionary
    except FileNotFoundError:
        return {}  # Return empty dict if file does not exist
    except json.JSONDecodeError:
        return {}  # Return empty dict if JSON is invalid

def save_items(items, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(items, file, indent=4)  # Save tasks in a pretty format

class Task:
    def __init__(
        self, name,
        due_date=date.today().strftime("%Y-%m-%d"),
        due_type="day", priority=2, tags=[], subtasks=[], parent=[]
    ):
        self.id = str(uuid.uuid4())  # Unique identifier for the task
        self.name = name  # Task name
        self.due_date = due_date  # Task due date (string, could be a day/week/month-based format)
        self.due_type = due_type
        self.priority = priority  # Priority: low, medium, high (default: medium)
        self.completed = False  # Task completion status (default: False)
        self.subtasks = subtasks   # List of subtasks (empty by default)
        self.parent = parent  # List of parent tasks (empty by default)
        self.tags = tags  # Optional tags (default: empty list)
        self.date_added = str(dt.now().date())  # When the task was originally scheduled
        self.date_history = []  # Track any past due dates for this task
        self.recurrence = {
            "interval": None,
            "days": [],
        }

    @staticmethod
    def load_tasks(filename=os.path.join(os.path.expanduser("~"), ".dots", "tasks.json")):
        return load_items(filename)

    @staticmethod
    def save_tasks(tasks, filename=os.path.join(os.path.expanduser("~"), ".dots", "tasks.json")):
        save_items(tasks, filename)

    @classmethod
    def add_task(cls, name, due_date=date.today().strftime("%Y-%m-%d"), due_type="day"):
        """Create a new task and add it to the tasks dictionary."""
        task = cls(name, due_date=due_date, due_type=due_type)
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

class Habit:
    def __init__(self, name, habit_type, unit, target_value=""):
        self.id = str(uuid.uuid4())  # Unique identifier for the habit
        self.name = name  # Habit name
        self.type = habit_type  # Habit type
        self.unit = unit  # Measurement unit
        self.target_value = target_value  # Target value (optional)
        self.data = {}  # Data will be saved to habits.json

    @staticmethod
    def load_habits(filename=os.path.join(os.path.expanduser("~"), ".dots", "habits.json")):
        return load_items(filename)

    @staticmethod
    def save_habits(habits, filename=os.path.join(os.path.expanduser("~"), ".dots", "habits.json")):
        save_items(habits, filename)

    @classmethod
    def add_habit(cls, name, habit_type, unit, target_value=""):
        """Add a new habit."""
        habit = cls(name, habit_type, unit, target_value)
        habits = cls.load_habits()  # Load existing habits
        habits[habit.id] = vars(habit)  # Add habit to the dictionary
        cls.save_habits(habits)  # Save updated habits to JSON
        return habit.id  # Return the ID of the new habit

    @classmethod
    def edit_habit(cls, habit_id, **kwargs):
        """Edit an existing habit's attributes."""
        habits = cls.load_habits()  # Load existing habits
        habit_id = str(habit_id)
        if habit_id in habits:  # Check if habit exists
            habit_data = habits[habit_id]  # Get habit data
            # Update habit attributes based on provided kwargs
            for key, value in kwargs.items():
                if key in habit_data:
                    habit_data[key] = value
            habits[habit_id] = habit_data  # Update the habit in the dictionary
            cls.save_habits(habits)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if habit not found

    @classmethod
    def remove_habit(cls, habit_id):
        """Remove a habit by its ID."""
        habits = cls.load_habits()  # Load existing habits
        if habit_id in habits:  # Check if habit exists
            del habits[habit_id]  # Remove the habit from the dictionary
            cls.save_habits(habits)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if habit not found

    @classmethod
    def get_habit(cls, habit_id):
        """Get a habit by its ID."""
        habits = cls.load_habits()  # Load existing habits
        return habits.get(habit_id, None)  # Return the habit if it exists, else None

class DurationHabit(Habit):
    def __init__(self, name, target_value=""):
        super().__init__(name, habit_type="duration", unit="hours", target_value=target_value)

    @classmethod
    def add_duration_record(cls, habit_id, duration_sessions):
        habits = cls.load_habits()  # Load existing habits

        if habit_id in habits:
            # Ensure the data structure for this habit is initialized
            if 'data' not in habits[habit_id]:
                habits[habit_id]['data'] = []

            # Split duration sessions if they exceed midnight
            updated_sessions = []
            for session in duration_sessions:
                start_time = dt.strptime(session[0], "%Y-%m-%d-%H:%M")
                end_time = dt.strptime(session[1], "%Y-%m-%d-%H:%M")

                # Check if the session exceeds midnight
                if start_time.date() < end_time.date():
                    # Split the session into two
                    midnight = dt.combine(start_time.date() + timedelta(days=1), dt.min.time())

                    # First part: from start to midnight
                    updated_sessions.append([session[0], midnight.strftime("%Y-%m-%d-%H:%M")])

                    # Second part: from midnight to end
                    updated_sessions.append([midnight.strftime("%Y-%m-%d-%H:%M"), session[1]])
                else:
                    # If it does not exceed midnight, add the session as is
                    updated_sessions.append(session)

            # Add sessions to the habit data, ensuring they are sorted by start time
            habits[habit_id]['data'] += updated_sessions

            # Sort the records by start time
            habits[habit_id]['data'] = sorted(
                habits[habit_id]['data'],
                key=lambda x: dt.strptime(x[0], "%Y-%m-%d-%H:%M")
            )

            cls.save_habits(habits)  # Save updated habits to JSON
            return True
        return False

    @classmethod
    def remove_duration_record(cls, habit_id, duration_session):
        habits = cls.load_habits()
        if habit_id in habits:
            if duration_session:
                habits[habit_id]['data'].remove(duration_session)  # Remove the session
            cls.save_habits(habits)  # Save updated habits to JSON
            return True
        return False

class ProgressHabit(Habit):
    def __init__(self, name, unit, target_value):
        super().__init__(name, habit_type="Progress", unit=unit, target_value=target_value)

    @classmethod
    def add_progress_record(cls, habit_id, on_date, completed_value):
        habits = cls.load_habits()
        if habit_id in habits:
            habits[habit_id]['data'][on_date] = completed_value  # Add record
            cls.save_habits(habits)
            return True
        return False

    @classmethod
    def edit_progress_record(cls, habit_id, on_date, new_completed_value):
        habits = cls.load_habits()
        if habit_id in habits and on_date in habits[habit_id]['data']:
            habits[habit_id]['data'][on_date] = new_completed_value  # Edit record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False

    @classmethod
    def remove_progress_record(cls, habit_id, on_date):
        habits = cls.load_habits()
        if habit_id in habits and on_date in habits[habit_id]['data']:
            del habits[habit_id]['data'][on_date]  # Remove record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False

class FrequencyHabit(Habit):
    def __init__(self, name, unit, target_value):
        super().__init__(name, habit_type="Frequency", unit=unit, target_value=target_value)

    @classmethod
    def add_occurrence_record(cls, habit_id, on_date, occurrences):
        habits = cls.load_habits()
        if habit_id in habits:
            habits[habit_id]['data'][on_date] = occurrences  # Add record
            cls.save_habits(habits)  # Save updated habits to JSON
            return True
        return False

    @classmethod
    def edit_occurrence_record(cls, habit_id, on_date, new_occurrences):
        habits = cls.load_habits()
        if habit_id in habits and on_date in habits[habit_id]['data']:
            habits[habit_id]['data'][on_date] = new_occurrences  # Edit record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False

    @classmethod
    def remove_occurrence_record(cls, habit_id, on_date):
        habits = cls.load_habits()
        if habit_id in habits and on_date in habits[habit_id]['data']:
            del habits[habit_id]['data'][on_date]  # Remove record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False
