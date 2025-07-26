#!/usr/bin/env python3
"""
Action Registry - Defines actions and their required/optional arguments
"""

ACTIONS = {
    "create_event": {
        "description": "Create a new calendar event with a specific title and start time. Optionally include duration, description, location, or date.",
        "required_args": ["title", "start_time"],
        "optional_args": ["duration", "description", "location", "date"]
    },
    "get_events": {
        "description": "Show the user's calendar events, optionally filtered by date, upcoming only, or a limit on the number of events.",
        "required_args": [],
        "optional_args": ["date", "upcoming_only", "limit"]
    },
    "get_time": {
        "description": "Tell the user the current time.",
        "required_args": [],
        "optional_args": []
    },
    "get_date": {
        "description": "Tell the user today's date.",
        "required_args": [],
        "optional_args": []
    },
    "get_day": {
        "description": "Tell the user the current day of the week.",
        "required_args": [],
        "optional_args": []
    },
    "create_note": {
        "description": "Create a new note with a specific title and content. Notes are for storing information, ideas, or reminders that are not part of your todo list.",
        "required_args": ["title", "content"],
        "optional_args": []
    },
    "read_note": {
        "description": "Display the content of a specific note by its title.",
        "required_args": ["title"],
        "optional_args": []
    },
    "edit_note": {
        "description": "Edit the content of an existing personal note, identified by its title. Notes are for information, not tasks.",
        "required_args": ["title", "content"],
        "optional_args": []
    },
    "delete_note": {
        "description": "Delete a personal note from your collection, identified by its title. Notes are not your todo list.",
        "required_args": ["title"],
        "optional_args": []
    },
    "list_notes": {
        "description": "List all personal notes you have created, optionally limiting the number shown. Notes are separate from your todo list.",
        "required_args": [],
        "optional_args": []
    },
    "add_todo": {
        "description": "Add a new task or item to your todo list. The todo list is for things you need to do, not for storing general notes.",
        "required_args": ["item"],
        "optional_args": []
    },
    "show_todo": {
        "description": "Show your current todo list. Use this to see your todo list, not your notes.",
        "required_args": [],
        "optional_args": []
    },
    "clear_todo": {
        "description": "Clear all tasks and items from your todo list. This does not affect your notes.",
        "required_args": [],
        "optional_args": []
    },
    "remove_todo_item": {
        "description": "Remove a specific task or item from your todo list by its number. This does not affect your notes.",
        "required_args": ["item_number"],
        "optional_args": []
    },
    "greeting": {
        "description": "Respond to greetings or friendly messages from the user.",
        "required_args": [],
        "optional_args": []
    },
    "unknown": {
        "description": "Handle user requests that do not match any known action or intent.",
        "required_args": [],
        "optional_args": []
    }
}
