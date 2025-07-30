#!/usr/bin/env python3
"""
Plan Memory - Stores variables and context across plan execution
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class PlanMemory:
    """
    Memory store for plan execution that maintains variables and context
    across reasoning and action steps.
    """
    
    def __init__(self):
        self.variables = {}  # e.g., {"events_list": [...], "free_slot": "7:00 PM"}
        self.execution_history = []
        self.created_at = datetime.now()
    
    def store(self, variable_name: str, value: Any) -> None:
        """
        Store a variable in memory.
        
        Args:
            variable_name: Name of the variable to store
            value: Value to store (can be any JSON-serializable type)
        """
        self.variables[variable_name] = value
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "store",
            "variable": variable_name,
            "value": str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
        })
    
    def retrieve(self, variable_name: str) -> Any:
        """
        Retrieve a variable from memory.
        
        Args:
            variable_name: Name of the variable to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        return self.variables.get(variable_name)
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get a copy of all stored variables.
        
        Returns:
            Dictionary of all stored variables
        """
        return self.variables.copy()
    
    def has_variable(self, variable_name: str) -> bool:
        """
        Check if a variable exists in memory.
        
        Args:
            variable_name: Name of the variable to check
            
        Returns:
            True if variable exists, False otherwise
        """
        return variable_name in self.variables
    
    def clear(self) -> None:
        """Clear all variables and history."""
        self.variables.clear()
        self.execution_history.clear()
        self.created_at = datetime.now()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current execution state.
        
        Returns:
            Dictionary with memory summary
        """
        return {
            "created_at": self.created_at.isoformat(),
            "variable_count": len(self.variables),
            "variables": list(self.variables.keys()),
            "execution_steps": len(self.execution_history),
            "recent_history": self.execution_history[-5:] if self.execution_history else []
        }
    
    def format_for_llm(self) -> str:
        """
        Format memory contents for LLM consumption.
        
        Returns:
            Formatted string representation of memory
        """
        if not self.variables:
            return "No data available"
        
        formatted_items = []
        for key, value in self.variables.items():
            # Format the value for readability
            formatted_value = self._format_value_for_llm(value)
            formatted_items.append(f"  {key}: {formatted_value}")
        
        return "\n".join(formatted_items)
    
    def _format_value_for_llm(self, value: Any) -> str:
        """
        Format a value for LLM consumption.
        
        Args:
            value: The value to format
            
        Returns:
            Formatted string representation
        """
        if isinstance(value, list):
            if not value:
                return "[]"
            # Format list items
            formatted_items = []
            for item in value:
                if isinstance(item, dict):
                    # Format dict items nicely
                    item_str = json.dumps(item, indent=2, default=str)
                    formatted_items.append(item_str)
                else:
                    formatted_items.append(str(item))
            return "[\n" + ",\n".join(f"    {item}" for item in formatted_items) + "\n  ]"
        elif isinstance(value, dict):
            return json.dumps(value, indent=2, default=str)
        elif isinstance(value, str):
            # Truncate very long strings
            if len(value) > 200:
                return value[:200] + "..."
            return value
        else:
            return str(value)
    
    def substitute_templates(self, text: str) -> str:
        """
        Substitute template variables in text with their values.
        
        Args:
            text: Text containing template variables like ${variable_name}
            
        Returns:
            Text with variables substituted
        """
        import re
        
        def replace_template(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return str(self.variables[var_name])
            else:
                return match.group(0)  # Keep original if variable not found
        
        # Replace ${variable} patterns
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_template, text)
    
    def validate_template_variables(self, text: str) -> List[str]:
        """
        Check if all template variables in text exist in memory.
        
        Args:
            text: Text containing template variables
            
        Returns:
            List of missing variable names
        """
        import re
        
        pattern = r'\$\{([^}]+)\}'
        template_vars = re.findall(pattern, text)
        
        missing_vars = []
        for var_name in template_vars:
            if var_name not in self.variables:
                missing_vars.append(var_name)
        
        return missing_vars 