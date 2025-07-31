#!/usr/bin/env python3
"""
Plan Executor - Executes structured plans with action and reasoning steps
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from v5.brain.plan_memory import PlanMemory
from v5.brain.reasoning_engine import ReasoningEngine
from v5.brain.plan_validator import PlanValidator

class PlanExecutor:
    """
    Executes structured plans step by step, handling both action and reasoning steps.
    """
    
    def __init__(self, reasoning_engine: ReasoningEngine, action_executor, actions_schema: Dict[str, Any]):
        """
        Initialize the plan executor.
        
        Args:
            reasoning_engine: Engine for executing reasoning steps
            action_executor: Function for executing action steps
            actions_schema: Schema of available actions
        """
        self.reasoning_engine = reasoning_engine
        self.action_executor = action_executor
        self.actions_schema = actions_schema
        self.validator = PlanValidator()
        self.memory = PlanMemory()
    
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete plan step by step.
        
        Args:
            plan: The plan to execute
            
        Returns:
            Dictionary with execution results and final memory state
        """
        print(f"[AGENT-DEBUG] Starting plan execution for goal: {plan.get('goal', 'Unknown')}")
        
        # Validate plan first
        print(f"[AGENT-DEBUG] Validating plan before execution...")
        is_valid, errors = self.validator.validate_plan(plan, self.actions_schema)
        print(f"[AGENT-DEBUG] Plan validation result: {is_valid}")
        if not is_valid:
            print(f"[AGENT-DEBUG] Plan validation failed with errors: {errors}")
            return {
                "success": False,
                "error": "Plan validation failed",
                "validation_errors": errors,
                "goal": plan.get("goal"),
                "results": [],
                "final_memory": {}
            }
        
        # Clear memory for new execution
        print(f"[AGENT-DEBUG] Clearing memory for new execution...")
        self.memory.clear()
        
        results = []
        execution_start = time.time()
        
        try:
            print(f"[AGENT-DEBUG] Executing {len(plan['steps'])} steps...")
            for i, step in enumerate(plan["steps"], 1):
                print(f"[AGENT-DEBUG] Executing step {i}/{len(plan['steps'])}...")
                step_result = self._execute_step(step, i)
                results.append(step_result)
                
                print(f"[AGENT-DEBUG] Step {i} completed. Type: {step_result.get('step_type', 'unknown')}")
                if step_result.get("error"):
                    print(f"[AGENT-DEBUG] Step {i} failed with error: {step_result['error']}")
                
                # Store result immediately if save_as is specified
                if "save_as" in step:
                    # Store only the actual result, not the entire step result object
                    actual_result = step_result.get("result") if isinstance(step_result, dict) else step_result
                    self.memory.store(step["save_as"], actual_result)
                    print(f"[AGENT-DEBUG] Stored result in memory as '{step['save_as']}': {str(actual_result)[:100]}")
                
                # Check for step failure
                if step_result.get("error"):
                    print(f"[AGENT-DEBUG] Plan execution failed at step {i}")
                    return {
                        "success": False,
                        "error": f"Step {i} failed: {step_result['error']}",
                        "goal": plan["goal"],
                        "results": results,
                        "final_memory": self.memory.get_context(),
                        "execution_time": time.time() - execution_start
                    }
            
            execution_time = time.time() - execution_start
            print(f"[AGENT-DEBUG] All steps completed successfully in {execution_time:.2f} seconds")
            
            return {
                "success": True,
                "goal": plan["goal"],
                "results": results,
                "final_memory": self.memory.get_context(),
                "execution_time": execution_time,
                "memory_summary": self.memory.get_execution_summary()
            }
            
        except Exception as e:
            execution_time = time.time() - execution_start
            print(f"[AGENT-DEBUG] Exception during plan execution: {e}")
            import traceback
            print(f"[AGENT-DEBUG] Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "goal": plan.get("goal"),
                "results": results,
                "final_memory": self.memory.get_context(),
                "execution_time": execution_time
            }
    
    def _execute_step(self, step: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """
        Execute a single step (action or reasoning).
        
        Args:
            step: The step to execute
            step_number: Step number for logging
            
        Returns:
            Dictionary with step result and metadata
        """
        step_start = time.time()
        
        try:
            if "action" in step:
                # Execute action step
                result = self._execute_action_step(step, step_number)
            elif "reasoning" in step:
                # Execute reasoning step
                result = self._execute_reasoning_step(step, step_number)
            elif "condition" in step:
                # Execute conditional step
                result = self._execute_conditional_step(step, step_number)
            else:
                result = {
                    "error": "Step must have either 'action', 'reasoning', or 'condition'",
                    "step_type": "unknown"
                }
            
            step_time = time.time() - step_start
            result["execution_time"] = step_time
            result["step_number"] = step_number
            
            return result
            
        except Exception as e:
            step_time = time.time() - step_start
            return {
                "error": str(e),
                "step_type": "error",
                "execution_time": step_time,
                "step_number": step_number
            }
    
    def _execute_action_step(self, step: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """
        Execute an action step.
        
        Args:
            step: The action step to execute
            step_number: Step number for logging
            
        Returns:
            Dictionary with action result
        """
        action_name = step["action"]
        args = step.get("args", {})
        
        # Substitute template variables in arguments
        substituted_args = {}
        for key, value in args.items():
            if isinstance(value, str):
                substituted_value = self.memory.substitute_templates(value)
                substituted_args[key] = substituted_value
            else:
                substituted_args[key] = value
        
        # Check for missing template variables
        missing_vars = []
        for key, value in substituted_args.items():
            if isinstance(value, str):
                missing_vars.extend(self.memory.validate_template_variables(value))
        
        if missing_vars:
            return {
                "error": f"Missing template variables: {missing_vars}",
                "step_type": "action",
                "action": action_name,
                "args": substituted_args
            }
        
        # Execute the action
        try:
            result = self.action_executor(action_name, substituted_args)
            return {
                "step_type": "action",
                "action": action_name,
                "args": substituted_args,
                "result": result
            }
        except Exception as e:
            return {
                "error": f"Action execution failed: {str(e)}",
                "step_type": "action",
                "action": action_name,
                "args": substituted_args
            }
    
    def _execute_reasoning_step(self, step: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """
        Execute a reasoning step.
        
        Args:
            step: The reasoning step to execute
            step_number: Step number for logging
            
        Returns:
            Dictionary with reasoning result
        """
        reasoning_instruction = step["reasoning"]
        
        # Execute reasoning
        try:
            result = self.reasoning_engine.execute_reasoning_step(reasoning_instruction, self.memory)
            
            # Validate reasoning result
            is_valid = self.reasoning_engine.validate_reasoning_result(result, reasoning_instruction)
            
            return {
                "step_type": "reasoning",
                "instruction": reasoning_instruction,
                "result": result,
                "is_valid": is_valid
            }
        except Exception as e:
            return {
                "error": f"Reasoning execution failed: {str(e)}",
                "step_type": "reasoning",
                "instruction": reasoning_instruction
            }
    
    def _execute_conditional_step(self, step: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """
        Execute a conditional step.
        
        Args:
            step: The conditional step to execute
            step_number: Step number for logging
            
        Returns:
            Dictionary with conditional result
        """
        condition = step["condition"]
        next_id = step["next_id"]
        
        # Evaluate the condition using the reasoning engine
        try:
            # Parse the condition (e.g., "${has_homework_note} == true")
            # For now, handle simple boolean conditions
            if "==" in condition:
                var_name, expected_value = condition.split("==")
                var_name = var_name.strip().replace("${", "").replace("}", "")
                expected_value = expected_value.strip()
                
                # Get the actual value from memory
                actual_value = self.memory.retrieve(var_name)
                
                # Convert expected value to appropriate type
                if expected_value.lower() == "true":
                    expected_value = True
                elif expected_value.lower() == "false":
                    expected_value = False
                elif expected_value.isdigit():
                    expected_value = int(expected_value)
                
                # Compare values
                condition_result = actual_value == expected_value
                
                return {
                    "step_type": "conditional",
                    "condition": condition,
                    "next_id": next_id,
                    "result": condition_result,
                    "evaluated_condition": f"{var_name} == {actual_value} (expected: {expected_value})"
                }
            else:
                # For more complex conditions, use reasoning engine
                result = self.reasoning_engine.execute_reasoning_step(f"Evaluate: {condition}", self.memory)
                
                return {
                    "step_type": "conditional",
                    "condition": condition,
                    "next_id": next_id,
                    "result": result,
                    "evaluated_condition": result
                }
                
        except Exception as e:
            return {
                "error": f"Conditional execution failed: {str(e)}",
                "step_type": "conditional",
                "condition": condition,
                "next_id": next_id
            }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current execution state.
        
        Returns:
            Dictionary with execution summary
        """
        return {
            "memory_summary": self.memory.get_execution_summary(),
            "variables": list(self.memory.variables.keys()),
            "variable_count": len(self.memory.variables)
        }
    
    def reset(self):
        """Reset the executor state."""
        self.memory.clear() 