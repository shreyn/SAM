#!/usr/bin/env python3
"""
SAM Brain - Main orchestrator for the SAM assistant
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .intent_classifier import IntentClassifier, IntentResult
from .task_state import TaskState
from .action_registry import ActionRegistry
from services.google_calendar import GoogleCalendarService, CalendarEvent
from services.notes_service import NotesService, Note

class SAMBrain:
    """Main brain that orchestrates intent classification, task state, and actions"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.action_registry = ActionRegistry()
        self.calendar_service = GoogleCalendarService()
        self.notes_service = NotesService()
        self.task_state = TaskState()
        
        # Initialize LLM for fallback responses
        from services.lightweight_llm import LightweightLLM
        self.llm = LightweightLLM(mock_mode=False)
        
        # Confidence thresholds
        self.high_confidence_threshold = 0.8
        self.low_confidence_threshold = 0.5
    
    def process_message(self, message: str) -> str:
        """Process a user message and return a response"""
        message = message.strip()
        
        # Check if this is a follow-up to an existing task
        if self.task_state.current_action and not self.task_state.is_complete():
            return self._handle_follow_up(message)
        
        # Classify the intent
        intent_result = self.intent_classifier.classify(message)
        
        # Handle unknown intents
        if intent_result.intent_type == 'UNKNOWN':
            return self._handle_unknown_intent(message)
        
        # Handle greetings
        if intent_result.intent_type == 'GREETING':
            return self._handle_greeting()
        
        # Start new task
        return self._start_new_task(intent_result, message)
    
    def _start_new_task(self, intent_result: IntentResult, message: str) -> str:
        """Start a new task"""
        action_name = intent_result.action
        
        # Get required arguments for this action
        required_args = self.action_registry.get_required_args(action_name)
        
        # Start new task state
        self.task_state.start_new_task(
            action=action_name,
            intent_type=intent_result.intent_type,
            confidence=intent_result.confidence,
            required_args=required_args,
            initial_args=intent_result.args
        )
        
        # Check if we have all required arguments
        if self.task_state.is_complete():
            return self._execute_action()
        else:
            # Ask for missing arguments
            return self._ask_for_missing_args()
    
    def _handle_follow_up(self, message: str) -> str:
        """Handle follow-up messages to collect missing arguments"""
        # Mark this as a follow-up
        self.task_state.add_follow_up(message)
        
        # Extract arguments from the follow-up message
        extracted_args = self._extract_args_from_follow_up(message)
        
        if extracted_args:
            # Update task state with new arguments
            self.task_state.update_args(extracted_args)
            
            # Check if we now have all required arguments
            if self.task_state.is_complete():
                return self._execute_action()
            else:
                # Ask for next missing argument
                return self._ask_for_missing_args()
        else:
            # Couldn't extract arguments, ask again
            return self._ask_for_missing_args()
    
    def _extract_args_from_follow_up(self, message: str) -> Dict[str, Any]:
        """Extract arguments from a follow-up message"""
        args = {}
        message_lower = message.lower().strip()
        
        # Extract based on current action
        if self.task_state.current_action == 'create_event':
            # Extract title
            if not self.task_state.collected_args.get('title'):
                title = self._extract_title_from_follow_up(message)
                if title:
                    args['title'] = title
            
            # Extract start_time
            if not self.task_state.collected_args.get('start_time'):
                time_info = self._extract_time_from_follow_up(message)
                if time_info:
                    args['start_time'] = time_info
            
            # If no specific extraction worked, try to infer based on missing args
            if not args:
                missing_args = self.task_state.missing_args
                if 'title' in missing_args and not any(word in message_lower for word in ['at', 'pm', 'am', ':', 'today', 'tomorrow', 'tonight']):
                    # If message doesn't contain time-related words, treat as title
                    args['title'] = message.strip()
                elif 'start_time' in missing_args:
                    # If we're missing time, try to extract it
                    time_info = self._extract_time_from_follow_up(message)
                    if time_info:
                        args['start_time'] = time_info
        
        elif self.task_state.current_action == 'create_note':
            # Extract title
            if not self.task_state.collected_args.get('title'):
                title = self._extract_note_title_from_follow_up(message)
                if title:
                    args['title'] = title
            
            # Extract content
            if not self.task_state.collected_args.get('content'):
                content = self._extract_note_content_from_follow_up(message)
                if content:
                    args['content'] = content
            
            # If no specific extraction worked, try to infer based on missing args
            if not args:
                missing_args = self.task_state.missing_args
                if 'content' in missing_args:
                    # If we're missing content, treat the message as content
                    args['content'] = message.strip()
                elif 'title' in missing_args:
                    # If we're missing title, treat the message as title
                    args['title'] = message.strip()
        
        elif self.task_state.current_action == 'read_note':
            # Extract title
            if not self.task_state.collected_args.get('title'):
                title = self._extract_note_title_from_follow_up(message)
                if title:
                    args['title'] = title
            
            # If no specific extraction worked, treat the message as title
            if not args:
                args['title'] = message.strip()
        
        elif self.task_state.current_action == 'edit_note':
            # Extract title
            if not self.task_state.collected_args.get('title'):
                title = self._extract_note_title_from_follow_up(message)
                if title:
                    args['title'] = title
            
            # Extract content
            if not self.task_state.collected_args.get('content'):
                content = self._extract_note_content_from_follow_up(message)
                if content:
                    args['content'] = content
            
            # If no specific extraction worked, try to infer based on missing args
            if not args:
                missing_args = self.task_state.missing_args
                if 'content' in missing_args:
                    # If we're missing content, treat the message as content
                    args['content'] = message.strip()
                elif 'title' in missing_args:
                    # If we're missing title, treat the message as title
                    args['title'] = message.strip()
        
        elif self.task_state.current_action == 'delete_note':
            # Extract title
            if not self.task_state.collected_args.get('title'):
                title = self._extract_note_title_from_follow_up(message)
                if title:
                    args['title'] = title
            
            # If no specific extraction worked, treat the message as title
            if not args:
                args['title'] = message.strip()
        
        elif self.task_state.current_action == 'add_todo':
            # Extract item
            if not self.task_state.collected_args.get('item'):
                args['item'] = message.strip()
        
        return args
    
    def _extract_title_from_follow_up(self, message: str) -> Optional[str]:
        """Extract event title from follow-up message"""
        # Simple extraction - look for quoted text or key phrases
        patterns = [
            r'"([^"]+)"',  # Quoted text
            r'called\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:at|on|for|meeting|event|appointment))?',
            r'named\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:at|on|for|meeting|event|appointment))?',
            r'for\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:at|on|for|meeting|event|appointment))?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if title and title not in ['a', 'an', 'the', 'event', 'appointment', 'meeting']:
                    return title
        
        # If no pattern matches, try to extract meaningful words
        words = message.split()
        if len(words) <= 5:  # Short message, likely just the title
            return message.strip()
        
        return None
    
    def _extract_time_from_follow_up(self, message: str) -> Optional[str]:
        """Extract time information from follow-up message using centralized parser"""
        from utils.time_parser import extract_time_info
        return extract_time_info(message)
    
    def _extract_note_title_from_follow_up(self, message: str) -> Optional[str]:
        """Extract note title from follow-up message"""
        # Simple extraction - look for quoted text or key phrases
        patterns = [
            r'"([^"]+)"',  # Quoted text
            r'called\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:about|with|for|note|memo))?',
            r'named\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:about|with|for|note|memo))?',
            r'titled\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:about|with|for|note|memo))?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if title and title not in ['a', 'an', 'the', 'note', 'memo']:
                    return title
        
        # If no pattern matches, try to extract meaningful words
        words = message.split()
        if len(words) <= 5:  # Short message, likely just the title
            return message.strip()
        
        return None
    
    def _extract_note_content_from_follow_up(self, message: str) -> Optional[str]:
        """Extract note content from follow-up message"""
        # If message is longer than a few words, treat as content
        if len(message.split()) > 3:
            return message.strip()
        
        return None
    
    def _ask_for_missing_args(self) -> str:
        """Ask for the next missing argument"""
        next_arg = self.task_state.get_next_missing_arg()
        if next_arg:
            question = self.task_state.get_follow_up_question()
            return question
        else:
            return "I'm not sure what information I need. Could you please provide more details?"
    
    def _execute_action(self) -> str:
        """Execute the current action with collected arguments"""
        action_name = self.task_state.current_action
        args = self.task_state.collected_args
        
        try:
            if action_name == 'create_event':
                return self._execute_create_event(args)
            elif action_name == 'get_events':
                return self._execute_get_events(args)
            elif action_name == 'get_time':
                return self._execute_get_time(args)
            elif action_name == 'get_date':
                return self._execute_get_date(args)
            elif action_name == 'get_day':
                return self._execute_get_day(args)
            elif action_name == 'create_note':
                return self._execute_create_note(args)
            elif action_name == 'read_note':
                return self._execute_read_note(args)
            elif action_name == 'edit_note':
                return self._execute_edit_note(args)
            elif action_name == 'delete_note':
                return self._execute_delete_note(args)
            elif action_name == 'list_notes':
                return self._execute_list_notes(args)
            elif action_name == 'add_todo':
                return self._execute_add_todo(args)
            elif action_name == 'show_todo':
                return self._execute_show_todo(args)
            elif action_name == 'clear_todo':
                return self._execute_clear_todo(args)
            elif action_name == 'remove_todo_item':
                return self._execute_remove_todo_item(args)
            elif action_name == 'greeting':
                return self._execute_greeting(args)
            else:
                return f"I'm not sure how to handle the action '{action_name}'."
        
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
        finally:
            # Reset task state after execution
            self.task_state.reset()
    
    def _execute_create_event(self, args: Dict[str, Any]) -> str:
        """Execute create_event action"""
        title = args.get('title', 'Untitled Event')
        start_time = args.get('start_time', 'now')
        
        # Create the event in Google Calendar
        success = self.calendar_service.create_event(
            title=title,
            start_time=start_time,
            description=args.get('description'),
            location=args.get('location')
        )
        
        if success:
            # Parse the time to get a formatted version for the response
            from utils.time_parser import parse_datetime, format_datetime
            try:
                parsed_time = parse_datetime(start_time)
                formatted_time = format_datetime(parsed_time, 'event_display')
                return f"I have created the event '{title}' at {formatted_time}."
            except:
                # Fallback if time parsing fails
                return f"I have created the event '{title}'."
        else:
            return "❌ Sorry, I couldn't create the event. Please try again."
    
    def _execute_get_events(self, args: Dict[str, Any]) -> str:
        """Execute get_events action"""
        events = self.calendar_service.get_events(args)
        
        if not events:
            # Generate appropriate message based on filters
            if args.get('next_single') and args.get('remaining_today'):
                return "You have no more events for the rest of the day."
            elif args.get('remaining_today'):
                return "You have no more events scheduled for today."
            elif args.get('date') == 'today':
                return "You have no events scheduled for today."
            elif args.get('date') == 'tomorrow':
                return "You have no events scheduled for tomorrow."
            elif args.get('upcoming_only'):
                return "You have no upcoming events."
            else:
                return "You have no events scheduled."
        
        # Format events for display using centralized formatter
        from utils.time_parser import format_datetime
        
        if len(events) >= 1 and args.get('next_single'):
            event = events[0]
            formatted_time = format_datetime(event.start_time, 'event_display')
            return f"Your next event is '{event.title}' on {formatted_time}."
        elif len(events) == 1:
            event = events[0]
            formatted_time = format_datetime(event.start_time, 'event_display')
            return f"You have 1 event: '{event.title}' on {formatted_time}."
        else:
            event_list = []
            for event in events:
                formatted_time = format_datetime(event.start_time, 'event_display')
                event_list.append(f"'{event.title}' on {formatted_time}")
            # Generate appropriate header based on filter type
            if args.get('next_single'):
                header = f"Your next event is:"
            elif args.get('remaining_today'):
                header = f"You have {len(events)} remaining events today:"
            elif args.get('date') == 'today':
                header = f"You have {len(events)} events today:"
            elif args.get('date') == 'tomorrow':
                header = f"You have {len(events)} events tomorrow:"
            else:
                header = f"You have {len(events)} events:"
            return f"{header}\n" + "\n".join(f"• {event}" for event in event_list)
    
    def _execute_get_time(self, args: Dict[str, Any]) -> str:
        """Execute get_time action"""
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."
    
    def _execute_get_date(self, args: Dict[str, Any]) -> str:
        """Execute get_date action"""
        now = datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}."
    
    def _execute_get_day(self, args: Dict[str, Any]) -> str:
        """Execute get_day action"""
        from utils.time_parser import parse_datetime, format_datetime
        
        # Check if user is asking about a specific date (like tomorrow)
        target_date = args.get('target_date')
        if target_date == 'tomorrow':
            tomorrow = datetime.now() + timedelta(days=1)
            day_name = format_datetime(tomorrow, 'day_only')
            return f"Tomorrow is {day_name}."
        else:
            # Default to today
            now = datetime.now()
            day_name = format_datetime(now, 'day_only')
            return f"Today is {day_name}."
    
    def _execute_greeting(self, args: Dict[str, Any]) -> str:
        """Execute greeting action"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good morning! How can I help you today?"
        elif 12 <= hour < 17:
            return "Good afternoon! How can I help you today?"
        elif 17 <= hour < 21:
            return "Good evening! How can I help you today?"
        else:
            return "Hello! How can I help you today?"
    
    def _handle_unknown_intent(self, message: str) -> str:
        """Handle unknown intents by falling back to LLM for a short response"""
        try:
            # Use LLM to generate a short, helpful response
            response = self.llm.generate_general_response(message)
            return response
        except Exception as e:
            # Fallback to generic message if LLM fails
            return "I'm not sure how to help with that. Could you try rephrasing your request?"
    
    def _handle_greeting(self) -> str:
        """Handle greetings"""
        return self._execute_greeting({})
    
    def get_task_state(self) -> Dict[str, Any]:
        """Get current task state for debugging"""
        return self.task_state.to_dict()
    
    def reset_task_state(self):
        """Reset the task state"""
        self.task_state.reset()
    
    def _execute_create_note(self, args: Dict[str, Any]) -> str:
        """Execute create_note action"""
        title = args.get('title', '')
        content = args.get('content', '')
        
        if not title:
            return "❌ Note title is required. Please provide a title for your note."
        
        if not content:
            return "❌ Note content is required. Please provide the content for your note."
        
        # Create the note
        note = self.notes_service.create_note(
            title=title,
            content=content
        )
        
        if note:
            return f"The note '{note.title}' has been created."
        else:
            return "❌ Sorry, I couldn't create the note. Please try again."
    
    def _execute_read_note(self, args: Dict[str, Any]) -> str:
        """Execute read_note action"""
        title = args.get('title', '')
        
        if not title:
            return "❌ Note title is required. Please provide the title of the note you want to read."
        
        # Get the note by title
        note = self.notes_service.get_note_by_title(title)
        
        if not note:
            return f"❌ Note '{title}' not found."
        
        return f"The note '{note.title}' says: {note.content}"
    
    def _execute_edit_note(self, args: Dict[str, Any]) -> str:
        """Execute edit_note action"""
        title = args.get('title', '')
        content = args.get('content', '')
        
        if not title:
            return "❌ Note title is required. Please provide the title of the note you want to edit."
        
        if not content:
            return "❌ New content is required. Please provide the new content for the note."
        
        # Check if note exists
        note = self.notes_service.get_note_by_title(title)
        if not note:
            return f"❌ Note '{title}' not found."
        
        # Edit the note
        success = self.notes_service.edit_note(title, content)
        
        if success:
            return f"The note '{title}' has been edited."
        else:
            return "❌ Sorry, I couldn't update the note. Please try again."
    
    def _execute_delete_note(self, args: Dict[str, Any]) -> str:
        """Execute delete_note action"""
        title = args.get('title', '')
        
        if not title:
            return "❌ Note title is required. Please provide the title of the note you want to delete."
        
        # Check if note exists
        note = self.notes_service.get_note_by_title(title)
        if not note:
            return f"❌ Note '{title}' not found."
        
        # Delete the note
        success = self.notes_service.delete_note_by_title(title)
        
        if success:
            return f"I deleted the note '{title}'."
        else:
            return "❌ Sorry, I couldn't delete the note. Please try again."
    
    def _execute_list_notes(self, args: Dict[str, Any]) -> str:
        """Execute list_notes action"""
        limit = args.get('limit')
        # Get all notes
        notes = self.notes_service.get_all_notes()
        if not notes:
            return "You have no notes yet."
        # Apply limit if specified
        if limit and isinstance(limit, int) and limit > 0:
            notes = notes[:limit]
        # Format the response
        if limit:
            header = f"Your {len(notes)} most recent notes:"
        else:
            header = f"You have {len(notes)} total notes."
        formatted_notes = self.notes_service.format_notes_list(notes)
        return f"{header}\n{formatted_notes}"
    
    def _execute_add_todo(self, args: Dict[str, Any]) -> str:
        """Execute add_todo action"""
        item = args.get('item', '')
        
        if not item:
            return "❌ Todo item is required. Please provide what you want to add to your todo list."
        
        # Add the item to the todo list
        success = self.notes_service.add_todo_item(item)
        
        if success:
            return f"✅ Added '{item}' to your todo list."
        else:
            return "❌ Sorry, I couldn't add the item to your todo list. Please try again."
    
    def _execute_show_todo(self, args: Dict[str, Any]) -> str:
        """Execute show_todo action"""
        todo_note = self.notes_service.get_or_create_todo_note()
        if not todo_note.content.strip():
            return "You have no items in your to do list."
        return f"Your todo list:\n{todo_note.content}"
    
    def _execute_clear_todo(self, args: Dict[str, Any]) -> str:
        """Execute clear_todo action"""
        # Clear the todo list
        success = self.notes_service.clear_todo_list()
        
        if success:
            return "✅ Your todo list has been cleared."
        else:
            return "❌ Sorry, I couldn't clear your todo list. Please try again."
    
    def _execute_remove_todo_item(self, args: Dict[str, Any]) -> str:
        """Execute remove_todo_item action"""
        item_number = args.get('item_number')
        
        if not item_number:
            return "❌ Item number is required. Please specify which item to remove."
        
        # Remove the item from the todo list
        success = self.notes_service.remove_todo_item(item_number)
        
        if success:
            return f"✅ Removed item {item_number} from your todo list."
        else:
            return f"❌ Sorry, I couldn't remove item {item_number} from your todo list. Please try again." 