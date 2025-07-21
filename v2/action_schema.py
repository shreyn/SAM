#!/usr/bin/env python3
"""
Action Registry - Defines actions and their required/optional arguments
"""

ACTIONS = {
    "create_event": {
        "description": "Create a new calendar event",
        "required_args": ["title", "start_time"],
        "optional_args": ["duration", "description", "location", "date"]
    },
    "get_events": {
        "description": "Get calendar events",
        "required_args": [],
        "optional_args": ["date", "upcoming_only", "limit"]
    },
    "get_time": {
        "description": "Get current time",
        "required_args": [],
        "optional_args": ["timezone"]
    },
    "get_date": {
        "description": "Get current date",
        "required_args": [],
        "optional_args": ["format", "timezone"]
    },
    "get_day": {
        "description": "Get current day of week",
        "required_args": [],
        "optional_args": ["timezone"]
    },
    "create_task": {
        "description": "Create a new task",
        "required_args": ["title"],
        "optional_args": ["due_date", "priority", "description"]
    },
    "create_note": {
        "description": "Create a new note",
        "required_args": ["title", "content"],
        "optional_args": []
    },
    "read_note": {
        "description": "Read a specific note by title",
        "required_args": ["title"],
        "optional_args": []
    },
    "edit_note": {
        "description": "Edit a note's content",
        "required_args": ["title", "content"],
        "optional_args": []
    },
    "delete_note": {
        "description": "Delete a note",
        "required_args": ["title"],
        "optional_args": []
    },
    "list_notes": {
        "description": "List all notes",
        "required_args": [],
        "optional_args": ["limit"]
    },
    "add_todo": {
        "description": "Add item to todo list",
        "required_args": ["item"],
        "optional_args": []
    },
    "show_todo": {
        "description": "Show todo list",
        "required_args": [],
        "optional_args": []
    },
    "clear_todo": {
        "description": "Clear todo list",
        "required_args": [],
        "optional_args": []
    },
    "remove_todo_item": {
        "description": "Remove item from todo list",
        "required_args": ["item_number"],
        "optional_args": []
    },
    "greeting": {
        "description": "Handle greetings",
        "required_args": [],
        "optional_args": []
    },
    "unknown": {
        "description": "Handle unknown intents",
        "required_args": [],
        "optional_args": []
    }
}
