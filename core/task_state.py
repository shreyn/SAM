#!/usr/bin/env python3
"""
Task State Management for Follow-up System
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class TaskState:
    """Represents the current task state for follow-up management"""
    
    # Current task information
    current_action: Optional[str] = None
    intent_type: Optional[str] = None
    confidence: float = 0.0
    
    # Arguments management
    collected_args: Dict[str, Any] = field(default_factory=dict)
    missing_args: List[str] = field(default_factory=list)
    required_args: List[str] = field(default_factory=list)
    
    # Follow-up state
    is_follow_up: bool = False
    follow_up_count: int = 0
    last_follow_up: Optional[str] = None
    
    # Timestamp
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.last_updated == self.created_at:
            self.last_updated = self.created_at
    
    def start_new_task(self, action: str, intent_type: str, confidence: float, 
                      required_args: List[str], initial_args: Dict[str, Any] = None):
        """Start a new task"""
        self.current_action = action
        self.intent_type = intent_type
        self.confidence = confidence
        self.required_args = required_args.copy()
        self.collected_args = initial_args.copy() if initial_args else {}
        self.missing_args = self._calculate_missing_args()
        self.is_follow_up = False
        self.follow_up_count = 0
        self.last_follow_up = None
        self.last_updated = datetime.now()
    
    def add_follow_up(self, follow_up_message: str):
        """Add a follow-up interaction"""
        self.is_follow_up = True
        self.follow_up_count += 1
        self.last_follow_up = follow_up_message
        self.last_updated = datetime.now()
    
    def update_args(self, new_args: Dict[str, Any]):
        """Update collected arguments"""
        self.collected_args.update(new_args)
        self.missing_args = self._calculate_missing_args()
        self.last_updated = datetime.now()
    
    def _calculate_missing_args(self) -> List[str]:
        """Calculate which required arguments are still missing"""
        return [arg for arg in self.required_args if arg not in self.collected_args]
    
    def is_complete(self) -> bool:
        """Check if all required arguments are collected"""
        return len(self.missing_args) == 0
    
    def get_next_missing_arg(self) -> Optional[str]:
        """Get the next missing argument to ask for"""
        return self.missing_args[0] if self.missing_args else None
    
    def get_follow_up_question(self) -> str:
        """Generate a follow-up question for the next missing argument"""
        if not self.missing_args:
            return ""
        
        next_arg = self.missing_args[0]
        
        # Generate appropriate questions based on argument type
        questions = {
            'title': "What should I call this event?",
            'start_time': "When should this event start?",
            'date': "What date should this be for?",
            'time': "What time should this be?",
            'duration': "How long should this event last?",
            'description': "What's the description for this event?",
            'location': "Where should this event take place?",
            'content': "What should the note say?",
            'note_id': "What's the ID of the note?",
            'query': "What would you like to search for?",
            'tag': "What tag would you like to filter by?",
            'tags': "What tags should I add to this note?"
        }
        
        # Override title question for note actions
        if self.current_action == 'create_note':
            questions['title'] = "What should I call this note?"
        elif self.current_action == 'read_note':
            questions['title'] = "What note do you want me to read?"
        elif self.current_action == 'edit_note':
            questions['title'] = "What note do you want me to edit?"
        elif self.current_action == 'delete_note':
            questions['title'] = "What note do you want me to delete?"
        elif self.current_action == 'add_todo':
            questions['item'] = "What would you like to add to your todo list?"
        elif self.current_action == 'remove_todo_item':
            questions['item_number'] = "Which item number would you like to remove?"
        
        return questions.get(next_arg, f"What's the {next_arg.replace('_', ' ')}?")
    
    def reset(self):
        """Reset the task state"""
        self.current_action = None
        self.intent_type = None
        self.confidence = 0.0
        self.collected_args.clear()
        self.missing_args.clear()
        self.required_args.clear()
        self.is_follow_up = False
        self.follow_up_count = 0
        self.last_follow_up = None
        self.last_updated = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 10) -> bool:
        """Check if the task state has expired"""
        time_diff = datetime.now() - self.last_updated
        return time_diff.total_seconds() > (timeout_minutes * 60)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'current_action': self.current_action,
            'intent_type': self.intent_type,
            'confidence': self.confidence,
            'collected_args': self.collected_args,
            'missing_args': self.missing_args,
            'required_args': self.required_args,
            'is_follow_up': self.is_follow_up,
            'follow_up_count': self.follow_up_count,
            'last_follow_up': self.last_follow_up,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        } 