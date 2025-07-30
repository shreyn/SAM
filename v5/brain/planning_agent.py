#!/usr/bin/env python3
"""
Planning Agent - Generates structured JSON plans from user goals
"""

import json
from typing import Dict, Any, Optional, Tuple
from v5.brain.plan_validator import PlanValidator

class PlanningAgent:
    """
    Generates structured execution plans from natural language goals.
    Uses LLM to decompose complex goals into step-by-step plans.
    """
    
    def __init__(self, llm_client=None):
        # Use provided LLM client or create default
        if llm_client is None:
            from v5.brain.unified_llm_client import UnifiedLLMClient
            self.llm_client = UnifiedLLMClient()
        else:
            self.llm_client = llm_client
        self.validator = PlanValidator()
        
    def generate_plan(self, user_goal: str, actions_schema: Dict[str, Any], stream: bool = False) -> Tuple[Dict[str, Any], bool, list]:
        """
        Generate a structured plan from a user goal.
        
        Args:
            user_goal: Natural language description of what the user wants
            actions_schema: Dictionary of available actions and their specifications
            stream: Whether to stream the LLM response in real-time
            
        Returns:
            Tuple of (plan_dict, is_valid, error_messages)
        """
        try:
            # Generate plan using unified LLM client
            plan, is_valid, errors = self.llm_client.generate_plan(user_goal, actions_schema, stream=stream)
            
            return plan, is_valid, errors
            
        except Exception as e:
            return {"error": str(e)}, False, [f"Planning failed: {str(e)}"] 