#!/usr/bin/env python3
"""
Plan Validator - Validates generated plans for correctness and executability
"""

import re
from typing import Dict, Any, List, Tuple

class PlanValidator:
    """
    Validates that generated plans are well-formed and executable.
    Checks structure, action validity, argument consistency, and logical flow.
    """
    
    def __init__(self):
        self.template_pattern = r'\$\{([^}]+)\}'
    
    def validate_plan(self, plan: Dict[str, Any], actions_schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of a generated plan.
        
        Args:
            plan: The plan dictionary to validate
            actions_schema: Available actions and their specifications
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Basic structure validation
        structure_errors = self._validate_structure(plan)
        errors.extend(structure_errors)
        
        # If basic structure is invalid, stop here
        if structure_errors:
            return False, errors
        
        # Validate each step
        step_errors = self._validate_steps(plan["steps"], actions_schema)
        errors.extend(step_errors)
        
        # Validate memory references
        memory_errors = self._validate_memory_references(plan["steps"])
        errors.extend(memory_errors)
        
        # Validate logical flow
        flow_errors = self._validate_logical_flow(plan["steps"])
        errors.extend(flow_errors)
        
        return len(errors) == 0, errors
    
    def _validate_structure(self, plan: Dict[str, Any]) -> List[str]:
        """Validate basic plan structure."""
        errors = []
        
        # Check required top-level keys
        required_keys = ["goal", "steps"]
        for key in required_keys:
            if key not in plan:
                errors.append(f"Missing required key: '{key}'")
        
        # Check goal is a string
        if "goal" in plan and not isinstance(plan["goal"], str):
            errors.append("'goal' must be a string")
        
        # Check steps is a list
        if "steps" in plan:
            if not isinstance(plan["steps"], list):
                errors.append("'steps' must be a list")
            elif len(plan["steps"]) == 0:
                errors.append("'steps' cannot be empty")
        
        # Check reasoning field if present
        if "reasoning" in plan and not isinstance(plan["reasoning"], str):
            errors.append("'reasoning' must be a string")
        
        return errors
    
    def _validate_steps(self, steps: List[Dict[str, Any]], actions_schema: Dict[str, Any]) -> List[str]:
        """Validate individual steps in the plan."""
        errors = []
        
        for i, step in enumerate(steps):
            step_errors = self._validate_single_step(step, i, actions_schema)
            errors.extend(step_errors)
        
        return errors
    
    def _validate_single_step(self, step: Dict[str, Any], step_index: int, actions_schema: Dict[str, Any]) -> List[str]:
        """Validate a single step."""
        errors = []
        
        # Check step is a dictionary
        if not isinstance(step, dict):
            errors.append(f"Step {step_index}: must be a dictionary")
            return errors
        
        # Check for step ID
        if "id" not in step:
            errors.append(f"Step {step_index}: missing 'id' field")
        
        # Check step type (action or reasoning)
        has_action = "action" in step
        has_reasoning = "reasoning" in step
        
        if not has_action and not has_reasoning:
            errors.append(f"Step {step_index}: must have either 'action' or 'reasoning'")
        elif has_action and has_reasoning:
            errors.append(f"Step {step_index}: cannot have both 'action' and 'reasoning'")
        
        # Validate action steps
        if has_action:
            action_errors = self._validate_action_step(step, step_index, actions_schema)
            errors.extend(action_errors)
        
        # Validate reasoning steps
        if has_reasoning:
            reasoning_errors = self._validate_reasoning_step(step, step_index)
            errors.extend(reasoning_errors)
        
        # Check save_as field
        if "save_as" in step:
            if not isinstance(step["save_as"], str):
                errors.append(f"Step {step_index}: 'save_as' must be a string")
            elif not step["save_as"].strip():
                errors.append(f"Step {step_index}: 'save_as' cannot be empty")
        
        return errors
    
    def _validate_action_step(self, step: Dict[str, Any], step_index: int, actions_schema: Dict[str, Any]) -> List[str]:
        """Validate an action step."""
        errors = []
        
        action_name = step["action"]
        
        # Check action exists in schema
        if action_name not in actions_schema:
            errors.append(f"Step {step_index}: unknown action '{action_name}'")
            return errors
        
        # Check arguments
        if "args" in step:
            if not isinstance(step["args"], dict):
                errors.append(f"Step {step_index}: 'args' must be a dictionary")
            else:
                arg_errors = self._validate_action_args(step["args"], action_name, actions_schema, step_index)
                errors.extend(arg_errors)
        
        return errors
    
    def _validate_action_args(self, args: Dict[str, Any], action_name: str, actions_schema: Dict[str, Any], step_index: int) -> List[str]:
        """Validate arguments for an action."""
        errors = []
        
        action_spec = actions_schema[action_name]
        required_args = action_spec.get("required_args", [])
        optional_args = action_spec.get("optional_args", [])
        all_valid_args = required_args + optional_args
        
        # Check for invalid arguments
        for arg_name in args:
            if arg_name not in all_valid_args:
                errors.append(f"Step {step_index}: invalid argument '{arg_name}' for action '{action_name}'")
        
        # Check required arguments are provided
        for required_arg in required_args:
            if required_arg not in args:
                errors.append(f"Step {step_index}: missing required argument '{required_arg}' for action '{action_name}'")
        
        # Validate argument values (basic type checking)
        for arg_name, arg_value in args.items():
            if not isinstance(arg_value, (str, int, float, bool)) and arg_value is not None:
                errors.append(f"Step {step_index}: argument '{arg_name}' must be a primitive type")
        
        return errors
    
    def _validate_reasoning_step(self, step: Dict[str, Any], step_index: int) -> List[str]:
        """Validate a reasoning step."""
        errors = []
        
        reasoning = step["reasoning"]
        
        if not isinstance(reasoning, str):
            errors.append(f"Step {step_index}: 'reasoning' must be a string")
        elif not reasoning.strip():
            errors.append(f"Step {step_index}: 'reasoning' cannot be empty")
        
        return errors
    
    def _validate_memory_references(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Validate that memory references are properly defined before use."""
        errors = []
        
        # Track defined variables
        defined_vars = set()
        
        for i, step in enumerate(steps):
            # Check for undefined variable references in arguments
            if "args" in step and isinstance(step["args"], dict):
                for arg_name, arg_value in step["args"].items():
                    if isinstance(arg_value, str):
                        template_vars = re.findall(self.template_pattern, arg_value)
                        for var in template_vars:
                            if var not in defined_vars:
                                errors.append(f"Step {i}: references undefined variable '${var}' in argument '{arg_name}'")
            
            # Add newly defined variables
            if "save_as" in step and isinstance(step["save_as"], str):
                defined_vars.add(step["save_as"])
        
        return errors
    
    def _validate_logical_flow(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Validate logical flow of the plan."""
        errors = []
        
        # Check for reasonable step count
        if len(steps) > 10:
            errors.append("Plan has too many steps (max 10)")
        
        # Check for circular dependencies (basic check)
        # This is a simplified check - a full dependency analysis would be more complex
        defined_vars = set()
        for i, step in enumerate(steps):
            if "save_as" in step:
                var_name = step["save_as"]
                if var_name in defined_vars:
                    errors.append(f"Step {i}: variable '{var_name}' is defined multiple times")
                defined_vars.add(var_name)
        
        return errors
    
    def extract_template_variables(self, text: str) -> List[str]:
        """Extract template variables from a string."""
        return re.findall(self.template_pattern, text)
    
    def validate_template_syntax(self, text: str) -> List[str]:
        """Validate template syntax in a string."""
        errors = []
        
        # Check for unmatched braces
        open_braces = text.count('${')
        close_braces = text.count('}')
        
        if open_braces != close_braces:
            errors.append("Mismatched braces in template")
        
        # Check for empty variable names
        empty_vars = re.findall(r'\$\{\s*\}', text)
        if empty_vars:
            errors.append("Empty variable names in template")
        
        return errors 