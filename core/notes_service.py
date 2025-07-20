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
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
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
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

class NotesService:
    """Local file-based notes service"""
    
    def __init__(self, notes_dir: str = "data/notes"):
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
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for filename"""
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:47] + "..."
        return sanitized.strip()
    
    def create_note(self, title: str, content: str, tags: List[str] = None) -> Optional[Note]:
        """Create a new note"""
        try:
            note_id = self._generate_id()
            sanitized_title = self._sanitize_filename(title)
            
            # Create note object
            note = Note(
                id=note_id,
                title=title,
                content=content,
                tags=tags or []
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
                'updated_at': note.updated_at.isoformat(),
                'tags': tags or []
            }
            self._save_index()
            
            return note
            
        except Exception as e:
            print(f"Error creating note: {e}")
            return None
    
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
    
    def search_notes(self, query: str) -> List[Note]:
        """Search notes by title, content, or tags"""
        query_lower = query.lower()
        matching_notes = []
        
        for note in self.get_all_notes():
            # Search in title
            if query_lower in note.title.lower():
                matching_notes.append(note)
                continue
            
            # Search in content
            if query_lower in note.content.lower():
                matching_notes.append(note)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in note.tags):
                matching_notes.append(note)
                continue
        
        return matching_notes
    
    def update_note(self, note_id: str, title: str = None, content: str = None, tags: List[str] = None) -> bool:
        """Update a note"""
        try:
            note = self.get_note(note_id)
            if not note:
                return False
            
            # Update fields
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            if tags is not None:
                note.tags = tags
            
            note.updated_at = datetime.now()
            
            # Save updated note
            note_file = self.notes_dir / f"{note_id}.json"
            with open(note_file, 'w', encoding='utf-8') as f:
                json.dump(note.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Update index
            if note_id in self.index:
                self.index[note_id]['title'] = note.title
                self.index[note_id]['updated_at'] = note.updated_at.isoformat()
                self.index[note_id]['tags'] = note.tags
                self._save_index()
            
            return True
            
        except Exception as e:
            print(f"Error updating note: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note"""
        try:
            if note_id not in self.index:
                return False
            
            # Delete note file
            note_file = self.notes_dir / self.index[note_id]['filename']
            if note_file.exists():
                note_file.unlink()
            
            # Remove from index
            del self.index[note_id]
            self._save_index()
            
            return True
            
        except Exception as e:
            print(f"Error deleting note: {e}")
            return False
    
    def get_notes_by_tag(self, tag: str) -> List[Note]:
        """Get all notes with a specific tag"""
        tag_lower = tag.lower()
        matching_notes = []
        
        for note in self.get_all_notes():
            if any(tag_lower == note_tag.lower() for note_tag in note.tags):
                matching_notes.append(note)
        
        return matching_notes
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        tags = set()
        for note in self.get_all_notes():
            tags.update(note.tags)
        return sorted(list(tags))
    
    def get_recent_notes(self, limit: int = 5) -> List[Note]:
        """Get the most recent notes"""
        all_notes = self.get_all_notes()
        return all_notes[:limit]
    
    def format_note_for_display(self, note: Note, include_content: bool = True) -> str:
        """Format a note for display"""
        lines = []
        lines.append(f"📝 {note.title}")
        lines.append(f"🆔 {note.id}")
        lines.append(f"📅 Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"🔄 Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
        
        if note.tags:
            lines.append(f"🏷️  Tags: {', '.join(note.tags)}")
        
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
            lines.append(f"{i}. 📝 {note.title}")
            lines.append(f"   🆔 {note.id}")
            lines.append(f"   📅 {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
            if note.tags:
                lines.append(f"   🏷️  {', '.join(note.tags)}")
            lines.append("")
        
        return "\n".join(lines) 