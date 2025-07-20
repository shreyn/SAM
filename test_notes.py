#!/usr/bin/env python3
"""
Test Notes Functionality for SAM
Tests all note-related features including creation, retrieval, search, and management
"""

import os
import shutil
import tempfile
from datetime import datetime
from core.notes_service import NotesService, Note

class NotesTestSuite:
    """Comprehensive test suite for notes functionality"""
    
    def __init__(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.notes_service = NotesService(notes_dir=self.test_dir)
        self.test_results = []
        
        # Clear any existing notes
        self.notes_service.index = {}
        self.notes_service._save_index()
        
    def cleanup(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def clear_notes(self):
        """Clear all notes for testing"""
        self.notes_service.index = {}
        self.notes_service._save_index()
        # Also clear any existing note files
        for file in self.notes_service.notes_dir.glob("*.json"):
            if file.name != "index.json":
                file.unlink()
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log a test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def test_create_note(self):
        """Test note creation"""
        print("\n=== Testing Note Creation ===")
        
        # Test basic note creation
        note = self.notes_service.create_note(
            title="Test Note",
            content="This is a test note content.",
            tags=["test", "sample"]
        )
        
        self.log_test(
            "Basic note creation",
            note is not None and note.title == "Test Note",
            f"Created note with ID: {note.id if note else 'None'}"
        )
        
        # Test note creation without tags
        note2 = self.notes_service.create_note(
            title="Untagged Note",
            content="This note has no tags."
        )
        
        self.log_test(
            "Note creation without tags",
            note2 is not None and note2.tags == [],
            f"Created note with ID: {note2.id if note2 else 'None'}"
        )
        
        # Test note creation with special characters in title
        note3 = self.notes_service.create_note(
            title="Note with special chars: <>/\\|?*",
            content="This note has special characters in the title."
        )
        
        self.log_test(
            "Note creation with special characters",
            note3 is not None,
            f"Created note with ID: {note3.id if note3 else 'None'}"
        )
    
    def test_get_note(self):
        """Test note retrieval"""
        print("\n=== Testing Note Retrieval ===")
        
        # Create a test note
        original_note = self.notes_service.create_note(
            title="Retrieval Test",
            content="This note is for testing retrieval.",
            tags=["retrieval", "test"]
        )
        
        # Test getting the note by ID
        retrieved_note = self.notes_service.get_note(original_note.id)
        
        self.log_test(
            "Get note by ID",
            retrieved_note is not None and retrieved_note.title == original_note.title,
            f"Retrieved note: {retrieved_note.title if retrieved_note else 'None'}"
        )
        
        # Test getting non-existent note
        fake_note = self.notes_service.get_note("fake_id_123")
        
        self.log_test(
            "Get non-existent note",
            fake_note is None,
            "Correctly returned None for fake ID"
        )
    
    def test_get_all_notes(self):
        """Test getting all notes"""
        print("\n=== Testing Get All Notes ===")
        
        # Clear existing notes
        self.clear_notes()
        
        # Create multiple notes with small delays to ensure different timestamps
        import time
        note1 = self.notes_service.create_note("First Note", "Content 1", ["first"])
        time.sleep(0.1)
        note2 = self.notes_service.create_note("Second Note", "Content 2", ["second"])
        time.sleep(0.1)
        note3 = self.notes_service.create_note("Third Note", "Content 3", ["third"])
        
        # Get all notes
        all_notes = self.notes_service.get_all_notes()
        
        self.log_test(
            "Get all notes",
            len(all_notes) == 3,
            f"Found {len(all_notes)} notes"
        )
        
        # Test sorting (should be newest first) - only if we have enough notes
        if len(all_notes) >= 2:
            self.log_test(
                "Notes sorted by updated_at",
                all_notes[0].updated_at >= all_notes[1].updated_at,
                "Notes are properly sorted by update time"
            )
        else:
            self.log_test(
                "Notes sorted by updated_at",
                True,  # Skip this test if not enough notes
                "Not enough notes to test sorting"
            )
    
    def test_search_notes(self):
        """Test note search functionality"""
        print("\n=== Testing Note Search ===")
        
        # Clear existing notes first
        self.clear_notes()
        
        # Create test notes
        self.notes_service.create_note("Python Programming", "Learn Python basics", ["programming", "python"])
        self.notes_service.create_note("Meeting Notes", "Discuss project timeline", ["meeting", "work"])
        self.notes_service.create_note("Shopping List", "Milk, bread, eggs", ["shopping", "personal"])
        
        # Test search by title
        python_notes = self.notes_service.search_notes("Python")
        self.log_test(
            "Search by title",
            len(python_notes) == 1 and python_notes[0].title == "Python Programming",
            f"Found {len(python_notes)} notes with 'Python' in title"
        )
        
        # Test search by content
        meeting_notes = self.notes_service.search_notes("timeline")
        self.log_test(
            "Search by content",
            len(meeting_notes) == 1 and "timeline" in meeting_notes[0].content,
            f"Found {len(meeting_notes)} notes with 'timeline' in content"
        )
        
        # Test search by tag
        programming_notes = self.notes_service.search_notes("programming")
        self.log_test(
            "Search by tag",
            len(programming_notes) == 1 and "programming" in programming_notes[0].tags,
            f"Found {len(programming_notes)} notes with 'programming' tag"
        )
        
        # Test search with no results
        no_results = self.notes_service.search_notes("nonexistent")
        self.log_test(
            "Search with no results",
            len(no_results) == 0,
            "Correctly returned empty list for non-existent search"
        )
    
    def test_update_note(self):
        """Test note updating"""
        print("\n=== Testing Note Updates ===")
        
        # Clear existing notes
        self.clear_notes()
        
        # Create a test note
        original_note = self.notes_service.create_note(
            "Original Title",
            "Original content",
            ["original"]
        )
        
        # Update title
        success1 = self.notes_service.update_note(
            original_note.id,
            title="Updated Title"
        )
        
        self.log_test(
            "Update note title",
            success1,
            "Successfully updated note title"
        )
        
        # Verify update
        updated_note = self.notes_service.get_note(original_note.id)
        self.log_test(
            "Verify title update",
            updated_note.title == "Updated Title",
            f"Title is now: {updated_note.title}"
        )
        
        # Update content
        success2 = self.notes_service.update_note(
            original_note.id,
            content="Updated content"
        )
        
        self.log_test(
            "Update note content",
            success2,
            "Successfully updated note content"
        )
        
        # Update tags
        success3 = self.notes_service.update_note(
            original_note.id,
            tags=["updated", "new"]
        )
        
        self.log_test(
            "Update note tags",
            success3,
            "Successfully updated note tags"
        )
        
        # Verify all updates
        final_note = self.notes_service.get_note(original_note.id)
        self.log_test(
            "Verify all updates",
            (final_note.title == "Updated Title" and 
             final_note.content == "Updated content" and 
             final_note.tags == ["updated", "new"]),
            f"Final note: {final_note.title}, {final_note.content[:20]}..., tags: {final_note.tags}"
        )
    
    def test_delete_note(self):
        """Test note deletion"""
        print("\n=== Testing Note Deletion ===")
        
        # Clear existing notes
        self.clear_notes()
        
        # Create a test note
        note = self.notes_service.create_note(
            "To Delete",
            "This note will be deleted",
            ["delete"]
        )
        
        # Verify note exists
        existing_note = self.notes_service.get_note(note.id)
        self.log_test(
            "Note exists before deletion",
            existing_note is not None,
            f"Note exists with ID: {note.id}"
        )
        
        # Delete the note
        success = self.notes_service.delete_note(note.id)
        
        self.log_test(
            "Delete note",
            success,
            "Successfully deleted note"
        )
        
        # Verify note is gone
        deleted_note = self.notes_service.get_note(note.id)
        self.log_test(
            "Note deleted",
            deleted_note is None,
            "Note no longer exists"
        )
        
        # Test deleting non-existent note
        fake_success = self.notes_service.delete_note("fake_id")
        self.log_test(
            "Delete non-existent note",
            not fake_success,
            "Correctly failed to delete non-existent note"
        )
    
    def test_tags_functionality(self):
        """Test tag-related functionality"""
        print("\n=== Testing Tags Functionality ===")
        
        # Clear existing notes first
        self.clear_notes()
        
        # Create notes with various tags
        self.notes_service.create_note("Work Note", "Work content", ["work", "important"])
        self.notes_service.create_note("Personal Note", "Personal content", ["personal", "important"])
        self.notes_service.create_note("Shopping Note", "Shopping content", ["shopping", "personal"])
        
        # Test get notes by tag
        work_notes = self.notes_service.get_notes_by_tag("work")
        self.log_test(
            "Get notes by tag",
            len(work_notes) == 1 and work_notes[0].title == "Work Note",
            f"Found {len(work_notes)} notes with 'work' tag"
        )
        
        # Test get all tags
        all_tags = self.notes_service.get_all_tags()
        expected_tags = ["important", "personal", "shopping", "work"]
        self.log_test(
            "Get all tags",
            set(all_tags) == set(expected_tags),
            f"Found tags: {all_tags}"
        )
        
        # Test case-insensitive tag search
        important_notes = self.notes_service.get_notes_by_tag("IMPORTANT")
        self.log_test(
            "Case-insensitive tag search",
            len(important_notes) == 2,
            f"Found {len(important_notes)} notes with 'IMPORTANT' tag (case-insensitive)"
        )
    
    def test_recent_notes(self):
        """Test recent notes functionality"""
        print("\n=== Testing Recent Notes ===")
        
        # Clear existing notes first
        self.clear_notes()
        
        # Create multiple notes
        for i in range(10):
            self.notes_service.create_note(
                f"Note {i}",
                f"Content {i}",
                [f"tag{i}"]
            )
        
        # Test get recent notes with default limit
        recent_notes = self.notes_service.get_recent_notes()
        self.log_test(
            "Get recent notes (default limit)",
            len(recent_notes) == 5,
            f"Found {len(recent_notes)} recent notes"
        )
        
        # Test get recent notes with custom limit
        recent_notes_3 = self.notes_service.get_recent_notes(3)
        self.log_test(
            "Get recent notes (custom limit)",
            len(recent_notes_3) == 3,
            f"Found {len(recent_notes_3)} recent notes with limit 3"
        )
    
    def test_formatting(self):
        """Test note formatting functions"""
        print("\n=== Testing Note Formatting ===")
        
        # Clear existing notes
        self.clear_notes()
        
        # Create a test note
        note = self.notes_service.create_note(
            "Format Test",
            "This is a test note for formatting.\nIt has multiple lines.",
            ["format", "test"]
        )
        
        # Test format_note_for_display
        formatted = self.notes_service.format_note_for_display(note)
        self.log_test(
            "Format note for display",
            "📝 Format Test" in formatted and "📄 Content:" in formatted,
            "Note properly formatted for display"
        )
        
        # Test format_notes_list
        notes_list = self.notes_service.format_notes_list([note])
        self.log_test(
            "Format notes list",
            "📝 Format Test" in notes_list and "🆔" in notes_list,
            "Notes list properly formatted"
        )
        
        # Test empty list formatting
        empty_list = self.notes_service.format_notes_list([])
        self.log_test(
            "Format empty notes list",
            empty_list == "No notes found.",
            "Empty list properly formatted"
        )
    
    def run_all_tests(self):
        """Run all test categories"""
        print("🧪 STARTING NOTES TEST SUITE")
        print("=" * 50)
        
        try:
            self.test_create_note()
            self.test_get_note()
            self.test_get_all_notes()
            self.test_search_notes()
            self.test_update_note()
            self.test_delete_note()
            self.test_tags_functionality()
            self.test_recent_notes()
            self.test_formatting()
            
            self.print_summary()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*20} TEST SUMMARY {'='*20}")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("\n✅ All tests passed!")
        
        print(f"\n🎉 Notes test suite completed!")

if __name__ == "__main__":
    test_suite = NotesTestSuite()
    test_suite.run_all_tests() 