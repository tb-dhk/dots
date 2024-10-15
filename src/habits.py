import json
import os
import uuid
import curses
from datetime import date, timedelta
import math
from misc import display_borders

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
        super().__init__(name, habit_type="duration", unit="hours", target_value=target_value)

    @classmethod
    def add_duration_record(cls, habit_id, date, duration_sessions):
        habits = cls.load_habits()  # Load existing habits
        if habit_id in habits:
            if date not in habits[habit_id]['data']:
                habits[habit_id]['data'][date] = []
            habits[habit_id]['data'][date] += duration_sessions  # Add duration sessions
            habits[habit_id]['data'] = dict(sorted(habits[habit_id]['data'].items(), key=lambda x: x[0]))  # Sort by date
            habits[habit_id]['data'][date] = list(sorted(habits[habit_id]['data'][date], key=lambda x: x[0]))  # Sort by start time
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
            if duration_session:
                try:
                    sessions.remove(sessions[duration_session - 1])  # Remove the session
                except:
                    raise Exception(f"{sessions} {duration_session}")
            else:
                del habits[habit_id]['data'][date]  # Remove the entire date 
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

def duration_maps(window, selected, duration_map_settings, removing):
    display_borders(window, selected)
    based_on = duration_map_settings['based_on']
    index = duration_map_settings['index']

    window.addstr(2, 5, "duration habits")

    window.addstr(4, 5, "based on: ")
    window.addstr(f"< {based_on} >", curses.color_pair(1 + (selected[0] == 2)))

    habits = Habit.load_habits()
    habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}

    if habits:
        if based_on == "day":
            day = date.today() + timedelta(days=index)
            on = day.strftime("%Y-%m-%d")
            try:
                records = {habit: habits[habit]['data'][on] for habit in habits}
            except:
                for habit in habits:
                    if on not in habits[habit]['data']:
                        habits[habit]['data'][on] = []
                records = {habit: habits[habit]['data'][on] for habit in habits}
        else:
            id = list(habits.keys())[index % len(habits)]
            records = habits[id]['data']
            on = habits[id]['name']

        for record in records:
            records[record] = [[int(time[:2]) + int(time[3:]) / 60 for time in entry] for entry in records[record]]

        window.addstr(6, 5, f"< {on} >", curses.color_pair(1 + (selected[0] == 3)))

        max_length = max(len(habits[habit]['name']) for habit in records) if based_on == "day" else 10
        raw_records = [item for record in records.values() for item in record]
        try:
            adjusted_records = [
                (record[0], record[1] + 24 * ((record[1] <= record[0])))  # add 24 if record[1] <= record[0]
                for record in raw_records
            ]
            earliest_time = min(record[0] for record in adjusted_records)
            latest_time_diff = max(record[1] for record in adjusted_records) - earliest_time
        except:
            earliest_time = 0
            latest_time_diff = 0

        max_width = window.getmaxyx()[1] - 11 - max_length
        try:
            hour_width = max_width // (latest_time_diff)
        except:
            hour_width = 0
        else:
            hour_widths = [4, 6, 12]
            hour_widths = [width for width in hour_widths if width * (latest_time_diff) <= max_width]
            gaps = [abs(hour_width - width) for width in hour_widths]
            hour_width = hour_widths[gaps.index(min(gaps))]

        for hour in range(math.ceil(latest_time_diff) + 1):
            window.addstr(8, 7 + max_length + math.ceil(hour * hour_width), str((hour + int(earliest_time)) % 24).rjust(2, "0"))

        for i, (key, value) in enumerate(records.items()):
            if based_on == "day":
                id = key
                key = habits[key]['name']
            window.addstr(9 + i, 5, key.rjust(max_length), curses.color_pair(1 + (selected[0] == i + 4)))
            count = 0
            removing_this = (based_on == "day" and removing == id) or (based_on == "habit" and removing == key)
            if value == [] and removing_this:
                window.addstr(9 + i, 7 + max_length, "press 0 to remove this date, esc to cancel", curses.color_pair(7))
            for record in value:
                count += 1
                length = (record[1] - record[0]) % 24
                text_length = math.ceil((length) * hour_width)
                removing_text = f"press {count} to remove, esc to cancel"
                window.addstr(9 + i, 7 + max_length + math.ceil((record[0] - earliest_time) * hour_width), removing_text.center(text_length) if removing_this else " " * text_length, curses.color_pair(2 if not removing_this else 7))
    else:
        window.addstr(8, 5, "no duration habits!")

def add_new_habit(window, selected, new_habit):
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
