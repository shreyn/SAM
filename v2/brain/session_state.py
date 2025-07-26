from typing import Dict, List, Optional, Any

class SessionState:
    """
    Tracks the current session state for the slot-filling assistant.
    """
    def __init__(self):
        self.reset()

    def start_new_action(self, action_name: str, required_args: List[str], optional_args: List[str]):
        self.action_name = action_name
        self.required_args = required_args.copy()
        self.optional_args = optional_args.copy()
        self.collected_args = {}
        self.missing_args = required_args.copy()
        self.history = []

    def update_argument(self, arg_name: str, value: Any):
        self.collected_args[arg_name] = value
        if arg_name in self.missing_args:
            self.missing_args.remove(arg_name)

    def add_history(self, user_message: str, system_message: Optional[str] = None):
        self.history.append({
            "user": user_message,
            "system": system_message
        })

    def is_complete(self) -> bool:
        return len(self.missing_args) == 0

    def get_next_missing_arg(self) -> Optional[str]:
        return self.missing_args[0] if self.missing_args else None

    def reset(self):
        self.action_name: Optional[str] = None
        self.required_args: List[str] = []
        self.optional_args: List[str] = []
        self.collected_args: Dict[str, Any] = {}
        self.missing_args: List[str] = []
        self.history: List[Dict[str, Optional[str]]] = [] 