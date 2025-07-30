#!/usr/bin/env python3
"""
Unified Orchestrator - Handles both simple actions and agentic workflows
Provides a single entry point for all user requests with clear flow separation
"""

import time
from typing import Dict, Any, Optional, Tuple
from v5.action_schema import ACTIONS
from v5.brain.session_state import SessionState
from v5.brain.unified_llm_client import UnifiedLLMClient
from v5.brain.execution import execute_action
from v5.brain.planning_agent import PlanningAgent
from v5.brain.reasoning_engine import ReasoningEngine
from v5.brain.plan_executor import PlanExecutor
from v5.commands.registry import get_command_handler

class UnifiedOrchestrator:
    """
    Unified orchestrator that handles both simple actions and complex agentic workflows.
    Provides clear separation between fast slot-filling and rich planning/reasoning.
    """
    
    def __init__(self, llm_client: Optional[UnifiedLLMClient] = None):
        """
        Initialize the unified orchestrator.
        
        Args:
            llm_client: Unified LLM client (creates default if not provided)
        """
        # Initialize LLM client
        self.llm_client = llm_client or UnifiedLLMClient()
        
        # Initialize memory systems
        self.simple_memory = SessionState()  # Fast, lightweight for simple actions
        self.agent_memory = None  # Will be initialized when needed for agentic workflows
        
        # Initialize agentic components (lazy-loaded)
        self.planning_agent = None
        self.reasoning_engine = None
        self.plan_executor = None
        
        # State tracking
        self.current_mode = None  # 'simple', 'agent', or None
        self.current_action = None
    
    # ============================================================================
    # MAIN ENTRY POINT
    # ============================================================================
    
    def process_user_input(self, user_input: str, intent: str = None, action_name: str = None) -> str:
        """
        Main entry point for processing user input.
        
        Args:
            user_input: User's natural language input
            intent: Pre-classified intent ('simple', 'agent', 'query')
            action_name: Pre-classified action name (for simple intent)
            
        Returns:
            Response string or follow-up question
        """
        # Check for commands first
        command_result = self._handle_commands(user_input)
        if command_result:
            return command_result
        
        # Determine intent and action if not provided
        if intent is None or action_name is None:
            intent, action_name = self._classify_intent_and_action(user_input)
        
        # Route to appropriate handler
        if intent == "simple":
            return self._handle_simple_action(user_input, action_name)
        elif intent == "agent":
            return self._handle_agentic_request(user_input)
        elif intent == "query":
            return self._handle_general_query(user_input)
        else:
            return "Sorry, I couldn't understand your request."
    
    # ============================================================================
    # COMMAND HANDLING
    # ============================================================================
    
    def _handle_commands(self, user_input: str) -> Optional[str]:
        """
        Handle system commands (cancel, shutdown, etc.).
        
        Args:
            user_input: User input to check for commands
            
        Returns:
            Command response or None if not a command
        """
        command_entry = get_command_handler(user_input)
        if command_entry:
            handler = command_entry["handler"]
            interrupting = command_entry["interrupting"]
            
            if handler.__name__ == 'handle_cancel':
                # Cancel current task and reset state
                self._reset_current_task()
                result = handler(self.simple_memory)
            else:
                # Shutdown command
                result = handler()
            
            if result and result.message:
                return result.message
            return "Command executed."
        
        return None
    
    def _reset_current_task(self):
        """Reset current task state."""
        if self.current_mode == "simple":
            self.simple_memory.reset()
        elif self.current_mode == "agent":
            if self.plan_executor:
                self.plan_executor.reset()
        
        self.current_mode = None
        self.current_action = None
    
    # ============================================================================
    # INTENT AND ACTION CLASSIFICATION
    # ============================================================================
    
    def _classify_intent_and_action(self, user_input: str) -> Tuple[str, Optional[str]]:
        """
        Classify user input to determine intent and action.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Tuple of (intent, action_name)
        """
        # This method is a fallback - in practice, intent and action classification
        # should be done in main.py using the ML classifiers and passed to this method
        
        # Simple heuristic: if it contains action keywords, it's likely simple
        action_keywords = ["create", "add", "show", "get", "read", "edit", "delete", "clear"]
        if any(keyword in user_input.lower() for keyword in action_keywords):
            # This is a simplified version - in practice, use the ML classifier
            return "simple", None  # Action name would be determined by ML classifier
        else:
            return "agent", None
    
    # ============================================================================
    # SIMPLE ACTION HANDLING (Fast slot-filling)
    # ============================================================================
    
    def _handle_simple_action(self, user_input: str, action_name: str) -> str:
        """
        Handle simple actions with fast slot-filling.
        
        Args:
            user_input: User's natural language input
            action_name: Name of the action to execute
            
        Returns:
            Response string or follow-up question
        """
        # Set current mode
        self.current_mode = "simple"
        self.current_action = action_name
        
        # Get action requirements
        if action_name not in ACTIONS:
            return f"Sorry, I don't know how to do '{action_name}'."
        
        action_spec = ACTIONS[action_name]
        required_args = action_spec["required_args"]
        optional_args = action_spec["optional_args"]
        
        # Check if we're in the middle of slot-filling
        if self.simple_memory.action_name and self.simple_memory.action_name != action_name:
            # User started a new action while in slot-filling mode
            self.simple_memory.reset()
        
        # Start new action if needed
        if not self.simple_memory.action_name:
            self.simple_memory.start_new_action(action_name, required_args, optional_args)
        
        # Only extract arguments if the action actually has arguments
        if required_args or optional_args:
            # Extract arguments from user input
            extracted_args = self.llm_client.extract_arguments(user_input, action_name)
            collected_args = {k: v for k, v in extracted_args.items() if v is not None}
            
            # Update memory with extracted arguments
            for arg_name, value in collected_args.items():
                self.simple_memory.update_argument(arg_name, value)
        else:
            # No arguments needed, execute immediately
            result = execute_action(action_name, {})
            self.simple_memory.reset()
            self.current_mode = None
            self.current_action = None
            return result
        
        # Check for missing required arguments
        missing_args = [arg for arg in required_args if arg not in self.simple_memory.collected_args]
        
        if missing_args:
            # Need to ask for missing arguments
            missing_arg = missing_args[0]
            followup_q = self.llm_client.generate_followup_question(missing_arg, action_name)
            self.simple_memory.add_history(user_input, followup_q)
            return followup_q
        else:
            # All required arguments collected, execute action
            result = execute_action(action_name, self.simple_memory.collected_args)
            self.simple_memory.reset()
            self.current_mode = None
            self.current_action = None
            return result
    
    def process_simple_followup(self, user_reply: str) -> str:
        """
        Process user reply to a follow-up question for simple actions.
        
        Args:
            user_reply: User's reply to the follow-up question
            
        Returns:
            Response string or next follow-up question
        """
        if self.current_mode != "simple" or not self.simple_memory.action_name:
            return "No action in progress. Please start an action."
        
        # Get the missing argument we're asking for
        missing_arg = self.simple_memory.get_next_missing_arg()
        if not missing_arg:
            return "Unexpected state: no missing arguments."
        
        # Extract value from user reply
        value = self.llm_client.extract_argument_from_reply(
            user_reply, missing_arg, self.simple_memory.action_name
        )
        
        if value is not None and (not isinstance(value, str) or value.strip()):
            # Valid value extracted
            self.simple_memory.update_argument(missing_arg, value)
            self.simple_memory.add_history(user_reply)
            
            # Check if we have all required arguments
            if self.simple_memory.is_complete():
                # Execute the action
                result = execute_action(
                    self.simple_memory.action_name, 
                    self.simple_memory.collected_args
                )
                self.simple_memory.reset()
                self.current_mode = None
                self.current_action = None
                return result
            else:
                # Ask for next missing argument
                next_missing = self.simple_memory.get_next_missing_arg()
                followup_q = self.llm_client.generate_followup_question(
                    next_missing, self.simple_memory.action_name
                )
                self.simple_memory.add_history("", followup_q)
                return followup_q
        else:
            # Extraction failed, re-ask the question
            followup_q = self.llm_client.generate_followup_question(
                missing_arg, self.simple_memory.action_name
            )
            self.simple_memory.add_history(user_reply, followup_q)
            return followup_q
    
    # ============================================================================
    # AGENTIC WORKFLOW HANDLING (Rich planning and reasoning)
    # ============================================================================
    
    def _handle_agentic_request(self, user_input: str) -> str:
        """
        Handle complex agentic requests with planning and reasoning.
        
        Args:
            user_input: User's natural language request
            
        Returns:
            Response string describing the result
        """
        # Set current mode
        self.current_mode = "agent"
        
        # Lazy-load agentic components
        self._ensure_agentic_components()
        
        try:
            # Step 1: Generate a plan
            plan, is_valid, errors = self.llm_client.generate_plan(user_input, ACTIONS)
            
            if not is_valid:
                error_msg = f"Sorry, I couldn't create a plan for that request. "
                if errors:
                    error_msg += f"Errors: {', '.join(errors[:3])}"  # Show first 3 errors
                return error_msg
            
            # Step 2: Execute the plan
            execution_result = self.plan_executor.execute_plan(plan)
            
            if not execution_result["success"]:
                return f"Sorry, I couldn't complete that request. Error: {execution_result.get('error', 'Unknown error')}"
            
            # Step 3: Format the response
            response = self._format_agentic_response(execution_result)
            
            # Reset mode after completion
            self.current_mode = None
            return response
            
        except Exception as e:
            self.current_mode = None
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
    
    def _ensure_agentic_components(self):
        """Lazy-load agentic components when needed."""
        if self.planning_agent is None:
            self.planning_agent = PlanningAgent(self.llm_client)
        if self.reasoning_engine is None:
            self.reasoning_engine = ReasoningEngine(self.llm_client)
        if self.plan_executor is None:
            self.plan_executor = PlanExecutor(
                reasoning_engine=self.reasoning_engine,
                action_executor=execute_action,
                actions_schema=ACTIONS
            )
    
    def _format_agentic_response(self, execution_result: Dict[str, Any]) -> str:
        """
        Format the agentic execution result into a user-friendly response.
        
        Args:
            execution_result: Result from plan execution
            
        Returns:
            Formatted response string
        """
        goal = execution_result.get("goal", "Unknown goal")
        results = execution_result.get("results", [])
        execution_time = execution_result.get("execution_time", 0)
        
        # Extract the final result (usually the last step)
        if results:
            final_step = results[-1]
            if final_step.get("step_type") == "action":
                # Return the action result
                return final_step.get("result", "Task completed successfully.")
            elif final_step.get("step_type") == "reasoning":
                # For reasoning steps, provide a summary
                return f"I've analyzed the information and found: {final_step.get('result', 'No specific result')}"
        
        # Fallback response
        return f"I've completed your request: {goal}. It took {execution_time:.1f} seconds."
    
    # ============================================================================
    # GENERAL QUERY HANDLING
    # ============================================================================
    
    def _handle_general_query(self, user_input: str) -> str:
        """
        Handle general conversational queries.
        
        Args:
            user_input: User's general question or comment
            
        Returns:
            Natural language response
        """
        return self.llm_client.generate_general_response(user_input)
    
    # ============================================================================
    # STATE MANAGEMENT AND UTILITIES
    # ============================================================================
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current orchestrator state.
        
        Returns:
            Dictionary with current state information
        """
        state = {
            "current_mode": self.current_mode,
            "current_action": self.current_action,
            "simple_memory_active": self.simple_memory.action_name is not None,
            "agent_memory_active": self.plan_executor is not None and self.plan_executor.memory.variables
        }
        
        if self.current_mode == "simple" and self.simple_memory.action_name:
            state.update({
                "action_name": self.simple_memory.action_name,
                "missing_args": self.simple_memory.missing_args,
                "collected_args": self.simple_memory.collected_args
            })
        
        if self.current_mode == "agent" and self.plan_executor:
            state.update({
                "agent_memory": self.plan_executor.get_execution_summary()
            })
        
        return state
    
    def reset(self):
        """Reset the orchestrator to initial state."""
        self.simple_memory.reset()
        if self.plan_executor:
            self.plan_executor.reset()
        
        self.current_mode = None
        self.current_action = None
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current execution state.
        
        Returns:
            Dictionary with execution summary
        """
        if self.current_mode == "agent" and self.plan_executor:
            return self.plan_executor.get_execution_summary()
        else:
            return {"mode": self.current_mode, "action": self.current_action} 