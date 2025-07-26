from v4.action_schema import ACTIONS
from v4.services.google_calendar import GoogleCalendarService
from v4.services.notes_service import NotesService

calendar_service = GoogleCalendarService()
notes_service = NotesService()

def execute_action(action_name, args):
    """
    Execute the given action with the provided arguments using the appropriate service.
    Returns a confirmation message or result string.
    """
    if action_name == "create_event":
        title = args.get("title")
        start_time = args.get("start_time")
        description = args.get("description")
        location = args.get("location")
        success = calendar_service.create_event(title, start_time, description, location)
        if success:
            return f"Event '{title}' created for {start_time}."
        else:
            return "Failed to create event."
    elif action_name == "get_events":
        # Default to today's events if no args or no date filter is provided
        if not args or not any(k in args for k in ["date", "upcoming_only", "remaining_today", "next_single", "limit"]):
            args = {"date": "today"}
        events = calendar_service.get_events(args)
        if not events:
            return "No events found."
        return "\n".join([f"{e.title} at {e.start_time}" for e in events])
    elif action_name == "create_note":
        title = args.get("title")
        content = args.get("content")
        note = notes_service.create_note(title, content)
        if note:
            return f"Note '{title}' created."
        else:
            return "Failed to create note."
    elif action_name == "read_note":
        title = args.get("title")
        note = notes_service.get_note_by_title(title)
        if note:
            return f"Note '{title}': {note.content}"
        else:
            return f"Note '{title}' not found."
    elif action_name == "edit_note":
        title = args.get("title")
        content = args.get("content")
        success = notes_service.edit_note(title, content)
        if success:
            return f"Note '{title}' updated."
        else:
            return f"Failed to update note '{title}'."
    elif action_name == "delete_note":
        title = args.get("title")
        success = notes_service.delete_note_by_title(title)
        if success:
            return f"Note '{title}' deleted."
        else:
            return f"Failed to delete note '{title}'."
    elif action_name == "list_notes":
        notes = notes_service.get_all_notes()
        if not notes:
            return "No notes found."
        return notes_service.format_notes_list(notes)
    elif action_name == "add_todo":
        item = args.get("item")
        success = notes_service.add_todo_item(item)
        if success:
            return f"Added '{item}' to your todo list."
        else:
            return "Failed to add item to todo list."
    elif action_name == "show_todo":
        todo_note = notes_service.get_or_create_todo_note()
        if not todo_note.content.strip():
            return "Your todo list is empty."
        return f"Your todo list:\n{todo_note.content}"
    elif action_name == "clear_todo":
        success = notes_service.clear_todo_list()
        if success:
            return "Todo list cleared."
        else:
            return "Failed to clear todo list."
    elif action_name == "remove_todo_item":
        item_number = args.get("item_number")
        success = notes_service.remove_todo_item(item_number)
        if success:
            return f"Removed item {item_number} from your todo list."
        else:
            return f"Failed to remove item {item_number} from your todo list."
    elif action_name == "get_time":
        from datetime import datetime
        return f"{datetime.now().strftime('%I:%M %p')}"
    elif action_name == "get_date":
        from datetime import datetime
        return f"{datetime.now().strftime('%A, %B %d, %Y')}"
    elif action_name == "get_day":
        from datetime import datetime
        return f"{datetime.now().strftime('%A')}"
    elif action_name == "greeting":
        return "Hello! How can I help you today?"
    else:
        return f"Action '{action_name}' is not implemented." 