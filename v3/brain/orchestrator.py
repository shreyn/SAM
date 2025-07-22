from v3.action_schema import ACTIONS
from v3.brain.session_state import SessionState
from v3.brain.llm_interface import LLMInterface
from v3.brain.execution import execute_action

class Orchestrator:
    def __init__(self):
        self.session = SessionState()
        self.llm = LLMInterface()

    def process_user_input(self, user_input: str) -> str:
        # Assume action_name is set externally; orchestrator only handles slot-filling
        if not self.session.action_name:
            return "No action in progress. Please start an action."
        else:
            # We're in a slot-filling loop, so treat input as a reply to a follow-up
            missing_arg = self.session.get_next_missing_arg()
            if not missing_arg:
                return "Unexpected state: no missing arguments."
            value = self.llm.extract_argument_from_reply(user_input, missing_arg)
            if value is not None and (not isinstance(value, str) or value.strip()):
                self.session.update_argument(missing_arg, value)
                self.session.add_history(user_input)
            else:
                # Extraction failed, re-ask the follow-up question
                followup_q = self.llm.generate_followup_question(missing_arg, self.session.action_name)
                self.session.add_history(user_input, followup_q)
                return followup_q

        # Slot-filling loop: keep asking for missing args until complete
        while not self.session.is_complete():
            missing_arg = self.session.get_next_missing_arg()
            followup_q = self.llm.generate_followup_question(missing_arg, self.session.action_name)
            self.session.add_history("", followup_q)
            return followup_q  # Wait for user reply

        # All required args collected, execute
        result = execute_action(self.session.action_name, self.session.collected_args)
        self.session.reset()
        return result 