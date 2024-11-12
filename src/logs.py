import curses
import os
import uuid
from misc import display_borders, load_items, save_items, open_editor_and_return_text
from datetime import date 

class Log:
    def __init__(self, name, description="", entries={}):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.entries = entries  # entries will be a dict in the format {date: markdown_content}

    @staticmethod
    def load_logs(filename=os.path.join(os.path.expanduser("~"), ".dots", "logs.json")):
        return load_items(filename)

    @staticmethod
    def save_logs(logs, filename=os.path.join(os.path.expanduser("~"), ".dots", "logs.json")):
        save_items(logs, filename)

    @classmethod
    def add_log(cls, name):
        """Create a new log and add it to the logs dictionary."""
        log_instance = cls(name)
        logs = cls.load_logs()  # Load existing logs
        logs[log_instance.id] = vars(log_instance)  # Add log to the dictionary
        cls.save_logs(logs)  # Save updated logs to JSON
        return log_instance.id  # Return the ID of the new log

    @classmethod
    def edit_log(cls, log_id, **kwargs):
        """Edit an existing log's attributes."""
        logs = cls.load_logs()  # Load existing logs
        log_id = str(log_id)
        if log_id in logs:  # Check if log exists
            log_data = logs[log_id]  # Get log data
            # Update log attributes based on provided kwargs
            for key, value in kwargs.items():
                if key in log_data:
                    log_data[key] = value
            logs[log_id] = log_data  # Update the log in the dictionary
            cls.save_logs(logs)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if log not found

    @classmethod
    def remove_log(cls, log_id):
        """Remove a log by its ID."""
        logs = cls.load_logs()  # Load existing logs
        if log_id in logs:  # Check if log exists
            del logs[log_id]  # Remove the log from the dictionary
            cls.save_logs(logs)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if log not found

    @classmethod
    def get_log(cls, log_id):
        """Get a log by its ID."""
        logs = cls.load_logs()  # Load existing logs
        return logs.get(log_id)  # Return the log if it exists, else None

    @classmethod
    def add_entry(cls, log_id, window, date=str(date.today()), markdown=""):
        """Add a new entry to a specific log."""
        logs = cls.load_logs()
        if log_id in logs:
            markdown_content = open_editor_and_return_text(window) if not markdown else markdown
            logs[log_id]["entries"][date] = markdown_content  # Add new entry to the dictionary
            cls.save_logs(logs)  # Save changes to JSON
            return date  # Return the date of the new entry
        return None  # Return None if log ID not found

    @classmethod
    def edit_entry(cls, log_id, window, date, markdown=""):
        """Edit an entry within a specific log."""
        logs = cls.load_logs()
        if log_id in logs and date in logs[log_id]["entries"]:
            markdown_content = open_editor_and_return_text(window) if not markdown else markdown
            logs[log_id]["entries"][date] = markdown_content  # Save changes to the specific entry
            cls.save_logs(logs)  # Save changes to JSON
            return True  # Return success if entry updated
        return False  # Return failure if entry or log ID not found

    @classmethod
    def remove_entry(cls, log_id, date):
        """Remove an entry from a specific log."""
        logs = cls.load_logs()
        if log_id in logs and date in logs[log_id]["entries"]:
            del logs[log_id]["entries"][date]  # Remove the entry by date
            cls.save_logs(logs)  # Save changes to JSON
            return True  # Return success if entry removed
        return False  # Return failure if entry or log ID not found

def add_new_log(window, selected):
    display_borders(window, selected)
    window.addstr(1, 2, "+ press : to add a new log.", curses.color_pair(4 + (selected[0] == 2)))

def view_log(window, inner_option, selected, removing):
    display_borders(window, selected)
    logs = Log.load_logs()
    entries = Log.get_log(list(logs.keys())[inner_option])["entries"]

    for i, date in enumerate(entries):
        if removing == date:
            window.addstr(i + 1, 2, f"• press r to confirm removal, esc to cancel", curses.color_pair(7))
        else:
            window.addstr(i + 1, 2, f"• {date}", curses.color_pair(1 + (selected[0] == i + 2)))

    if removing == ".":
        window.addstr(len(entries) + 1, 2, "+ press r to confirm removal, esc to cancel", curses.color_pair(7))
    else:
        window.addstr(len(entries) + 1, 2, "+ press : to add a new entry, e to change log name, r to remove log.", curses.color_pair(4 + (selected[0] == (len(entries) + 2))))
