from typing import Dict, List, Any, Optional
from v2.services.lightweight_llm import LightweightLLM
from v2.action_schema import ACTIONS

class LLMInterface:
    """
    Handles all LLM prompt/response logic for the assistant.
    """
    def __init__(self, llm: Optional[LightweightLLM] = None):
        self.llm = llm or LightweightLLM()

    def select_action(self, user_prompt: str) -> str:
        """
        Given the user prompt and the list of available actions, ask the LLM to select the best action.
        """
        actions_list = list(ACTIONS.keys())
        schema_str = ', '.join(actions_list)
        prompt = (
            f"Given this user prompt and the list of available actions [{schema_str}], "
            f"which action best matches the user's goal? Output ONLY the action name.\n"
            f"User prompt: {user_prompt}"
        )
        action = self.llm.generate_response(prompt).strip().split()[0]
        if action in actions_list:
            return action
        return "unknown"

    SHORT_RESPONSE_ACTIONS = {"get_time", "get_date", "get_day", "greeting"}

    def extract_arguments(self, user_prompt: str, action_name: str) -> Dict[str, Any]:
        """
        Ask the LLM to extract only the arguments explicitly present in the user's message for the given action.
        Output a JSON object with only the arguments found (no nulls for missing). Add debug prints for LLM response and parsed dict.
        Use a shorter max_tokens for actions that require no arguments.
        """
        action_args = ACTIONS[action_name]["required_args"] + ACTIONS[action_name]["optional_args"]
        args_str = ', '.join(action_args)
        examples = (
            "Examples:\n"
            "- User prompt: 'create an event called studying at 9 pm tomorrow'\n"
            "  Output: {\"title\": \"studying\", \"start_time\": \"9 pm tomorrow\"}\n"
            "- User prompt: 'remind me to call mom at 5pm'\n"
            "  Output: {\"title\": \"call mom\", \"start_time\": \"5pm\"}\n"
            "- User prompt: 'create a new event called studying'\n"
            "  Output: {\"title\": \"studying\"}\n"
            "- User prompt: 'create a new event at 8pm'\n"
            "  Output: {\"start_time\": \"8pm\"}\n"
        )
        prompt = (
            f"Given the user's prompt and the following argument list for action [{action_name}]: [{args_str}], "
            f"extract ONLY the arguments that are explicitly present in the user's message. Do NOT guess or fill in plausible values. "
            f"Output a JSON object with only the arguments you are certain about.\n"
            f"{examples}"
            f"User prompt: {user_prompt}"
        )
        max_tokens = 20 if action_name in self.SHORT_RESPONSE_ACTIONS else None
        response = self.llm.generate_response(prompt, max_tokens=max_tokens)
        print(f"[DEBUG] LLM raw response for extract_arguments: {response}")
        try:
            import json
            parsed = json.loads(response)
            print(f"[DEBUG] Parsed dict from extract_arguments: {parsed}")
            return parsed
        except Exception as e:
            print(f"[DEBUG] Exception parsing LLM response in extract_arguments: {e}")
            return {}

    def generate_followup_question(self, missing_arg: str, action_name: str, context: Dict[str, Any]) -> str:
        """
        Ask the LLM to generate a natural, concise follow-up question for the missing argument. Do not use quotes.
        """
        prompt = (
            f"We still need the argument [{missing_arg}] for action [{action_name}]. "
            f"Given the current context: {context}, generate a natural, concise follow-up question to ask the user for this argument. "
            f"Do not use quotes, just output the question text."
        )
        return self.llm.generate_response(prompt).strip()

    def extract_argument_from_reply(self, reply: str, arg_name: str, context: Dict[str, Any]) -> Optional[Any]:
        """
        Ask the LLM to extract a value for the missing argument from the user's reply. Output a JSON value for the argument only, not a full object or quoted string.
        The reply may be just the value itself, or a phrase containing the value. Use examples to guide the LLM.
        """
        # General examples
        examples = (
            "Examples:\n"
            "- User reply: 'studying' → 'studying'\n"
            "- User reply: 'call it studying' → 'studying'\n"
            "- User reply: 'the name is studying' → 'studying'\n"
            "- User reply: 'I want to call it studying' → 'studying'\n"
        )
        # Add time/date examples if relevant
        if any(key in arg_name.lower() for key in ["time", "date"]):
            examples += (
                "- User reply: '8 pm tomorrow' → '8 pm tomorrow'\n"
                "- User reply: 'tomorrow at 8pm' → 'tomorrow at 8pm'\n"
                "- User reply: 'tonight at 7' → 'tonight at 7'\n"
                "- User reply: 'today at 5' → 'today at 5'\n"
            )
        prompt = (
            f"You are being given a user's reply to a direct question asking for the value of [{arg_name}] for [{context.get('action', 'the current action')}]. "
            f"The reply may be just the value itself (e.g., 'studying'), or a phrase containing the value (e.g., 'call it studying').\n"
            f"Extract ONLY the value for [{arg_name}] as a JSON string. If you are not sure, return null.\n"
            f"{examples}"
            f"User reply: {reply}"
        )
        response = self.llm.generate_response(prompt)
        print(f"[DEBUG] LLM raw response for arg '{arg_name}': {response}")
        try:
            import json
            value = json.loads(response)
            # If the LLM returns a dict, extract the value for arg_name
            if isinstance(value, dict):
                value = value.get(arg_name)
            # Strip leading/trailing quotes if value is a string
            if isinstance(value, str):
                value = value.strip('"\' ')
            print(f"[DEBUG] Parsed value for arg '{arg_name}': {value}")
            if value is None or (isinstance(value, str) and not value.strip()):
                return None
            return value
        except Exception as e:
            print(f"[DEBUG] Exception parsing LLM response for arg '{arg_name}': {e}")
            return None 