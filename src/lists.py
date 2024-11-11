import os
import uuid
from misc import load_items, save_items

class List:
    def __init__(self, name, description="", items=[]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.items = items

    @staticmethod
    def load_lists(filename=os.path.join(os.path.expanduser("~"), ".dots", "lists.json")):
        return load_items(filename)

    @staticmethod
    def save_lists(lists, filename=os.path.join(os.path.expanduser("~"), ".dots", "lists.json")):
        save_items(lists, filename)

    @classmethod
    def add_list(cls, name):
        """Create a new list and add it to the lists dictionary."""
        list = cls(name)
        lists = cls.load_lists()  # Load existing lists
        lists[list.id] = vars(list)  # Add list to the dictionary
        cls.save_lists(lists)  # Save updated lists to JSON
        return list.id  # Return the ID of the new list

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
        return lists[list_id]  # Return the list if it exists, else None
