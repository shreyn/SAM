#!/usr/bin/env python3
"""
Test script for the Plan Generator - v5 Integration
"""

import sys
import os
from plan_generator import PlanGenerator

def test_single_prompt():
    """Test the plan generator with a single prompt"""
    generator = PlanGenerator()
    
    # Test the specific example you mentioned
    prompt = "Create an event to eat dinner when I'm free tonight"
    
    print("Testing Plan Generator - v5 Integration")
    print("=" * 60)
    print(f"Input: {prompt}")
    print()
    
    try:
        plan = generator.generate_plan(prompt)
        print("Generated Plan:")
        print(plan.to_json())
    except Exception as e:
        print(f"[ERROR] {str(e)}")

def test_multiple_prompts():
    """Test multiple prompts to verify plan generation quality"""
    generator = PlanGenerator()
    
    test_cases = [
        {
            "prompt": "Create an event to eat dinner when I'm free tonight",
            "expected_actions": ["get_events", "create_event"],
            "description": "Complex scheduling with availability check"
        },
        {
            "prompt": "What's my schedule for tomorrow and create a note about it",
            "expected_actions": ["get_events", "create_note"],
            "description": "Information gathering and note creation"
        },
        {
            "prompt": "Add 'buy groceries' to my todo list and show me what's on it",
            "expected_actions": ["add_todo", "show_todo"],
            "description": "Todo list management"
        },
        {
            "prompt": "What time is it and what day is today?",
            "expected_actions": ["get_time", "get_day"],
            "description": "Simple time/date queries"
        },
        {
            "prompt": "Create a note about my meeting tomorrow and add it to my todo list",
            "expected_actions": ["create_note", "add_todo"],
            "description": "Note creation and todo addition"
        }
    ]
    
    print("Comprehensive Plan Generator Testing")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print("-" * 40)
        print(f"Prompt: {test_case['prompt']}")
        print(f"Expected actions: {test_case['expected_actions']}")
        
        try:
            plan = generator.generate_plan(test_case['prompt'])
            print("\nGenerated Plan:")
            print(plan.to_json())
            
            # Validate that expected actions are present
            generated_actions = [step.action for step in plan.steps]
            missing_actions = [action for action in test_case['expected_actions'] if action not in generated_actions]
            
            if missing_actions:
                print(f"\n[WARNING] Missing expected actions: {missing_actions}")
            else:
                print(f"\n[SUCCESS] All expected actions found: {test_case['expected_actions']}")
                
        except Exception as e:
            print(f"[ERROR] {str(e)}")
        
        print("\n" + "="*60)

def test_interactive():
    """Interactive testing mode"""
    generator = PlanGenerator()
    
    print("Interactive Plan Generator - v5 Integration")
    print("=" * 60)
    print("Enter prompts to generate plans. Type 'quit' to exit.")
    print("Available actions in v5:")
    
    # Show available actions
    from v5.action_schema import ACTIONS
    for action_name, action_info in ACTIONS.items():
        print(f"  - {action_name}: {action_info['description']}")
    
    print("\n" + "="*60)
    
    while True:
        prompt = input("\nEnter your prompt: ").strip()
        
        if prompt.lower() in ['quit', 'exit', 'q']:
            break
        
        if not prompt:
            continue
        
        print(f"\nGenerating plan for: '{prompt}'")
        print("-" * 40)
        
        try:
            plan = generator.generate_plan(prompt)
            print("\nGenerated Plan:")
            print(plan.to_json())
            
            # Show plan summary
            print(f"\nPlan Summary:")
            print(f"  Goal: {plan.goal}")
            print(f"  Steps: {len(plan.steps)}")
            for step in plan.steps:
                print(f"    Step {step.step_id}: {step.action} - {step.reasoning}")
                
        except Exception as e:
            print(f"[ERROR] {str(e)}")
        
        print("\n" + "="*60)

def test_edge_cases():
    """Test edge cases and error handling"""
    generator = PlanGenerator()
    
    edge_cases = [
        {
            "prompt": "",
            "description": "Empty prompt"
        },
        {
            "prompt": "Hello",
            "description": "Simple greeting"
        },
        {
            "prompt": "Do something impossible that doesn't exist",
            "description": "Impossible request"
        },
        {
            "prompt": "Create an event called 'Meeting' at 3pm tomorrow with location 'Office' and duration 2 hours",
            "description": "Complex event with many arguments"
        }
    ]
    
    print("Edge Case Testing")
    print("=" * 60)
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: {test_case['description']}")
        print("-" * 40)
        print(f"Prompt: '{test_case['prompt']}'")
        
        try:
            plan = generator.generate_plan(test_case['prompt'])
            print("\nGenerated Plan:")
            print(plan.to_json())
        except Exception as e:
            print(f"[ERROR] {str(e)}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "--interactive":
            test_interactive()
        elif mode == "--comprehensive":
            test_multiple_prompts()
        elif mode == "--edge-cases":
            test_edge_cases()
        elif mode == "--single":
            test_single_prompt()
        else:
            print("Usage:")
            print("  python test_plan_generator.py                    # Single test")
            print("  python test_plan_generator.py --interactive     # Interactive mode")
            print("  python test_plan_generator.py --comprehensive   # Multiple tests")
            print("  python test_plan_generator.py --edge-cases      # Edge case testing")
    else:
        test_single_prompt() 