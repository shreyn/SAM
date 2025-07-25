from v4.brain.orchestrator import Orchestrator
from v4.brain.llm_interface import LLMInterface
from v4.utils.intent_classifier import IntentClassifier
from v4.action_schema import ACTIONS
import time
import joblib
import os
from sentence_transformers import SentenceTransformer
from v4.commands.registry import get_command_handler

# Load the new simple action classifier and label encoder
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'simple_action_classifier.joblib')
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'models', 'simple_action_label_encoder.joblib')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
simple_action_clf = joblib.load(MODEL_PATH)
simple_action_le = joblib.load(LABEL_ENCODER_PATH)
simple_action_embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

def get_user_input_with_command_check(prompt, orchestrator):
    while True:
        user_input = input(prompt).strip()
        command_entry = get_command_handler(user_input)
        if command_entry:
            handler = command_entry["handler"]
            interrupting = command_entry["interrupting"]
            # Call with session if needed
            if handler.__name__ == 'handle_cancel':
                result = handler(orchestrator.session)
            else:
                result = handler()
            if result and result.message:
                print(result.message)
            return result  # Always return CommandResult for commands
        return user_input

def main():
    print("🤖 SAM v4 - LLM-Driven Assistant with Intent Classifier")
    print("Type 'quit' or 'exit' to stop.")
    orchestrator = Orchestrator()
    llm_interface = LLMInterface()
    intent_classifier = IntentClassifier()
    while True:
        try:
            user_input = get_user_input_with_command_check("\n👤 You: ", orchestrator)
            if user_input is None:
                continue
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("👋 Goodbye! SAM v4 is shutting down.")
                break
            if not user_input:
                continue
            start_time = time.time()  # Start timing
            # --- Intent Classification ---
            intent, probs = intent_classifier.classify(user_input)
            print(f"[DEBUG] Intent: {intent} | Probabilities: {probs}")
            # --- Routing ---
            if intent == "simple":
                # --- ML-based Action Classification ---
                emb = simple_action_embedder.encode([user_input])
                pred = simple_action_clf.predict(emb)[0]
                action_name = simple_action_le.inverse_transform([pred])[0]
                print(f"[DEBUG] Predicted action: {action_name}")
                required_args = ACTIONS[action_name]["required_args"]
                optional_args = ACTIONS[action_name]["optional_args"]
                # --- Argument Extraction ---
                collected_args = {}
                if required_args or optional_args:
                    extracted_args = llm_interface.extract_arguments(user_input, action_name)
                    collected_args = {k: v for k, v in extracted_args.items() if v is not None}
                    # --- Slot-filling loop ---
                    missing_args = [arg for arg in required_args if arg not in collected_args]
                    aborted = False
                    while missing_args:
                        missing_arg = missing_args[0]
                        followup_q = llm_interface.generate_followup_question(missing_arg, action_name)
                        print(f"🤖 SAM: {followup_q}")
                        user_reply = get_user_input_with_command_check("👤 You: ", orchestrator)
                        from v4.commands.handlers import CommandResult
                        if isinstance(user_reply, CommandResult):
                            if user_reply.abort:
                                # Interrupting command: abort the task
                                aborted = True
                                break
                            else:
                                # Non-interrupting command: re-ask the question
                                continue
                        value = llm_interface.extract_argument_from_reply(user_reply, missing_arg, action_name)
                        if value is not None and (not isinstance(value, str) or value.strip()):
                            collected_args[missing_arg] = value
                            missing_args = [arg for arg in required_args if arg not in collected_args]
                        else:
                            print(f"[DEBUG] Extraction failed, re-asking.")
                    if aborted:
                        continue
                # --- Execute Action ---
                from v4.brain.execution import execute_action
                result = execute_action(action_name, collected_args)
                response = result
            elif intent == "query":
                response = llm_interface.llm.generate_general_response(user_input)
            elif intent == "agent":
                # For now, fallback to orchestrator (could be replaced with agentic pipeline)
                response = orchestrator.process_user_input(user_input)
            else:
                response = "Sorry, I couldn't classify your request."
            elapsed = (time.time() - start_time) * 1000  # ms
            print(f"🤖 SAM: {response}")
            print(f"[DEBUG] Processing time: {elapsed:.1f} ms")
        except KeyboardInterrupt:
            print("\n👋 Goodbye! SAM v4 is shutting down.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 