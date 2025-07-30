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
        # Validate plan first
        is_valid, errors = self.validator.validate_plan(plan, self.actions_schema)
        if not is_valid:
            return {
                "success": False,
                "error": "Plan validation failed",
                "validation_errors": errors,
                "goal": plan.get("goal"),
                "results": [],
                "final_memory": {}
            }
        
        # Clear memory for new execution
        self.memory.clear()
        
        results = []
        execution_start = time.time()
        
        try:
            for i, step in enumerate(plan["steps"], 1):
                step_result = self._execute_step(step, i)
                results.append(step_result)
                
                # Store result immediately if save_as is specified
                if "save_as" in step:
                    # Store only the actual result, not the entire step result object
                    actual_result = step_result.get("result") if isinstance(step_result, dict) else step_result
                    self.memory.store(step["save_as"], actual_result)
                
                # Check for step failure
                if step_result.get("error"):
                    return {
                        "success": False,
                        "error": f"Step {i} failed: {step_result['error']}",
                        "goal": plan["goal"],
                        "results": results,
                        "final_memory": self.memory.get_context(),
                        "execution_time": time.time() - execution_start
                    }
            
            execution_time = time.time() - execution_start
            
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
            else:
                result = {
                    "error": "Step must have either 'action' or 'reasoning'",
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