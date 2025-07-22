from v3.brain.orchestrator import Orchestrator
from v3.brain.llm_interface import LLMInterface
from v3.utils.intent_classifier import IntentClassifier
from v3.utils.simple_action_knn import SimpleActionKNN
from v3.action_schema import ACTIONS
import time


def main():
    print("🤖 SAM v3 - LLM-Driven Assistant with Intent Classifier")
    print("Type 'quit' or 'exit' to stop.")
    orchestrator = Orchestrator()
    llm_interface = LLMInterface()
    intent_classifier = IntentClassifier()
    knn = SimpleActionKNN(k=3)
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("👋 Goodbye! SAM v3 is shutting down.")
                break
            if not user_input:
                continue
            start_time = time.time()  # Start timing
            # --- Intent Classification ---
            intent, probs = intent_classifier.classify(user_input)
            print(f"[DEBUG] Intent: {intent} | Probabilities: {probs}")
            # --- Routing ---
            if intent == "simple":
                # --- Top-1 Action Selection with Heuristic for 'todo' ---
                top_k = knn.get_top_k(user_input)
                action_name = top_k[0][0]
                print(f"[DEBUG] Top-1 action: {action_name}")
                # Heuristic: If user mentions 'todo' or 'to do', and show_todo is in top-K, prefer it over read_note
                user_input_lower = user_input.lower()
                top_k_names = [name for name, _ in top_k]
                if ("todo" in user_input_lower or "to do" in user_input_lower) and "show_todo" in top_k_names:
                    if action_name == "read_note":
                        print("[DEBUG] Heuristic: Switching to 'show_todo' due to user input containing 'todo'.")
                        action_name = "show_todo"
                # Similarity delta logic: if top-1 and top-2 are close and one is show_todo, prefer show_todo if relevant
                if len(top_k) > 1:
                    delta = abs(top_k[0][1] - top_k[1][1])
                    if delta < 0.05 and "show_todo" in top_k_names:
                        if ("todo" in user_input_lower or "to do" in user_input_lower):
                            print("[DEBUG] Similarity delta small, preferring 'show_todo'.")
                            action_name = "show_todo"
                required_args = ACTIONS[action_name]["required_args"]
                optional_args = ACTIONS[action_name]["optional_args"]
                # --- Argument Extraction ---
                collected_args = {}
                if required_args:
                    extracted_args = llm_interface.extract_arguments(user_input, action_name)
                    collected_args = {k: v for k, v in extracted_args.items() if v is not None}
                    # --- Slot-filling loop ---
                    missing_args = [arg for arg in required_args if arg not in collected_args]
                    while missing_args:
                        missing_arg = missing_args[0]
                        followup_q = llm_interface.generate_followup_question(missing_arg, action_name)
                        print(f"🤖 SAM: {followup_q}")
                        user_reply = input("👤 You: ").strip()
                        value = llm_interface.extract_argument_from_reply(user_reply, missing_arg)
                        if value is not None and (not isinstance(value, str) or value.strip()):
                            collected_args[missing_arg] = value
                            missing_args = [arg for arg in required_args if arg not in collected_args]
                        else:
                            print(f"[DEBUG] Extraction failed, re-asking.")
                # --- Execute Action ---
                from v3.brain.execution import execute_action
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
            print("\n👋 Goodbye! SAM v3 is shutting down.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 