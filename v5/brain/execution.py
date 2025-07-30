from v5.action_schema import ACTIONS
from v5.services.google_calendar import GoogleCalendarService
from v5.services.notes_service import NotesService

calendar_service = GoogleCalendarService()
notes_service = NotesService()

def format_list_natural(items):
    if not items:
        return ''
    if len(items) == 1:
        return items[0]
    return ', '.join(items[:-1]) + f', and {items[-1]}'

def format_event_time(dt):
    # If minute is 00, drop :00
    if dt.minute == 0:
        return dt.strftime('%-I %p') if hasattr(dt, 'strftime') else dt.strftime('%I %p').lstrip('0')
    else:
        return dt.strftime('%-I:%M %p') if hasattr(dt, 'strftime') else dt.strftime('%I:%M %p').lstrip('0')

def format_event_date(dt):
    return dt.strftime('%A, %B %d, %Y')

def format_event(event):
    if event.location:
        return f"{event.title} at {format_event_time(event.start_time)} in {event.location}"
    else:
        return f"{event.title} at {format_event_time(event.start_time)}"

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
            return f"I've created an event called '{title}' for {start_time}."
        else:
            return "Sorry, I couldn't create that event."
    elif action_name == "get_events":
        # Default to today's events if no args or no date filter is provided
        if not args or not any(k in args for k in ["date", "upcoming_only", "remaining_today", "next_single", "limit"]):
            args = {"date": "today"}
        events = calendar_service.get_events(args)
        if not events:
            return "You have no events scheduled."
        # Natural summary
        if args.get('date') == 'today':
            day_str = 'today'
        elif args.get('date') == 'tomorrow':
            day_str = 'tomorrow'
        else:
            day_str = ''
        event_strs = [format_event(e) for e in events]
        if len(events) == 1:
            return f"You have 1 event {day_str}. {event_strs[0]}."
        else:
            return f"You have {len(events)} events {day_str}. {format_list_natural(event_strs)}."
    elif action_name == "create_note":
        title = args.get("title")
        content = args.get("content")
        note = notes_service.create_note(title, content)
        if note:
            return f"I've created a note titled '{title}'."
        else:
            return "Sorry, I couldn't create that note."
    elif action_name == "read_note":
        title = args.get("title")
        note = notes_service.get_note_by_title(title)
        if note:
            return f"Here's your note titled '{title}." + (f" {note.content}" if note.content else "")
        else:
            return f"I couldn't find a note titled '{title}'."
    elif action_name == "edit_note":
        title = args.get("title")
        content = args.get("content")
        success = notes_service.edit_note(title, content)
        if success:
            return f"I've updated your note titled '{title}'."
        else:
            return f"Sorry, I couldn't update your note titled '{title}'."
    elif action_name == "delete_note":
        title = args.get("title")
        success = notes_service.delete_note_by_title(title)
        if success:
            return f"I've deleted your note titled '{title}'."
        else:
            return f"Sorry, I couldn't delete your note titled '{title}'."
    elif action_name == "list_notes":
        notes = notes_service.get_all_notes()
        if not notes:
            return "You don't have any notes yet."
        note_titles = [note.title for note in notes]
        if len(notes) == 1:
            return f"1. {note_titles[0]}"
        else:
            # Return numbered list for easier parsing
            numbered_list = "\n".join([f"{i+1}. {title}" for i, title in enumerate(note_titles)])
            return numbered_list
    elif action_name == "add_todo":
        item = args.get("item")
        success = notes_service.add_todo_item(item)
        if success:
            return f"I've added '{item}' to your to-do list."
        else:
            return "Sorry, I couldn't add that item to your to-do list."
    elif action_name == "show_todo":
        todo_note = notes_service.get_or_create_todo_note()
        if not todo_note.content.strip():
            return "Your to-do list is empty."
        # Return the numbered todo list as-is
        return todo_note.content.strip()
    elif action_name == "clear_todo":
        success = notes_service.clear_todo_list()
        if success:
            return "I've cleared your to-do list."
        else:
            return "Sorry, I couldn't clear your to-do list."
    elif action_name == "remove_todo_item":
        item_number = args.get("item_number")
        success = notes_service.remove_todo_item(item_number)
        if success:
            return f"I've removed item {item_number} from your to-do list."
        else:
            return f"Sorry, I couldn't remove item {item_number} from your to-do list."
    elif action_name == "get_time":
        from datetime import datetime
        now = datetime.now()
        if now.minute == 0:
            time_str = now.strftime('%-I %p') if hasattr(now, 'strftime') else now.strftime('%I %p').lstrip('0')
        else:
            time_str = now.strftime('%-I:%M %p') if hasattr(now, 'strftime') else now.strftime('%I:%M %p').lstrip('0')
        return f"It is {time_str}."
    elif action_name == "get_date":
        from datetime import datetime
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    elif action_name == "get_day":
        from datetime import datetime
        return f"It's {datetime.now().strftime('%A')}."
    elif action_name == "greeting":
        return "Hello! How can I help you today?"
    else:
        return "Sorry, I don't know how to do that yet." 