#!/usr/bin/env python3
"""
Reasoning Engine - Executes reasoning steps with access to stored memory
"""

import json
import time
from typing import Any, Dict, Optional
from v5.brain.plan_memory import PlanMemory

class ReasoningEngine:
    """
    Executes reasoning steps using LLM with access to stored memory context.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the reasoning engine.
        
        Args:
            llm_client: Unified LLM client for generating responses (optional)
        """
        # Use provided LLM client or create default
        if llm_client is None:
            from v5.brain.unified_llm_client import UnifiedLLMClient
            self.llm = UnifiedLLMClient()
        else:
            self.llm = llm_client
    
    def execute_reasoning_step(self, reasoning_instruction: str, memory: PlanMemory) -> Any:
        """
        Execute a reasoning step with access to stored memory.
        
        Args:
            reasoning_instruction: The reasoning prompt (e.g., "Find first available 1-hour slot...")
            memory: Current memory state with all stored variables
            
        Returns:
            The result of the reasoning (e.g., "7:00 PM")
        """
        try:
            # Execute reasoning using unified LLM client
            result = self.llm.execute_reasoning(reasoning_instruction, memory.format_for_llm())
            
            return result
            
        except Exception as e:
            return f"REASONING_ERROR: {str(e)}"
    
    def validate_reasoning_result(self, result: Any, instruction: str) -> bool:
        """
        Basic validation of reasoning results.
        
        Args:
            result: The reasoning result to validate
            instruction: The original reasoning instruction
            
        Returns:
            True if result seems reasonable, False otherwise
        """
        # Check for error indicators
        if isinstance(result, str):
            if result.upper() in ["INSUFFICIENT_DATA", "ERROR", "REASONING_ERROR"]:
                return False
            if result.upper().startswith("ERROR:"):
                return False
        
        # Check for empty results
        if result is None or result == "":
            return False
        
        # Basic length check for string results
        if isinstance(result, str) and len(result) > 1000:
            return False
        
        return True 