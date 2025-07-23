from typing import Dict, Any, Optional
from v4.services.lightweight_llm import LightweightLLM
from v4.action_schema import ACTIONS

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
            # Event
            "- User prompt: 'create an event called studying at 9 pm tomorrow'\n"
            "  Output: {\"title\": \"studying\", \"start_time\": \"9 pm tomorrow\"}\n"
            # Note
            "- User prompt: 'create a note titled project ideas with content about AI'\n"
            "  Output: {\"title\": \"project ideas\", \"content\": \"about AI\"}\n"
            # Todo
            "- User prompt: 'add buy milk to my todo list'\n"
            "  Output: {\"item\": \"buy milk\"}\n"
            # Negative/ambiguous
            "- User prompt: 'create a new note'\n"
            "  Output: {}\n"
            "- User prompt: 'add something'\n"
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
        response = self.llm.generate_response(prompt)
        print(f"[DEBUG] LLM raw response for extract_arguments: {response}")
        try:
            import json
            parsed = json.loads(response)
            print(f"[DEBUG] Parsed dict from extract_arguments: {parsed}")
            return parsed
        except Exception as e:
            print(f"[DEBUG] Exception parsing LLM response in extract_arguments: {e}")
            return {}

    def generate_followup_question(self, missing_arg: str, action_name: str) -> str:
        """
        Generate a concise, natural follow-up question for a missing argument, with one example per action type.
        """
        examples = (
            "Examples:\n"
            "- Missing argument: title (for create_note) → What should the note be called?\n"
            "- Missing argument: content (for create_note) → What should the note say?\n"
            "- Missing argument: item (for add_todo) → What would you like to add to your todo list?\n"
            "- Missing argument: start_time (for create_event) → When should the event start?\n"
        )
        prompt = (
            f"You need to ask the user for the missing argument [{missing_arg}] for action [{action_name}]. "
            f"Generate a concise, natural follow-up question. Do not use quotes.\n"
            f"{examples}"
        )
        return self.llm.generate_response(prompt).strip()

    def extract_argument_from_reply(self, reply: str, arg_name: str) -> Optional[Any]:
        """
        Extract a value for a missing argument from the user's reply. Includes diverse examples and explicit instructions.
        """
        examples = (
            "Examples:\n"
            "- User reply: 'studying' → 'studying'\n"
            "- User reply: 'call it project ideas' → 'project ideas'\n"
            "- User reply: 'buy milk' → 'buy milk'\n"
            "- User reply: 'the name is new' → null\n"
            "- User reply: 'something' → null\n"
        )
        prompt = (
            f"You are extracting the value for argument [{arg_name}]. "
            f"Extract ONLY the value, as a JSON string. "
            f"If the reply is generic (like 'new' or 'something'), return null.\n"
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