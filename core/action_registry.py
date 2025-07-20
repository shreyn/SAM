#!/usr/bin/env python3
"""
Action Registry - Defines actions and their required/optional arguments
"""

from typing import Dict, List, Any, Callable
from dataclasses import dataclass

@dataclass
class ActionDefinition:
    """Definition of an action with its arguments"""
    name: str
    description: str
    required_args: List[str]
    optional_args: List[str]
    handler: Callable = None

class ActionRegistry:
    """Registry for all available actions"""
    
    def __init__(self):
        self.actions: Dict[str, ActionDefinition] = {}
        self._register_default_actions()
    
    def register_action(self, action_def: ActionDefinition):
        """Register a new action"""
        self.actions[action_def.name] = action_def
    
    def get_action(self, action_name: str) -> ActionDefinition:
        """Get action definition by name"""
        return self.actions.get(action_name)
    
    def get_required_args(self, action_name: str) -> List[str]:
        """Get required arguments for an action"""
        action = self.get_action(action_name)
        return action.required_args if action else []
    
    def get_optional_args(self, action_name: str) -> List[str]:
        """Get optional arguments for an action"""
        action = self.get_action(action_name)
        return action.optional_args if action else []
    
    def is_valid_action(self, action_name: str) -> bool:
        """Check if an action exists"""
        return action_name in self.actions
    
    def list_actions(self) -> List[str]:
        """List all available actions"""
        return list(self.actions.keys())
    
    def _register_default_actions(self):
        """Register default actions"""
        
        # Event-related actions
        self.register_action(ActionDefinition(
            name="create_event",
            description="Create a new calendar event",
            required_args=["title", "start_time"],
            optional_args=["duration", "description", "location", "date"]
        ))
        
        self.register_action(ActionDefinition(
            name="get_events",
            description="Get calendar events",
            required_args=[],
            optional_args=["date", "upcoming_only", "limit"]
        ))
        
        # Time-related actions
        self.register_action(ActionDefinition(
            name="get_time",
            description="Get current time",
            required_args=[],
            optional_args=["timezone"]
        ))
        
        self.register_action(ActionDefinition(
            name="get_date",
            description="Get current date",
            required_args=[],
            optional_args=["format", "timezone"]
        ))
        
        self.register_action(ActionDefinition(
            name="get_day",
            description="Get current day of week",
            required_args=[],
            optional_args=["timezone"]
        ))
        
        # Task-related actions
        self.register_action(ActionDefinition(
            name="create_task",
            description="Create a new task",
            required_args=["title"],
            optional_args=["due_date", "priority", "description"]
        ))
        
        # Note-related actions
        self.register_action(ActionDefinition(
            name="create_note",
            description="Create a new note",
            required_args=["content"],
            optional_args=["title", "tags"]
        ))
        
        self.register_action(ActionDefinition(
            name="get_notes",
            description="Get all notes or search notes",
            required_args=[],
            optional_args=["query", "tag", "limit", "recent_only"]
        ))
        
        self.register_action(ActionDefinition(
            name="get_note",
            description="Get a specific note by ID",
            required_args=["note_id"],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="update_note",
            description="Update a note",
            required_args=["note_id"],
            optional_args=["title", "content", "tags"]
        ))
        
        self.register_action(ActionDefinition(
            name="delete_note",
            description="Delete a note",
            required_args=["note_id"],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="search_notes",
            description="Search notes by query",
            required_args=["query"],
            optional_args=["limit"]
        ))
        
        self.register_action(ActionDefinition(
            name="get_tags",
            description="Get all available tags",
            required_args=[],
            optional_args=[]
        ))
        
        # Greeting action
        self.register_action(ActionDefinition(
            name="greeting",
            description="Handle greetings",
            required_args=[],
            optional_args=[]
        ))
        
        # Unknown action
        self.register_action(ActionDefinition(
            name="unknown",
            description="Handle unknown intents",
            required_args=[],
            optional_args=[]
        ))
    
    def validate_args(self, action_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate arguments for an action and return valid ones"""
        action = self.get_action(action_name)
        if not action:
            return {}
        
        valid_args = {}
        
        # Check required args
        for required_arg in action.required_args:
            if required_arg in args:
                valid_args[required_arg] = args[required_arg]
        
        # Check optional args
        for optional_arg in action.optional_args:
            if optional_arg in args:
                valid_args[optional_arg] = args[optional_arg]
        
        return valid_args
    
    def get_missing_required_args(self, action_name: str, provided_args: Dict[str, Any]) -> List[str]:
        """Get list of missing required arguments"""
        action = self.get_action(action_name)
        if not action:
            return []
        
        missing = []
        for required_arg in action.required_args:
            if required_arg not in provided_args:
                missing.append(required_arg)
        
        return missing 