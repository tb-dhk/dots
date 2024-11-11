import curses
import os
import uuid
from misc import display_borders, load_items, save_items

class List:
    def __init__(self, name, description="", items={}):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.items = items if items is not None else {}

    @staticmethod
    def load_lists(filename=os.path.join(os.path.expanduser("~"), ".dots", "lists.json")):
        return load_items(filename)

    @staticmethod
    def save_lists(lists, filename=os.path.join(os.path.expanduser("~"), ".dots", "lists.json")):
        save_items(lists, filename)

    @classmethod
    def add_list(cls, name):
        """Create a new list and add it to the lists dictionary."""
        list_instance = cls(name)
        lists = cls.load_lists()  # Load existing lists
        lists[list_instance.id] = vars(list_instance)  # Add list to the dictionary
        cls.save_lists(lists)  # Save updated lists to JSON
        return list_instance.id  # Return the ID of the new list

    @classmethod
    def edit_list(cls, list_id, **kwargs):
        """Edit an existing list's attributes."""
        lists = cls.load_lists()  # Load existing lists
        list_id = str(list_id)
        if list_id in lists:  # Check if list exists
            list_data = lists[list_id]  # Get list data
            # Update list attributes based on provided kwargs
            for key, value in kwargs.items():
                if key in list_data:
                    list_data[key] = value
            lists[list_id] = list_data  # Update the list in the dictionary
            cls.save_lists(lists)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if list not found

    @classmethod
    def remove_list(cls, list_id):
        """Remove a list by its ID."""
        lists = cls.load_lists()  # Load existing lists
        if list_id in lists:  # Check if list exists
            del lists[list_id]  # Remove the list from the dictionary
            cls.save_lists(lists)  # Save changes to JSON
            return True  # Return success
        return False  # Return failure if list not found

    @classmethod
    def get_list(cls, list_id):
        """Get a list by its ID."""
        lists = cls.load_lists()  # Load existing lists
        return lists.get(list_id)  # Return the list if it exists, else None

    @classmethod
    def add_item(cls, list_id, name, description=""):
        """Add a new item to a specific list."""
        lists = cls.load_lists()
        if list_id in lists:
            new_item = ListItem(name, description=description)
            lists[list_id]["items"][new_item.id] = vars(new_item)  # Add new item to the dictionary
            cls.save_lists(lists)  # Save changes to JSON
            return new_item.id  # Return the new item's ID
        return None  # Return None if list ID not found

    @classmethod
    def edit_item(cls, list_id, item_id, **kwargs):
        """Edit an item within a specific list."""
        lists = cls.load_lists()
        if list_id in lists and item_id in lists[list_id]["items"]:
            item_data = lists[list_id]["items"][item_id]
            for key, value in kwargs.items():
                if key in item_data:
                    item_data[key] = value  # Update item attributes
            lists[list_id]["items"][item_id] = item_data  # Save changes to the specific item
            cls.save_lists(lists)  # Save changes to JSON
            return True  # Return success if item updated
        return False  # Return failure if item or list ID not found

    @classmethod
    def remove_item(cls, list_id, item_id):
        """Remove an item from a specific list."""
        lists = cls.load_lists()
        if list_id in lists and item_id in lists[list_id]["items"]:
            del lists[list_id]["items"][item_id]  # Remove the item by ID
            cls.save_lists(lists)  # Save changes to JSON
            return True  # Return success if item removed
        return False  # Return failure if item or list ID not found

class ListItem:
    def __init__(self, name, description="", task=""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.completed = False
        self.description = description
        self.task = task

def add_new_list(window, selected):
    display_borders(window, selected)

    window.addstr(1, 2, "+ press : to add a new list.", curses.color_pair(4 + (selected[0] == 2)))

def view_list(window, inner_option, selected, removing):
    display_borders(window, selected)

    lists = List.load_lists()
    items = List.get_list(list(lists.keys())[inner_option])["items"]

    for i, item in enumerate(items):
        symbol = "x" if items[item]["completed"] else "•"
        if removing == item:
            window.addstr(i + 1, 2, symbol + " press r to confirm removal, esc to cancel", curses.color_pair(7))
        else:
            window.addstr(i + 1, 2, symbol + " " + items[item]["name"], curses.color_pair(1 + (selected[0] == i + 2)))

    if removing == ".":
        window.addstr(len(items) + 1, 2, "+ press r to confirm removal, esc to cancel", curses.color_pair(7))
    else:
        window.addstr(len(items) + 1, 2, "+ press : to add a new item, e to change list name, r to remove list.", curses.color_pair(4 + (selected[0] == (len(items) + 2))))
