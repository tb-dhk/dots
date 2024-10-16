import json
import os
import uuid
import curses
from datetime import date, timedelta, datetime as dt
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
            habits[habit_id]['data'].extend(updated_sessions)
            # Sort the records by start time
            habits[habit_id]['data'] = sorted(habits[habit_id]['data'], key=lambda x: dt.strptime(x[0], "%Y-%m-%d-%H:%M"))

            cls.save_habits(habits)  # Save updated habits to JSON
            return True
        return False

    @classmethod
    def remove_duration_record(cls, habit_id, date, duration_session):
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

def get_records_from_habits(habits, index):
    id = list(habits.keys())[index % len(habits)]
    raw_records = habits[id]['data']

    records = {date.today().strftime("%Y-%m-%d"): []}

    for record in raw_records:
        day_of_record = record[0][:10]
        try:
            records[day_of_record].append(record)
        except KeyError:
            records[day_of_record] = [record]

    return records

def duration_maps(window, selected, map_settings, removing):
    display_borders(window, selected)
    based_on = map_settings['based_on']
    index = map_settings['index']

    window.addstr(2, 5, "duration habits")
    window.addstr(4, 5, "based on: ")
    window.addstr(f"< {based_on} >", curses.color_pair(1 + (selected[0] == 2)))

    habits = Habit.load_habits()
    habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "duration"}

    if habits:
        if based_on == "day":
            day = date.today() + timedelta(days=index)
            tomorrow = dt.combine(date.today() + timedelta(days=index + 1), dt.min.time())
            on = day.strftime("%Y-%m-%d")
            # all records that start or end on this day (fetch date from datetime)
            records = {habit: [record for record in habits[habit]['data'] if record[0][:10] == on] for habit in habits}
            
            try:
                earliest_time = min(min(dt.strptime(record[0], "%Y-%m-%d-%H:%M") for record in records[habit]) for habit in records if records[habit])
                latest_time = max(max(dt.strptime(record[1], "%Y-%m-%d-%H:%M") for record in records[habit]) for habit in records if records[habit])
            except:
                earliest_time = 0
                latest_time = 24
            latest_time_diff = math.ceil((latest_time - earliest_time) / timedelta(hours=1))
            earliest_time = earliest_time.hour

        else:
            id = list(habits.keys())[index % len(habits)]
            raw_records = habits[id]['data']
            on = habits[id]['name']

            # Find periods and analyze the least recorded times
            # Create a count for each hour in a 24-hour format
            hour_counts = [0] * 24
            for record in raw_records:
                start_dt = dt.strptime(record[0], "%Y-%m-%d-%H:%M")
                end_dt = dt.strptime(record[1], "%Y-%m-%d-%H:%M")
                for hour in range(start_dt.hour, end_dt.hour + 1):
                    hour_counts[hour % 24] += 1

            # Find the hour with the least records
            earliest_time = 24 - hour_counts[::-1].index(min(hour_counts))
            latest_time_diff = 24

            records = get_records_from_habits(habits, index)

        window.addstr(6, 5, f"< {on} >", curses.color_pair(1 + (selected[0] == 3)))

        max_length = max(len(habits[habit]['name']) for habit in records) if based_on == "day" else 10
        max_width = window.getmaxyx()[1] - 13 - max_length

        try:
            hour_width = max_width // (latest_time_diff)
        except:
            hour_width = 0
        else:
            hour_widths = [4, 6, 12]
            hour_widths = [width for width in hour_widths if width * (latest_time_diff) <= max_width]
            gaps = [abs(hour_width - width) for width in hour_widths]
            hour_width = hour_widths[gaps.index(min(gaps))]

        for x in range(latest_time_diff + 1):
            window.addstr(8, 7 + max_length + round(hour_width * x), str((earliest_time + x) % 24).rjust(2, "0"))

        for i, record in enumerate(records):
            if based_on == "day":
                window.addstr(9 + i, 5, habits[record]["name"].rjust(max_length), curses.color_pair(1 + (selected[0] == i + 4)))
            else:
                window.addstr(9 + i, 5, record.rjust(max_length), curses.color_pair(1 + (selected[0] == i + 4)))
            count = 0
            for entry in records[record]:
                count += 1
                width = hour_width * ((dt.strptime(entry[1], "%Y-%m-%d-%H:%M").hour - dt.strptime(entry[0], "%Y-%m-%d-%H:%M").hour) % 24)
                message = " " * width if removing != record else f"press {count} to remove this entry, esc to cancel"
                if len(message) > width:
                    message = message[:width-3] + "..."
                window.addstr(9 + i, 8 + max_length + hour_width * ((dt.strptime(entry[0], "%Y-%m-%d-%H:%M").hour - earliest_time) % 24), message, curses.color_pair(2 if removing != record else 7))                     
    else:
        window.addstr(8, 5, "no duration habits!")

def progress_maps(window, selected, map_settings, removing):
    display_borders(window, selected)
    based_on = map_settings['based_on']
    index = map_settings['index']

    window.addstr(2, 5, "progress habits")

    window.addstr(4, 5, "based on: ")
    window.addstr(f"< {based_on} >", curses.color_pair(1 + (selected[0] == 2)))

    habits = Habit.load_habits()
    habits = {habit: habits[habit] for habit in habits if habits[habit]['type'] == "progress"}

    if habits:
        if based_on == "day":
            day = date.today() + timedelta(days=index)
            on = day.strftime("%Y-%m-%d")
            try:
                records = {habit: habits[habit]['data'][on] for habit in habits}
            except:
                for habit in habits:
                    if on not in habits[habit]['data']:
                        habits[habit]['data'][on] = 0
                records = {habit: habits[habit]['data'][on] for habit in habits}
        else:
            id = list(habits.keys())[index % len(habits)]
            records = habits[id]['data']
            on = habits[id]['name']

        window.addstr(6, 5, f"< {on} >", curses.color_pair(1 + (selected[0] == 3)))

        max_length = max(len(habits[habit]['name']) for habit in records) if based_on == "day" else 10
        max_width = window.getmaxyx()[1] - 20 - max_length

        interval = max_width // 10
        for x in range(interval + 1):
            window.addstr(8, 7 + max_length + round(max_width * (x / interval)), str(round(x / interval * 100)).rjust(2, "0"))

        for i, (key, value) in enumerate(records.items()):
            if based_on == "day":
                id = key
                key = habits[key]['name']
                target = habits[id]['target_value']
            else:
                target = habits[key]['target_value']
            window.addstr(9 + i, 5, key.rjust(max_length), curses.color_pair(1 + (selected[0] == i + 4)))
            removing_this = (based_on == "day" and removing == id) or (based_on == "habit" and removing == key)
            if removing_this:
                window.addstr(9 + i, 8 + max_length, "press 0 to remove this date, esc to cancel", curses.color_pair(7))
            window.addstr(9 + i, 8 + max_length, " " * max_width, curses.color_pair(2 if not removing_this else 7))
            window.addstr(f"{round(value / target * 100, 2):.2f}%".rjust(10))
    else:
        window.addstr(8, 5, "no progress habits!")

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
