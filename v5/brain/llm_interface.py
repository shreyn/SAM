from typing import Dict, Any, Optional
from v5.services.lightweight_llm import LightweightLLM
from v5.action_schema import ACTIONS
import time
from v5.utils.slotfilling_logger import log_slotfilling_event

class LLMInterface:
    """
    Handles all LLM prompt/response logic for the assistant.
    """
    def __init__(self, llm: Optional[LightweightLLM] = None):
        self.llm = llm or LightweightLLM()

    def extract_arguments(self, user_prompt: str, action_name: str) -> Dict[str, Any]:
        """
        Extract arguments for a specific action. Uses concise, diverse examples and explicit instructions.
        """
        action_args = ACTIONS[action_name]["required_args"] + ACTIONS[action_name]["optional_args"]
        args_str = ', '.join(action_args)
        examples = (
            "Examples:\n"
            # Positive
            "- User prompt: 'create an event called studying at 9 pm tomorrow'\n"
            "  Output: {\"title\": \"studying\", \"start_time\": \"9 pm tomorrow\"}\n"
            # Negative/ambiguous
            "- User prompt: 'create a new note'\n"
            "  Output: {}\n"
        )
        prompt = (
            f"You are extracting arguments for the action [{action_name}].\n"
            f"Arguments: [{args_str}]\n"
            f"Extract ONLY the arguments that are clearly present in the user's message. "
            f"Do NOT use generic words like 'new' or 'something' as argument values. "
            f"Output a JSON object with only the arguments you are certain about.\n"
            f"{examples}"
            f"User prompt: {user_prompt}"
        )
        start_time = time.time()
        response = self.llm.generate_response(prompt)
        elapsed = (time.time() - start_time) * 1000
        print(f"[DEBUG] LLM raw response for extract_arguments: {response}")
        print(f"[TIMING] LLM arg extraction took {elapsed:.1f} ms")
        print(f"[SLOTFILLING-TIMING] extract_arguments for action '{action_name}' took {elapsed:.1f} ms")
        try:
            import json as _json
            args = _json.loads(response)
        except Exception as e:
            print(f"[DEBUG] Exception parsing LLM response: {e}")
            args = {}
        # --- LOGGING ---
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

    # --- Hardcoded follow-up question templates ---
    FOLLOWUP_TEMPLATES = {
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
        # Add more as needed
    }

    def generate_followup_question(self, missing_arg: str, action_name: str) -> str:
        """
        Generate a natural follow-up question for a missing argument using hardcoded templates.
        """
        question = self.FOLLOWUP_TEMPLATES.get((action_name, missing_arg))
        if question:
            return question
        # Fallback to a generic but natural template
        return f"What should the {missing_arg.replace('_', ' ')} be?"

    def extract_argument_from_reply(self, reply: str, arg_name: str, action_name: str) -> Optional[Any]:
        """
        Extract a value for a missing argument from the user's reply. Includes diverse examples and explicit instructions.
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
        response = self.llm.generate_response(prompt)
        elapsed = (time.time() - start_time) * 1000
        print(f"[DEBUG] LLM raw response for arg '{arg_name}': {response}")
        print(f"[TIMING] LLM arg extraction (follow-up) took {elapsed:.1f} ms")
        try:
            import json as _json
            value = _json.loads(response)
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