import json
import os
import uuid
import curses
from misc import display_borders
import os
import json
import uuid
import os

class Habit:
    def __init__(self, name, habit_type, unit, target_value=""):
        self.id = str(uuid.uuid4())  # Unique identifier for the habit
        self.name = name  # Habit name
        self.type = habit_type  # Habit type
        self.unit = unit  # Measurement unit
        self.target_value = target_value  # Target value (optional)
        self.data = {}  # Data will be saved to habits.json

    @classmethod
    def load_habits(cls, filename=os.path.join(os.path.expanduser("~"), ".dots", "habits.json")):
        """Load habits from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)  # Load and return habits as a dictionary
        except FileNotFoundError:
            return {}  # Return empty dict if file does not exist
        except json.JSONDecodeError:
            return {}  # Return empty dict if JSON is invalid

    @classmethod
    def save_habits(cls, habits, filename=os.path.join(os.path.expanduser("~"), ".dots", "habits.json")):
        """Save habits to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(habits, file, indent=4)  # Save habits in a pretty format

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
    def __init__(self, name, unit, target_value=""):
        super().__init__(name, habit_type="duration", unit=unit, target_value=target_value)

    @classmethod
    def add_duration_record(cls, habit_id, date, duration_sessions):
        habits = cls.load_habits()  # Load existing habits
        if habit_id in habits:
            if date not in habits[habit_id]['data']:
                habits[habit_id]['data'][date] = []
            habits[habit_id]['data'][date].extend(duration_sessions)  # Add duration sessions
            cls.save_habits(habits)  # Save updated habits to JSON
            return True
        return False

    @classmethod
    def edit_duration_record(cls, habit_id, date, old_session, new_session):
        habits = cls.load_habits()
        if habit_id in habits and date in habits[habit_id]['data']:
            sessions = habits[habit_id]['data'][date]
            if old_session in sessions:
                sessions[sessions.index(old_session)] = new_session  # Edit the session
                cls.save_habits(habits)  # Save updated habits to JSON
                return True
        return False

    @classmethod
    def remove_duration_record(cls, habit_id, date, duration_session):
        habits = cls.load_habits()
        if habit_id in habits and date in habits[habit_id]['data']:
            sessions = habits[habit_id]['data'][date]
            if duration_session in sessions:
                sessions.remove(duration_session)  # Remove the session
                cls.save_habits(habits)  # Save updated habits to JSON
                return True
        return False

class ProgressHabit(Habit):
    def __init__(self, name, unit, target_value):
        super().__init__(name, habit_type="Progress", unit=unit, target_value=target_value)

    @classmethod
    def add_progress_record(cls, habit_id, date, completed_value):
        habits = cls.load_habits()
        if habit_id in habits:
            habits[habit_id]['data'][date] = completed_value  # Add record
            cls.save_habits(habits)
            return True
        return False

    @classmethod
    def edit_progress_record(cls, habit_id, date, new_completed_value):
        habits = cls.load_habits()
        if habit_id in habits and date in habits[habit_id]['data']:
            habits[habit_id]['data'][date] = new_completed_value  # Edit record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False

    @classmethod
    def remove_progress_record(cls, habit_id, date):
        habits = cls.load_habits()
        if habit_id in habits and date in habits[habit_id]['data']:
            del habits[habit_id]['data'][date]  # Remove record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False

class FrequencyHabit(Habit):
    def __init__(self, name, unit, target_value):
        super().__init__(name, habit_type="Frequency", unit=unit, target_value=target_value)

    @classmethod
    def add_occurrence_record(cls, habit_id, date, occurrences):
        habits = cls.load_habits()
        if habit_id in habits:
            habits[habit_id]['data'][date] = occurrences  # Add record
            cls.save_habits(habits)  # Save updated habits to JSON
            return True
        return False

    @classmethod
    def edit_occurrence_record(cls, habit_id, date, new_occurrences):
        habits = cls.load_habits()
        if habit_id in habits and date in habits[habit_id]['data']:
            habits[habit_id]['data'][date] = new_occurrences  # Edit record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False

    @classmethod
    def remove_occurrence_record(cls, habit_id, date):
        habits = cls.load_habits()
        if habit_id in habits and date in habits[habit_id]['data']:
            del habits[habit_id]['data'][date]  # Remove record
            cls.save_habits(habits)  # Save changes to JSON
            return True
        return False

def add_new_habit(window, selected, text_input, text_box, text_mode, text_index, new_habit):
    display_borders(window, selected)

    window.addstr(2, 5, "new habit")

    # input for habit name
    window.addstr(4, 5, "name: ")
    window.addstr(new_habit['name'], curses.color_pair(1 + (selected[0] == 2)))  # display current input for habit name

    window.addstr(6, 5, "type: ")
    window.addstr(f"< {new_habit['type']} >", curses.color_pair(1 + (selected[0] == 3)))  # display current input for habit type

    # input for measurement unit
    window.addstr(8, 5, "unit (e.g. hours): ")
    window.addstr(new_habit['unit'] if new_habit['unit'] else "(none)", curses.color_pair(1 + (selected[0] == 4)))  # display current input for unit

    # input for target value
    window.addstr(10, 5, "target value: ")
    window.addstr(str(new_habit['target_value']), curses.color_pair(1 + (selected[0] == 5)))  # display current input for target value

    # additional information if needed
    window.addstr(12, 5, "submit", curses.color_pair(1 + (selected[0] == 6)))
    
    # refresh window to display updates
    window.refresh()
