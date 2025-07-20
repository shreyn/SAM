#!/usr/bin/env python3
"""
Demo script for SAM Notes functionality
Shows how to use the notes system with natural language
"""

from core.brain import SAMBrain
import time

def demo_notes():
    """Demonstrate notes functionality"""
    print("📝 SAM Notes Demo")
    print("=" * 50)
    
    # Initialize SAM
    sam = SAMBrain()
    
    # Demo conversations
    demos = [
        # Create notes
        ("Create a note about Python programming", "Creating a note about Python programming"),
        ("Learn Python basics, data structures, and OOP", "Adding content to the note"),
        ("with tags programming, python, learning", "Adding tags to the note"),
        
        # Create another note
        ("Create a note called shopping list", "Creating a shopping list note"),
        ("Milk, bread, eggs, cheese, and vegetables", "Adding items to shopping list"),
        ("with tags shopping, personal", "Adding tags to shopping list"),
        
        # Create a work note
        ("Write a note about meeting notes", "Creating a meeting notes"),
        ("Discuss project timeline, assign tasks, and set deadlines", "Adding meeting content"),
        ("with tags work, meeting, project", "Adding work-related tags"),
        
        # View notes
        ("Show my notes", "Displaying all notes"),
        ("Show recent notes", "Showing recent notes"),
        ("Show notes with tag work", "Filtering by work tag"),
        
        # Search notes
        ("Search notes for python", "Searching for Python-related notes"),
        ("Find notes about shopping", "Searching for shopping notes"),
        ("Search notes for meeting", "Searching for meeting notes"),
        
        # Get tags
        ("Show all tags", "Displaying all available tags"),
        
        # Create a note with all info at once
        ("Create a note called recipe for pasta with content boil water, add pasta, cook for 10 minutes with tags cooking, food", "Creating a complete note"),
        
        # Search and view
        ("Search notes for recipe", "Searching for recipe notes"),
        ("Show my notes", "Final view of all notes"),
    ]
    
    for query, description in demos:
        print(f"\n👤 User: {query}")
        print(f"📝 Action: {description}")
        
        response = sam.process_message(query)
        print(f"🤖 SAM: {response}")
        
        # Add a small delay to make the demo more readable
        time.sleep(1)
    
    print("\n🎉 Notes demo completed!")
    print("\n💡 Try these commands yourself:")
    print("• 'Create a note about [topic]'")
    print("• 'Show my notes'")
    print("• 'Search notes for [keyword]'")
    print("• 'Show notes with tag [tag]'")
    print("• 'Show all tags'")

if __name__ == "__main__":
    demo_notes() 