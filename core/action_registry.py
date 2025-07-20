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
            required_args=["title", "content"],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="read_note",
            description="Read a specific note by title",
            required_args=["title"],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="edit_note",
            description="Edit a note's content",
            required_args=["title", "content"],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="delete_note",
            description="Delete a note",
            required_args=["title"],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="list_notes",
            description="List all notes",
            required_args=[],
            optional_args=["tag", "limit"]
        ))
        
        # Todo-related actions
        self.register_action(ActionDefinition(
            name="add_todo",
            description="Add item to todo list",
            required_args=["item"],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="show_todo",
            description="Show todo list",
            required_args=[],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="clear_todo",
            description="Clear todo list",
            required_args=[],
            optional_args=[]
        ))
        
        self.register_action(ActionDefinition(
            name="remove_todo_item",
            description="Remove item from todo list",
            required_args=["item_number"],
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