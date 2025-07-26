#!/usr/bin/env python3
"""
Plan Execution Engine for SAM v5
Executes generated plans step by step with real reasoning and action execution.
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import v5 components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'v5'))

from v5.brain.execution import execute_action
from v5.services.lightweight_llm import LightweightLLM
from v5.action_schema import ACTIONS

@dataclass
class ExecutionResult:
    """Result of executing a plan step"""
    step_id: int
    action: str
    success: bool
    output: Any
    error: Optional[str] = None

class PlanExecutor:
    """Executes plans step by step with real reasoning and action execution"""
    
    def __init__(self, llm: Optional[LightweightLLM] = None):
        self.llm = llm or LightweightLLM()
        self.action_schema = ACTIONS
        self.execution_results = {}
        self.user_responses = {}
    
    def _execute_action(self, action: str, arguments: Dict[str, Any]) -> Any:
        """Execute a v5 action and return the result"""
        try:
            print(f"[EXEC] Executing action: {action} with args: {arguments}")
            result = execute_action(action, arguments)
            print(f"[EXEC] Action result: {result}")
            return result
        except Exception as e:
            print(f"[EXEC] Action failed: {str(e)}")
            raise e
    
    def _execute_reasoning(self, arguments: Dict[str, Any], previous_outputs: Dict[int, Any]) -> str:
        """Execute a reasoning step using the LLM"""
        input_data = arguments.get("input", "")
        task = arguments.get("task", "")
        
        # Get the actual input data from previous step
        if input_data.startswith("step_") and input_data.endswith("_output"):
            step_num = int(input_data.split("_")[1])
            actual_input = previous_outputs.get(step_num, "")
        else:
            actual_input = input_data
        
        prompt = f"""You are performing reasoning on this task: {task}

Input data: {actual_input}

Analyze the input data and provide reasoning for the task. Be specific and actionable.
If you're looking for free time, analyze the events and suggest specific available time slots.
If you're summarizing, create a clear summary.

Reasoning:"""
        
        print(f"[REASONING] Task: {task}")
        print(f"[REASONING] Input: {actual_input}")
        
        response = self.llm.generate_response(prompt, max_tokens=500)
        print(f"[REASONING] Output: {response}")
        return response
    
    def _execute_user_confirmation(self, arguments: Dict[str, Any]) -> str:
        """Execute a user confirmation step"""
        question = arguments.get("question", "")
        options = arguments.get("options", [])
        
        print(f"\n[USER] {question}")
        if options:
            print(f"[USER] Options: {', '.join(options)}")
        
        # For now, simulate user response (in real implementation, this would get actual user input)
        # In a real system, this would pause and wait for user input
        user_response = input("Your response: ").strip().lower()
        
        # Store the response for later use
        self.user_responses[len(self.user_responses) + 1] = user_response
        return user_response
    
    def _check_conditional(self, conditional: str, step_id: int) -> bool:
        """Check if a conditional step should be executed"""
        if not conditional:
            return True
        
        # Simple conditional logic
        if "user confirmed" in conditional.lower():
            # Check if user confirmed in the previous step
            user_response = self.user_responses.get(step_id - 1, "")
            return user_response in ["yes", "y", "confirm"]
        
        return True
    
    def _resolve_arguments(self, arguments: Dict[str, Any], previous_outputs: Dict[int, Any]) -> Dict[str, Any]:
        """Resolve dynamic arguments that reference previous step outputs"""
        resolved_args = {}
        
        for key, value in arguments.items():
            if isinstance(value, str) and value.startswith("step_") and value.endswith("_output"):
                # Extract step number and get the actual output
                step_num = int(value.split("_")[1])
                resolved_args[key] = previous_outputs.get(step_num, "")
            elif isinstance(value, str) and "user_confirmed" in value:
                # Replace with actual user response
                user_response = self.user_responses.get(len(self.user_responses), "")
                resolved_args[key] = user_response
            else:
                resolved_args[key] = value
        
        return resolved_args
    
    def execute_plan(self, plan: Dict[str, Any]) -> List[ExecutionResult]:
        """Execute a complete plan step by step"""
        print(f"\n[EXECUTOR] Starting execution of plan: {plan['goal']}")
        print("=" * 60)
        
        steps = plan["steps"]
        results = []
        previous_outputs = {}
        
        for step in steps:
            step_id = step["step_id"]
            action = step["action"]
            arguments = step["arguments"]
            conditional = step.get("conditional")
            
            print(f"\n[EXECUTOR] Executing Step {step_id}: {action}")
            print(f"[EXECUTOR] Reasoning: {step['reasoning']}")
            
            # Check conditional
            if not self._check_conditional(conditional, step_id):
                print(f"[EXECUTOR] Skipping step {step_id} due to conditional: {conditional}")
                results.append(ExecutionResult(
                    step_id=step_id,
                    action=action,
                    success=False,
                    output=None,
                    error=f"Conditional not met: {conditional}"
                ))
                continue
            
            # Resolve dynamic arguments
            resolved_args = self._resolve_arguments(arguments, previous_outputs)
            print(f"[EXECUTOR] Resolved arguments: {resolved_args}")
            
            try:
                # Execute the step based on action type
                if action in self.action_schema:
                    # Execute a v5 action
                    output = self._execute_action(action, resolved_args)
                elif action == "reasoning":
                    # Execute reasoning
                    output = self._execute_reasoning(resolved_args, previous_outputs)
                elif action == "user_confirmation":
                    # Execute user confirmation
                    output = self._execute_user_confirmation(resolved_args)
                else:
                    raise Exception(f"Unknown action type: {action}")
                
                # Store the result
                result = ExecutionResult(
                    step_id=step_id,
                    action=action,
                    success=True,
                    output=output
                )
                results.append(result)
                previous_outputs[step_id] = output
                
                print(f"[EXECUTOR] Step {step_id} completed successfully")
                
            except Exception as e:
                print(f"[EXECUTOR] Step {step_id} failed: {str(e)}")
                result = ExecutionResult(
                    step_id=step_id,
                    action=action,
                    success=False,
                    output=None,
                    error=str(e)
                )
                results.append(result)
                previous_outputs[step_id] = f"ERROR: {str(e)}"
        
        print("\n" + "=" * 60)
        print("[EXECUTOR] Plan execution completed")
        return results

def main():
    """Test the plan executor"""
    from plan_generator import PlanGenerator
    
    # Generate a plan
    generator = PlanGenerator()
    plan = generator.generate_plan("Create an event to eat dinner when I'm free tonight")
    
    # Execute the plan
    executor = PlanExecutor()
    results = executor.execute_plan(plan.to_dict())
    
    # Print results
    print("\nExecution Results:")
    for result in results:
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        print(f"Step {result.step_id} ({result.action}): {status}")
        if result.error:
            print(f"  Error: {result.error}")
        else:
            print(f"  Output: {result.output}")

if __name__ == "__main__":
    main() 