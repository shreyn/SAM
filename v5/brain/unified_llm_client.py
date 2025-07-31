#!/usr/bin/env python3
"""
Unified LLM Client - Single interface for all LLM interactions
Consolidates argument extraction, planning, reasoning, and general responses
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List, Tuple
from v5.utils.config import API_URL, MODEL_NAME, MAX_RESPONSE_LENGTH
from v5.action_schema import ACTIONS
from v5.utils.slotfilling_logger import log_slotfilling_event

class UnifiedLLMClient:
    """
    Unified LLM client that handles all types of LLM interactions with organized instruction types.
    Provides consistent error handling, timing, and logging across all LLM operations.
    """
    
    def __init__(self, api_url: str = None, model_name: str = None):
        """
        Initialize the unified LLM client.
        
        Args:
            api_url: LLM API endpoint (defaults to config)
            model_name: LLM model name (defaults to config)
        """
        self.api_url = api_url or API_URL
        self.model_name = model_name or MODEL_NAME
        
        # Hardcoded follow-up question templates for speed
        self.followup_templates = {
            ("create_note", "title"): "What should the note be called?",
            ("create_note", "content"): "What should the note say?",
            ("create_event", "title"): "What is the title of the event?",
            ("create_event", "start_time"): "When should the event start?",
            ("create_event", "duration"): "How long will the event last?",
            ("create_event", "description"): "What is the description of the event?",
            ("create_event", "location"): "Where will the event take place?",
            ("create_event", "date"): "On what date should the event be scheduled?",
            ("add_todo", "item"): "What would you like to add to your to-do list?",
            ("read_note", "title"): "What is the title of the note you want to read?",
            ("edit_note", "title"): "What is the title of the note you want to edit?",
            ("edit_note", "content"): "What should the updated note say?",
            ("delete_note", "title"): "What is the title of the note you want to delete?",
            ("remove_todo_item", "item_number"): "Which item number would you like to remove from your to-do list?",
        }
    
    # ============================================================================
    # ARGUMENT EXTRACTION METHODS (for slot-filling)
    # ============================================================================
    
    def extract_arguments(self, user_prompt: str, action_name: str) -> Dict[str, Any]:
        """
        Extract arguments for a specific action from user input.
        
        Args:
            user_prompt: User's natural language input
            action_name: Name of the action to extract arguments for
            
        Returns:
            Dictionary of extracted arguments
        """
        action_args = ACTIONS[action_name]["required_args"] + ACTIONS[action_name]["optional_args"]
        args_str = ', '.join(action_args)
        
        examples = (
            "Examples:\n"
            "- User prompt: 'create an event called studying at 9 pm tomorrow'\n"
            "  Output: {\"title\": \"studying\", \"start_time\": \"9 pm tomorrow\"}\n"
            "- User prompt: 'create a new note'\n"
            "  Output: {}\n"
        )
        
        prompt = (
            f"You are extracting arguments for the action [{action_name}].\n"
            f"Arguments: [{args_str}]\n"
            f"Extract ONLY the arguments that are clearly present in the user's message. "
            f"Do NOT use generic words like 'new', 'something', 'a note', 'an event', 'the note', 'the event' as argument values. "
            f"Only extract specific, meaningful values. If the user says something generic like 'read a note', do NOT extract 'a note' as the title.\n"
            f"Output a JSON object with only the arguments you are certain about.\n"
            f"{examples}"
            f"User prompt: {user_prompt}"
        )
        
        start_time = time.time()
        response = self._make_request(
            messages=[
                {"role": "system", "content": "You are an argument extraction assistant. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.05
        )
        elapsed = (time.time() - start_time) * 1000
        
        print(f"[DEBUG] LLM raw response for extract_arguments: {response}")
        print(f"[TIMING] LLM arg extraction took {elapsed:.1f} ms")
        print(f"[SLOTFILLING-TIMING] extract_arguments for action '{action_name}' took {elapsed:.1f} ms")
        
        # Parse response
        try:
            args = json.loads(response) if isinstance(response, str) else {}
        except Exception as e:
            print(f"[DEBUG] Exception parsing LLM response: {e}")
            args = {}
        
        # Log the event
        log_slotfilling_event({
            'event_type': 'extract_arguments',
            'user_prompt': user_prompt,
            'action_name': action_name,
            'required_args': ACTIONS[action_name]["required_args"],
            'optional_args': ACTIONS[action_name]["optional_args"],
            'llm_args_output': args,
            'llm_raw_response': response
        })
        
        return args
    
    def generate_followup_question(self, missing_arg: str, action_name: str) -> str:
        """
        Generate a follow-up question for a missing argument using hardcoded templates.
        
        Args:
            missing_arg: Name of the missing argument
            action_name: Name of the action
            
        Returns:
            Natural language follow-up question
        """
        question = self.followup_templates.get((action_name, missing_arg))
        if question:
            return question
        # Fallback to a generic but natural template
        return f"What should the {missing_arg.replace('_', ' ')} be?"
    
    def extract_argument_from_reply(self, reply: str, arg_name: str, action_name: str) -> Optional[Any]:
        """
        Extract a value for a missing argument from the user's reply.
        
        Args:
            reply: User's reply to the follow-up question
            arg_name: Name of the argument being extracted
            action_name: Name of the action
            
        Returns:
            Extracted value or None if extraction failed
        """
        examples = (
            "Examples:\n"
            "- User reply: 'studying' → 'studying'\n"
            "- User reply: 'the name is new' → null\n"
        )
        
        prompt = (
            f"You are extracting the value for argument [{arg_name}]. "
            f"Extract ONLY the value, as a JSON string. "
            f"If the reply is generic (like 'new' or 'something'), return null.\n"
            f"{examples}"
            f"User reply: {reply}"
        )
        
        start_time = time.time()
        response = self._make_request(
            messages=[
                {"role": "system", "content": "You are an argument extraction assistant. Output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.05
        )
        elapsed = (time.time() - start_time) * 1000
        
        print(f"[DEBUG] LLM raw response for arg '{arg_name}': {response}")
        print(f"[TIMING] LLM arg extraction (follow-up) took {elapsed:.1f} ms")
        
        try:
            value = json.loads(response) if isinstance(response, str) else None
            
            # If the LLM returns a dict, extract the value for arg_name
            if isinstance(value, dict):
                value = value.get(arg_name)
            
            # Strip leading/trailing quotes if value is a string
            if isinstance(value, str):
                value = value.strip('"\' ')
            
            print(f"[DEBUG] Parsed value for arg '{arg_name}': {value}")
            
            if value is None or (isinstance(value, str) and not value.strip()):
                log_slotfilling_event({
                    'event_type': 'extract_argument_from_reply',
                    'user_reply': reply,
                    'arg_name': arg_name,
                    'action_name': action_name,
                    'llm_arg_value': None,
                    'llm_raw_response': response
                })
                return None
            
            log_slotfilling_event({
                'event_type': 'extract_argument_from_reply',
                'user_reply': reply,
                'arg_name': arg_name,
                'action_name': action_name,
                'llm_arg_value': value,
                'llm_raw_response': response
            })
            
            return value
            
        except Exception as e:
            print(f"[DEBUG] Exception parsing LLM response for arg '{arg_name}': {e}")
            log_slotfilling_event({
                'event_type': 'extract_argument_from_reply',
                'user_reply': reply,
                'arg_name': arg_name,
                'action_name': action_name,
                'llm_arg_value': None,
                'llm_raw_response': response,
                'error': str(e)
            })
            return None
    
    # ============================================================================
    # PLANNING METHODS (for agentic workflows)
    # ============================================================================
    
    def generate_plan(self, user_goal: str, actions_schema: Dict[str, Any], stream: bool = False) -> Tuple[Dict[str, Any], bool, List[str]]:
        """
        Generate a structured plan from a user goal.
        
        Args:
            user_goal: Natural language description of what the user wants
            actions_schema: Dictionary of available actions and their specifications
            stream: Whether to stream the LLM response
            
        Returns:
            Tuple of (plan_dict, is_valid, error_messages)
        """
        from v5.brain.planning_prompts import build_planning_prompt
        from v5.brain.plan_validator import PlanValidator
        
        print(f"[AGENT-DEBUG] Generating plan for goal: {user_goal}")
        
        # Build the planning prompt
        prompt = build_planning_prompt(user_goal, actions_schema)
        print(f"[AGENT-DEBUG] Planning prompt length: {len(prompt)} characters")
        
        # Generate plan using LLM
        print(f"[AGENT-DEBUG] Making LLM request for plan generation...")
        start_time = time.time()
        raw_response = self._make_request(
            messages=[
                {"role": "system", "content": "You are a planning agent. Output only valid JSON plans. Be precise and accurate."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.05,
            top_p=0.8,
            stream=stream
        )
        llm_time = (time.time() - start_time) * 1000
        print(f"[AGENT-DEBUG] LLM response received in {llm_time:.1f} ms")
        print(f"[AGENT-DEBUG] Raw LLM response length: {len(raw_response)} characters")
        print(f"[AGENT-DEBUG] Raw LLM response (FULL): {raw_response}")
        
        # Parse the response into a plan
        print(f"[AGENT-DEBUG] Parsing LLM response into plan...")
        try:
            plan = self._parse_plan_response(raw_response)
            print(f"[AGENT-DEBUG] Plan parsing successful")
            print(f"[AGENT-DEBUG] Plan structure: {list(plan.keys()) if isinstance(plan, dict) else 'Not a dict'}")
            if isinstance(plan, dict) and 'steps' in plan:
                print(f"[AGENT-DEBUG] Number of steps: {len(plan['steps'])}")
                for i, step in enumerate(plan['steps']):
                    step_type = 'action' if 'action' in step else 'reasoning' if 'reasoning' in step else 'conditional' if 'condition' in step else 'unknown'
                    step_content = step.get('action', step.get('reasoning', step.get('condition', 'unknown')))
                    print(f"[AGENT-DEBUG] Step {i+1}: {step_type} - {step_content}")
                    # Also show the full step structure for debugging
                    print(f"[AGENT-DEBUG] Step {i+1} full structure: {step}")
        except Exception as e:
            print(f"[AGENT-DEBUG] Plan parsing failed: {e}")
            raise
        
        # Validate the plan
        print(f"[AGENT-DEBUG] Validating plan...")
        validator = PlanValidator()
        is_valid, errors = validator.validate_plan(plan, actions_schema)
        print(f"[AGENT-DEBUG] Plan validation result: {is_valid}")
        if errors:
            print(f"[AGENT-DEBUG] Validation errors: {errors}")
        
        return plan, is_valid, errors
    
    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured plan.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed plan dictionary
        """
        try:
            print(f"[AGENT-DEBUG] Starting JSON extraction from response...")
            
            # Extract JSON from the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            print(f"[AGENT-DEBUG] JSON bounds: start_idx={start_idx}, end_idx={end_idx}")

            if start_idx == -1 or end_idx == 0:
                print(f"[AGENT-DEBUG] No JSON braces found in response")
                raise ValueError("No JSON found in response")

            json_str = response[start_idx:end_idx]
            print(f"[AGENT-DEBUG] Extracted JSON string length: {len(json_str)}")
            print(f"[AGENT-DEBUG] Extracted JSON (first 300 chars): {json_str[:300]}")
            if len(json_str) > 300:
                print(f"[AGENT-DEBUG] Extracted JSON (last 200 chars): {json_str[-200:]}")
            
            # Clean the JSON string
            print(f"[AGENT-DEBUG] Cleaning JSON string...")
            json_str = self._clean_json_string(json_str)
            print(f"[AGENT-DEBUG] Cleaned JSON string length: {len(json_str)}")
            print(f"[AGENT-DEBUG] Cleaned JSON (first 300 chars): {json_str[:300]}")
            if len(json_str) > 300:
                print(f"[AGENT-DEBUG] Cleaned JSON (last 200 chars): {json_str[-200:]}")
            
            print(f"[AGENT-DEBUG] Attempting JSON parsing...")
            plan = json.loads(json_str)
            print(f"[AGENT-DEBUG] JSON parsing successful")

            # Validate basic structure
            if not isinstance(plan, dict):
                print(f"[AGENT-DEBUG] Plan is not a dictionary: {type(plan)}")
                raise ValueError("Plan must be a dictionary")

            if "steps" not in plan:
                print(f"[AGENT-DEBUG] Plan missing 'steps' key. Available keys: {list(plan.keys())}")
                raise ValueError("Plan must contain 'steps' key")

            if not isinstance(plan["steps"], list):
                print(f"[AGENT-DEBUG] Steps is not a list: {type(plan['steps'])}")
                raise ValueError("Steps must be a list")

            print(f"[AGENT-DEBUG] Plan structure validation successful")
            return plan

        except json.JSONDecodeError as e:
            print(f"[AGENT-DEBUG] JSON decode error: {e}")
            print(f"[AGENT-DEBUG] Error occurred at position: {e.pos}")
            print(f"[AGENT-DEBUG] Line: {e.lineno}, Column: {e.colno}")
            # Show the problematic area
            if hasattr(e, 'pos') and e.pos < len(json_str):
                start_show = max(0, e.pos - 50)
                end_show = min(len(json_str), e.pos + 50)
                print(f"[AGENT-DEBUG] Problematic area: {json_str[start_show:end_show]}")
                print(f"[AGENT-DEBUG] Error position: {' ' * (e.pos - start_show)}^")
            raise ValueError(f"Invalid JSON in response: {e}")
        except Exception as e:
            print(f"[AGENT-DEBUG] Unexpected error during plan parsing: {e}")
            raise ValueError(f"Failed to parse plan: {e}")
    
    def _clean_json_string(self, json_str: str) -> str:
        """
        Clean JSON string by removing comments and fixing common issues.
        
        Args:
            json_str: Raw JSON string
            
        Returns:
            Cleaned JSON string
        """
        import re
        
        print(f"[AGENT-DEBUG] Cleaning JSON string...")
        original_length = len(json_str)
        
        # Remove single-line comments (// ...)
        json_str = re.sub(r'//.*?(?=\n|$)', '', json_str)
        
        # Remove multi-line comments (/* ... */)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Remove trailing commas before closing brackets/braces
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Additional cleaning: fix common LLM JSON issues
        # Fix missing quotes around property names
        json_str = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', json_str)
        
        # DON'T convert single quotes to double quotes - this breaks valid JSON
        # The LLM correctly uses single quotes inside string content
        # json_str = re.sub(r"'([^']*)'", r'"\1"', json_str)  # REMOVED - this was the bug!
        
        # CRITICAL FIX: Handle unescaped quotes inside string values
        # This is the main issue - LLM generates quotes inside strings without escaping them
        
        # First, try to parse the JSON as-is to see if it's already valid
        try:
            json.loads(json_str)
            print(f"[AGENT-DEBUG] JSON is already valid, no cleaning needed")
            return json_str.strip()
        except json.JSONDecodeError as e:
            print(f"[AGENT-DEBUG] JSON needs cleaning. Error: {e}")
            print(f"[AGENT-DEBUG] For now, returning original JSON to see exact LLM output")
            # For debugging, return the original JSON to see exactly what the LLM generated
            return json_str.strip()
        
        # Remove any non-printable characters
        json_str = ''.join(char for char in json_str if char.isprintable() or char in '\n\r\t')
        
        cleaned_length = len(json_str)
        print(f"[AGENT-DEBUG] JSON cleaning: {original_length} -> {cleaned_length} characters")
        
        return json_str.strip()
    
    # ============================================================================
    # REASONING METHODS (for agentic workflows)
    # ============================================================================
    
    def execute_reasoning(self, instruction: str, memory_context: str) -> Any:
        """
        Execute a reasoning step with access to stored memory.
        
        Args:
            instruction: The reasoning prompt (e.g., "Find first available 1-hour slot...")
            memory_context: Current memory state with all stored variables
            
        Returns:
            The result of the reasoning (e.g., "7:00 PM")
        """
        prompt = f"""You are a reasoning engine that performs logical operations on data.

AVAILABLE DATA:
{memory_context}

INSTRUCTION:
{instruction}

INSTRUCTIONS:
1. Analyze the available data above
2. Follow the instruction precisely
3. Return ONLY the result, formatted appropriately
4. If the instruction asks for a specific format (like a timestamp), use that format
5. If the data shows "no events" or empty lists, interpret this as "all time is free"
6. For time-based reasoning with no events, suggest reasonable default times (e.g., "7:00 PM")
7. When parsing natural language responses, extract the relevant information:
   - From numbered lists like "1. homework\n2. club things\n3. to do" → extract the title that matches
   - From "You have 2 events today. Work meeting at 6 PM, and Gym at 8 PM." → extract event details
8. If you cannot complete the instruction with available data, return "INSUFFICIENT_DATA"
9. Be concise and precise in your response

EXAMPLES:
- Instruction: "Find the note titled 'homework' from the notes list"
- Data: "1. homework\n2. club things\n3. to do"
- Result: "homework"

Result:"""
        
        response = self._make_request(
            messages=[
                {"role": "system", "content": "You are a reasoning engine. Provide concise, accurate responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.05,
            top_p=0.8
        )
        
        return self._parse_reasoning_result(response)
    
    def _parse_reasoning_result(self, response: str) -> Any:
        """
        Parse the LLM response to extract the reasoning result.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed result (string, number, or structured data)
        """
        # Clean the response
        response = response.strip()
        
        # Handle special cases
        if response.upper() == "INSUFFICIENT_DATA":
            return "INSUFFICIENT_DATA"
        
        if response.upper().startswith("ERROR:"):
            return response
        
        # Try to parse as JSON if it looks like structured data
        if response.startswith('{') or response.startswith('['):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
        
        # Try to parse as number
        try:
            if '.' in response:
                return float(response)
            else:
                return int(response)
        except ValueError:
            pass
        
        # Strip quotes from string responses (common LLM behavior)
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]  # Remove outer quotes
        elif response.startswith("'") and response.endswith("'"):
            response = response[1:-1]  # Remove outer single quotes
        
        # Return as string (most common case)
        return response
    
    # ============================================================================
    # GENERAL RESPONSE METHODS (for queries)
    # ============================================================================
    
    def generate_general_response(self, query: str) -> str:
        """
        Generate a general response for conversational queries.
        
        Args:
            query: User's general question or comment
            
        Returns:
            Natural language response
        """
        system_prompt = (
            "You are SAM, a personal assistant. Respond naturally to each query as if it's a fresh conversation.\n"
            "For factual, info questions (what is, how many, when, where): Give direct, concise answers.\n"
            "For conversational comments (wow, that's cool, etc.): Respond naturally and conversationally.\n"
            "For social questions (jokes, favorites, etc.): Be warm and engaging.\n"
            "For complex questions (academic, technical, etc.): Be slightly more detailed, but still concise.\n"
            "Examples:\n"
            "- 'What's the moon's size?' → 'The moon's diameter is 2,159 miles.'\n"
            "- 'Wow, that's far!' → 'Yeah, it really is! Space is pretty incredible.'\n"
            "- 'Tell me a joke' → 'Why don't scientists trust atoms? Because they make up everything!'\n"
            "- 'That's interesting' → 'I think so too! What caught your attention?'\n"
            "Keep responses natural and conversational (1-2 sentences)."
        )
        
        return self._make_request(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=MAX_RESPONSE_LENGTH,
            temperature=0.1
        )
    
    # ============================================================================
    # CORE LLM REQUEST METHOD
    # ============================================================================
    
    def _make_request(self, messages: List[Dict[str, str]], max_tokens: int = None, 
                     temperature: float = 0.1, top_p: float = 1.0, stream: bool = False) -> str:
        """
        Make a request to the LLM API with consistent error handling.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stream: Whether to stream the response
            
        Returns:
            Generated response string or error message
        """
        if max_tokens is None:
            max_tokens = MAX_RESPONSE_LENGTH
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream
        }
        
        try:
            if stream:
                return self._stream_response(payload)
            else:
                return self._regular_response(payload)
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out - please try again"
        except requests.exceptions.ConnectionError as e:
            return f"Error: Cannot connect to language model - {str(e)}"
        except Exception as e:
            return f"Error: Unexpected error - {str(e)}"
    
    def _regular_response(self, payload: dict) -> str:
        """Handle regular (non-streaming) LLM response."""
        response = requests.post(
            f"{self.api_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code} - {response.text}"
        
        result = response.json()
        
        if "choices" not in result or not result["choices"]:
            return "Error: Invalid response format from language model"
        
        content = result["choices"][0]["message"]["content"].strip()
        return content
    
    def _stream_response(self, payload: dict) -> str:
        """Handle streaming LLM response."""
        response = requests.post(
            f"{self.api_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60,
            stream=True
        )
        
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code} - {response.text}"
        
        full_content = ""
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                # Skip the "data: [DONE]" line
                if line_str == "data: [DONE]":
                    break
                
                # Parse SSE format
                if line_str.startswith("data: "):
                    data_str = line_str[6:]  # Remove "data: " prefix
                    
                    try:
                        data = json.loads(data_str)
                        
                        if "choices" in data and data["choices"]:
                            choice = data["choices"][0]
                            
                            if "delta" in choice and "content" in choice["delta"]:
                                content_chunk = choice["delta"]["content"]
                                full_content += content_chunk
                                
                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue
        
        return full_content.strip()
    
    def test_connection(self) -> bool:
        """
        Test if the LLM server is accessible.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = requests.get(f"{self.api_url}/v1/chat/completions", timeout=5)
            return response.status_code in [200, 405]  # 405 is Method Not Allowed, which means endpoint exists
        except Exception:
            return False 