#!/usr/bin/env python3
"""
Test the reasoning capabilities of the plan executor
"""

from plan_executor import PlanExecutor
from v5.services.lightweight_llm import LightweightLLM

def test_reasoning_with_mock_calendar():
    """Test reasoning with a mock calendar output"""
    
    # Create a mock plan with reasoning
    mock_plan = {
        "goal": "Create dinner event when free tonight",
        "steps": [
            {
                "step_id": 1,
                "action": "get_events",
                "arguments": {"date": "today", "upcoming_only": True},
                "reasoning": "Check calendar for tonight's availability",
                "expected_output": "Events list"
            },
            {
                "step_id": 2,
                "action": "reasoning",
                "arguments": {
                    "input": "step_1_output",
                    "task": "Find free time slots for dinner tonight"
                },
                "reasoning": "Analyze events to find available dinner time",
                "expected_output": "Available time slots",
                "depends_on": [1]
            }
        ]
    }
    
    # Create executor
    executor = PlanExecutor()
    
    # Mock the calendar output (simulating that you have an event at 7 PM)
    mock_calendar_output = """You have 1 event today. Dinner at 7:00 PM."""
    
    # Execute step 1 (mock)
    print("Step 1: Mock calendar check")
    print(f"Calendar output: {mock_calendar_output}")
    
    # Execute step 2 (real reasoning)
    print("\nStep 2: Reasoning about free time")
    reasoning_args = {
        "input": "step_1_output",
        "task": "Find free time slots for dinner tonight"
    }
    
    # Mock the previous outputs
    previous_outputs = {1: mock_calendar_output}
    
    # Execute reasoning
    reasoning_result = executor._execute_reasoning(reasoning_args, previous_outputs)
    
    print(f"\nReasoning result: {reasoning_result}")

def test_reasoning_with_different_scenarios():
    """Test reasoning with different calendar scenarios"""
    
    scenarios = [
        {
            "name": "Busy at 7 PM",
            "calendar_output": "You have 1 event today. Dinner at 7:00 PM."
        },
        {
            "name": "Free evening",
            "calendar_output": "You have no events scheduled."
        },
        {
            "name": "Multiple events",
            "calendar_output": "You have 3 events today. Meeting at 5:00 PM, Dinner at 7:00 PM, Movie at 9:00 PM."
        }
    ]
    
    executor = PlanExecutor()
    
    for scenario in scenarios:
        print(f"\n{'='*50}")
        print(f"Testing scenario: {scenario['name']}")
        print(f"{'='*50}")
        
        reasoning_args = {
            "input": "step_1_output",
            "task": "Find free time slots for dinner tonight"
        }
        
        previous_outputs = {1: scenario['calendar_output']}
        
        reasoning_result = executor._execute_reasoning(reasoning_args, previous_outputs)
        
        print(f"Calendar: {scenario['calendar_output']}")
        print(f"Reasoning: {reasoning_result}")

if __name__ == "__main__":
    print("Testing Reasoning Capabilities")
    print("=" * 60)
    
    # Test with your specific scenario (busy at 7 PM)
    test_reasoning_with_mock_calendar()
    
    # Test multiple scenarios
    test_reasoning_with_different_scenarios() 