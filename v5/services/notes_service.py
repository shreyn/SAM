#!/usr/bin/env python3
"""
Local Notes Service for SAM
Handles note creation, retrieval, editing, and deletion using local files
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

@dataclass
class Note:
    """Represents a note"""
    id: str
    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        """Create Note from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

class NotesService:
    """Local file-based notes service"""
    
    def __init__(self, notes_dir: str = None):
        if notes_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            notes_dir = os.path.join(base_dir, "data", "notes")
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.notes_dir / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Load the notes index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.index = {}
        else:
            self.index = {}
    
    def _save_index(self):
        """Save the notes index"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving notes index: {e}")
    
    def _generate_id(self) -> str:
        """Generate a unique note ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"note_{timestamp}"
    
    def create_note(self, title: str, content: str) -> Optional[Note]:
        """Create a new note"""
        try:
            note_id = self._generate_id()
            
            # Create note object
            note = Note(
                id=note_id,
                title=title,
                content=content
            )
            
            # Save note file
            note_file = self.notes_dir / f"{note_id}.json"
            with open(note_file, 'w', encoding='utf-8') as f:
                json.dump(note.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Update index
            self.index[note_id] = {
                'title': title,
                'filename': f"{note_id}.json",
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat()
            }
            self._save_index()
            
            return note
            
        except Exception as e:
            print(f"Error creating note: {e}")
            return None
    
    def get_or_create_todo_note(self) -> Note:
        """Get the todo note, create it if it doesn't exist"""
        todo_note = self.get_note_by_title("to do")
        if not todo_note:
            # Create the todo note with empty content
            todo_note = self.create_note("to do", "")
        else:
            # Ensure existing todo items are properly numbered
            todo_note = self._ensure_todo_numbering(todo_note)
        return todo_note
    
    def _ensure_todo_numbering(self, todo_note: Note) -> Note:
        """Ensure all todo items have proper numbering"""
        if not todo_note.content.strip():
            return todo_note
        
        lines = [line.strip() for line in todo_note.content.split('\n') if line.strip()]
        numbered_lines = []
        
        for i, line in enumerate(lines, 1):
            # Check if line already has a number
            if re.match(r'^\d+[.)]', line):
                numbered_lines.append(line)
            else:
                # Add number to line
                numbered_lines.append(f"{i}. {line}")
        
        if numbered_lines != lines:
            # Update the note with proper numbering
            new_content = '\n'.join(numbered_lines)
            self.edit_note("to do", new_content)
            # Return updated note
            return self.get_note_by_title("to do")
        
        return todo_note
    
    def add_todo_item(self, item_text: str) -> bool:
        """Add an item to the todo list"""
        try:
            todo_note = self.get_or_create_todo_note()
            # Parse existing content to find the highest number
            lines = [line for line in todo_note.content.split('\n') if line.strip()]
            max_number = 0
            for line in lines:
                match = re.match(r'^(\d+)[.)]', line.strip())
                if match:
                    number = int(match.group(1))
                    max_number = max(max_number, number)
            new_number = max_number + 1
            new_line = f"{new_number}. {item_text}"
            if todo_note.content.strip():
                new_content = todo_note.content + '\n' + new_line
            else:
                new_content = new_line
            success = self.edit_note("to do", new_content)
            return success
        except Exception as e:
            print(f"Error adding todo item: {e}")
            return False
    
    def clear_todo_list(self) -> bool:
        """Clear the todo list"""
        try:
            todo_note = self.get_or_create_todo_note()
            success = self.edit_note("to do", "")
            return success
        except Exception as e:
            print(f"Error clearing todo list: {e}")
            return False
    
    def remove_todo_item(self, item_number: int) -> bool:
        """Remove a specific item from the todo list"""
        try:
            todo_note = self.get_or_create_todo_note()
            lines = [line for line in todo_note.content.split('\n') if line.strip()]
            new_lines = []
            renumbered = False
            for line in lines:
                match = re.match(r'^(\d+)[.)]', line.strip())
                if match:
                    number = int(match.group(1))
                    if number == item_number:
                        renumbered = True
                        continue
                    elif renumbered:
                        new_number = number - 1
                        new_line = re.sub(r'^\d+[.)]', f"{new_number}.", line)
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            if not new_lines:
                new_content = ""
            else:
                new_content = '\n'.join(new_lines)
            success = self.edit_note("to do", new_content)
            return success
        except Exception as e:
            print(f"Error removing todo item: {e}")
            return False
    
    def get_note(self, note_id: str) -> Optional[Note]:
        """Get a note by ID"""
        try:
            if note_id not in self.index:
                return None
            
            note_file = self.notes_dir / self.index[note_id]['filename']
            if not note_file.exists():
                return None
            
            with open(note_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Note.from_dict(data)
            
        except Exception as e:
            print(f"Error loading note: {e}")
            return None
    
    def get_note_by_title(self, title: str) -> Optional[Note]:
        """Get a note by title"""
        try:
            # Search through index for matching title
            for note_id, note_info in self.index.items():
                if note_info['title'].lower() == title.lower():
                    return self.get_note(note_id)
            return None
            
        except Exception as e:
            print(f"Error finding note by title: {e}")
            return None
    
    def edit_note(self, title: str, new_content: str) -> bool:
        """Edit a note's content by title"""
        try:
            note = self.get_note_by_title(title)
            if not note:
                return False
            
            # Update content and timestamp
            note.content = new_content
            note.updated_at = datetime.now()
            
            # Save updated note
            note_file = self.notes_dir / f"{note.id}.json"
            with open(note_file, 'w', encoding='utf-8') as f:
                json.dump(note.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Update index
            self.index[note.id]['updated_at'] = note.updated_at.isoformat()
            self._save_index()
            
            return True
            
        except Exception as e:
            print(f"Error editing note: {e}")
            return False
    
    def delete_note_by_title(self, title: str) -> bool:
        """Delete a note by title"""
        try:
            note = self.get_note_by_title(title)
            if not note:
                return False
            
            # Delete note file
            note_file = self.notes_dir / f"{note.id}.json"
            if note_file.exists():
                note_file.unlink()
            
            # Remove from index
            if note.id in self.index:
                del self.index[note.id]
                self._save_index()
            
            return True
            
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False
    
    def get_all_notes(self) -> List[Note]:
        """Get all notes"""
        notes = []
        for note_id in self.index:
            note = self.get_note(note_id)
            if note:
                notes.append(note)
        # Sort by updated_at (newest first)
        notes.sort(key=lambda x: x.updated_at, reverse=True)
        return notes
    
    def format_note_for_display(self, note: Note, include_content: bool = True) -> str:
        """Format a note for display"""
        lines = []
        lines.append(f"📝 {note.title}")
        lines.append(f"🆔 {note.id}")
        lines.append(f"📅 Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"🔄 Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        if include_content:
            lines.append("")
            lines.append("📄 Content:")
            lines.append("-" * 40)
            lines.append(note.content)
        
        return "\n".join(lines)
    
    def format_notes_list(self, notes: List[Note]) -> str:
        """Format a list of notes for display"""
        if not notes:
            return "No notes found."
        
        lines = []
        for i, note in enumerate(notes, 1):
            lines.append(f"{i}. {note.title}")
        
        return "\n".join(lines) 