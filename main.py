#!/usr/bin/env python3
"""
SAM - Smart Assistant Manager
Main entry point for the SAM assistant
"""

import os
import sys
from core.brain import SAMBrain

def main():
    """Main function to run SAM"""
    print("🤖 SAM - Smart Assistant Manager")
    print("=" * 50)
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for available commands")
    print("=" * 50)
    
    # Initialize SAM brain
    sam = SAMBrain()
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! SAM is shutting down.")
                break
            
            # Check for help
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # Check for debug commands
            if user_input.lower() == 'debug':
                print_debug_info(sam)
                continue
            
            # Check for reset
            if user_input.lower() == 'reset':
                sam.reset_task_state()
                print("🔄 Task state has been reset.")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Process the message
            response = sam.process_message(user_input)
            print(f"🤖 SAM: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! SAM is shutting down.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'help' for assistance.")

def print_help():
    """Print help information"""
    print("\n📚 SAM Help")
    print("-" * 30)
    print("Available commands:")
    print("• 'help' - Show this help")
    print("• 'debug' - Show debug information")
    print("• 'reset' - Reset current task")
    print("• 'quit' or 'exit' - Exit SAM")
    print("\nExample queries:")
    print("• 'What time is it?'")
    print("• 'What day is it?'")
    print("• 'Do I have events today?'")
    print("• 'Create an event called meeting'")
    print("• 'Next event?'")
    print("• 'Create a note about project ideas'")
    print("• 'Show my notes'")
    print("• 'Search notes for python'")
    print("• 'Hello'")

def print_debug_info(sam):
    """Print debug information"""
    print("\n🔍 Debug Information")
    print("-" * 30)
    task_state = sam.get_task_state()
    print(f"Current Action: {task_state.get('current_action', 'None')}")
    print(f"Intent Type: {task_state.get('intent_type', 'None')}")
    print(f"Confidence: {task_state.get('confidence', 0.0):.2f}")
    print(f"Collected Args: {task_state.get('collected_args', {})}")
    print(f"Missing Args: {task_state.get('missing_args', [])}")
    print(f"Is Follow-up: {task_state.get('is_follow_up', False)}")
    print(f"Follow-up Count: {task_state.get('follow_up_count', 0)}")

if __name__ == "__main__":
    main() 