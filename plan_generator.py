#!/usr/bin/env python3
"""
Plan Generator for SAM v5
Converts natural language prompts into structured JSON plans using available actions.
Integrates with v5's LLM interface and action schema.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Import v5 components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'v5'))

from v5.services.lightweight_llm import LightweightLLM
from v5.action_schema import ACTIONS
from v5.utils.config import API_URL, MODEL_NAME, MAX_RESPONSE_LENGTH

@dataclass
class PlanStep:
    """Represents a single step in a plan"""
    step_id: int
    action: str
    arguments: Dict[str, Any]
    reasoning: str
    expected_output: str
    depends_on: Optional[List[int]] = None
    conditional: Optional[str] = None

@dataclass
class Plan:
    """Represents a complete plan"""
    goal: str
    steps: List[PlanStep]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary for JSON serialization"""
        return {
            "goal": self.goal,
            "steps": [asdict(step) for step in self.steps]
        }
    
    def to_json(self) -> str:
        """Convert plan to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

class PlanGenerator:
    """Generates plans from natural language prompts using v5's LLM interface"""
    
    def __init__(self, llm: Optional[LightweightLLM] = None):
        self.llm = llm or LightweightLLM()
        self.action_schema = ACTIONS
    
    def _create_planning_prompt(self, user_prompt: str) -> str:
        """Create the prompt for plan generation using v5's prompt style"""
        
        # Build action schema description in v5's format - more concise
        schema_description = "Available Actions:\n"
        for action_name, action_info in self.action_schema.items():
            schema_description += f"{action_name}: {action_info['description']} (req: {action_info['required_args']}, opt: {action_info['optional_args']})\n"
        
        # Create a more sophisticated planning prompt with reasoning and user interaction
        prompt = (
            f"Create a plan to break down this request into steps using available actions.\n\n"
            f"{schema_description}\n"
            f"Rules: Use only valid actions, include reasoning, use depends_on for dependencies.\n"
            f"For complex requests, add reasoning steps and user confirmation when needed.\n\n"
            f"Example:\n"
            f"User: 'Create dinner event when free tonight'\n"
            f"Output: {{\n"
            f'  "goal": "Create dinner event when free tonight",\n'
            f'  "steps": [\n'
            f'    {{"step_id": 1, "action": "get_events", "arguments": {{"date": "today", "upcoming_only": true}}, "reasoning": "Check calendar for tonight\'s availability", "expected_output": "Events list"}},\n'
            f'    {{"step_id": 2, "action": "reasoning", "arguments": {{"input": "step_1_output", "task": "Find free time slots for dinner tonight"}}, "reasoning": "Analyze events to find available dinner time", "expected_output": "Available time slots", "depends_on": [1]}},\n'
            f'    {{"step_id": 3, "action": "user_confirmation", "arguments": {{"question": "I found free time at 7:00 PM. Should I create the dinner event?", "options": ["yes", "no", "different_time"]}}, "reasoning": "Get user confirmation before creating event", "expected_output": "User confirmation", "depends_on": [2]}},\n'
            f'    {{"step_id": 4, "action": "create_event", "arguments": {{"title": "Dinner", "start_time": "user_confirmed_time"}}, "reasoning": "Create dinner event at confirmed time", "expected_output": "Event created", "depends_on": [3], "conditional": "If user confirmed"}}\n'
            f'  ]\n'
            f'}}\n\n'
            f"User: 'What's my schedule tomorrow and create a note about it'\n"
            f"Output: {{\n"
            f'  "goal": "Get tomorrow\'s schedule and create a note about it",\n'
            f'  "steps": [\n'
            f'    {{"step_id": 1, "action": "get_events", "arguments": {{"date": "tomorrow"}}, "reasoning": "Get all events scheduled for tomorrow", "expected_output": "List of tomorrow\'s events"}},\n'
            f'    {{"step_id": 2, "action": "reasoning", "arguments": {{"input": "step_1_output", "task": "Summarize tomorrow\'s schedule"}}, "reasoning": "Create a summary of tomorrow\'s events", "expected_output": "Schedule summary", "depends_on": [1]}},\n'
            f'    {{"step_id": 3, "action": "create_note", "arguments": {{"title": "Tomorrow\'s Schedule", "content": "step_2_output"}}, "reasoning": "Create a note with the schedule summary", "expected_output": "Note created", "depends_on": [2]}}\n'
            f'  ]\n'
            f'}}\n\n'
            f"User: '{user_prompt}'\n"
            f"Output:"
        )
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM using v5's LightweightLLM interface with increased timeout"""
        start_time = time.time()
        
        # Create a custom LLM call with longer timeout for plan generation
        messages = [
            {"role": "system", "content": "You are a planning assistant. Respond with only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        payload = {
            "model": self.llm.model_name,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.1,
            "stream": False
        }
        
        try:
            import requests
            response = requests.post(
                f"{self.llm.api_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30  # Increased timeout for plan generation
            )
            response.raise_for_status()
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"].strip()
            
            elapsed = (time.time() - start_time) * 1000
            print(f"[DEBUG] LLM raw response for plan generation: {llm_response}")
            print(f"[TIMING] LLM plan generation took {elapsed:.1f} ms")
            return llm_response
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            print(f"[DEBUG] LLM call failed: {str(e)}")
            print(f"[TIMING] LLM plan generation took {elapsed:.1f} ms")
            raise Exception(f"LLM API call failed: {str(e)}")
    
    def _validate_plan(self, plan_dict: Dict[str, Any]) -> bool:
        """Validate that the generated plan is valid using v5's action schema"""
        try:
            # Check required fields
            if "goal" not in plan_dict or "steps" not in plan_dict:
                print("[DEBUG] Missing required fields 'goal' or 'steps'")
                return False
            
            # Define special planning actions that aren't in v5's schema
            planning_actions = {
                "reasoning": {
                    "description": "Analyze previous step output and perform reasoning",
                    "required_args": ["input", "task"],
                    "optional_args": []
                },
                "user_confirmation": {
                    "description": "Ask user for confirmation or input",
                    "required_args": ["question"],
                    "optional_args": ["options"]
                }
            }
            
            # Validate each step
            for step in plan_dict["steps"]:
                required_fields = ["step_id", "action", "arguments", "reasoning", "expected_output"]
                for field in required_fields:
                    if field not in step:
                        print(f"[DEBUG] Missing required field '{field}' in step {step.get('step_id', 'unknown')}")
                        return False
                
                # Check if action exists in v5's action schema or planning actions
                if step["action"] not in self.action_schema and step["action"] not in planning_actions:
                    print(f"[DEBUG] Unknown action '{step['action']}' in step {step['step_id']}")
                    return False
                
                # Check if arguments match action schema
                if step["action"] in self.action_schema:
                    action_info = self.action_schema[step["action"]]
                else:
                    action_info = planning_actions[step["action"]]
                
                required_args = action_info["required_args"]
                optional_args = action_info["optional_args"]
                all_valid_args = required_args + optional_args
                
                for arg in step["arguments"]:
                    if arg not in all_valid_args:
                        print(f"[DEBUG] Unknown argument '{arg}' for action '{step['action']}' in step {step['step_id']}")
                        return False
            
            return True
            
        except Exception as e:
            print(f"[DEBUG] Plan validation error: {str(e)}")
            return False
    
    def _parse_plan(self, llm_response: str) -> Plan:
        """Parse the LLM response into a Plan object using v5's error handling style"""
        try:
            # Try to extract JSON from the response (v5 style)
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise Exception("No JSON found in LLM response")
            
            json_str = llm_response[start_idx:end_idx]
            plan_dict = json.loads(json_str)
            
            # Validate the plan
            if not self._validate_plan(plan_dict):
                raise Exception("Generated plan is invalid")
            
            # Convert to Plan object
            steps = []
            for step_dict in plan_dict["steps"]:
                step = PlanStep(
                    step_id=step_dict["step_id"],
                    action=step_dict["action"],
                    arguments=step_dict["arguments"],
                    reasoning=step_dict["reasoning"],
                    expected_output=step_dict["expected_output"],
                    depends_on=step_dict.get("depends_on"),
                    conditional=step_dict.get("conditional")
                )
                steps.append(step)
            
            return Plan(
                goal=plan_dict["goal"],
                steps=steps
            )
            
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON parsing error: {str(e)}")
            raise Exception(f"Failed to parse JSON from LLM response: {str(e)}")
        except Exception as e:
            print(f"[DEBUG] Plan parsing error: {str(e)}")
            raise Exception(f"Failed to parse plan: {str(e)}")
    
    def generate_plan(self, user_prompt: str) -> Plan:
        """Generate a plan from a natural language prompt using v5's patterns"""
        print(f"[PLAN] Generating plan for: '{user_prompt}'")
        
        # Create the planning prompt
        prompt = self._create_planning_prompt(user_prompt)
        
        # Call the LLM using v5's interface
        print("[PLAN] Calling LLM for plan generation...")
        llm_response = self._call_llm(prompt)
        
        # Parse and validate the plan
        print("[PLAN] Parsing and validating plan...")
        plan = self._parse_plan(llm_response)
        
        print("[PLAN] Plan generated successfully!")
        return plan

def main():
    """Test the plan generator with v5 integration"""
    generator = PlanGenerator()
    
    # Test cases that match v5's action capabilities
    test_prompts = [
        "Create an event to eat dinner when I'm free tonight",
        "What's my schedule for tomorrow and create a note about it",
        "Add 'buy groceries' to my todo list and show me what's on it",
        "What time is it and what day is today?",
        "Create a note about my meeting tomorrow and add it to my todo list"
    ]
    
    for prompt in test_prompts:
        print("\n" + "="*60)
        print(f"Testing: {prompt}")
        print("="*60)
        
        try:
            plan = generator.generate_plan(prompt)
            print("\nGenerated Plan:")
            print(plan.to_json())
        except Exception as e:
            print(f"[ERROR] {str(e)}")

if __name__ == "__main__":
    main() 