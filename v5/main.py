from v5.brain.unified_orchestrator import UnifiedOrchestrator
from v5.brain.unified_llm_client import UnifiedLLMClient
from v5.utils.intent_classifier import IntentClassifier
from v5.action_schema import ACTIONS
import time
import joblib
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from sentence_transformers import SentenceTransformer
import sys
from v5.commands.registry import get_command_handler
from concurrent.futures import ThreadPoolExecutor

# Load the new simple action classifier and label encoder
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'simple_action_classifier.joblib')
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'models', 'simple_action_label_encoder.joblib')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
simple_action_clf = joblib.load(MODEL_PATH)
simple_action_le = joblib.load(LABEL_ENCODER_PATH)
simple_action_embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

# --- Mode selector and config ---
MODE = None  # 'text' or 'voice'

def select_mode():
    global MODE
    if len(sys.argv) > 1 and sys.argv[1] in ["--mode=text", "--mode=voice"]:
        MODE = sys.argv[1].split("=")[1]
    else:
        print("Select mode: [1] Text  [2] Voice")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "2":
            MODE = "voice"
        else:
            MODE = "text"
    print(f"[INFO] Running in {MODE.upper()} mode.")

# --- Input/Output abstraction ---
def get_user_input_with_command_check_text(prompt, orchestrator):
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

# Placeholder for future STT integration
stt = None  # Global VoskSTT instance for voice mode
def get_user_input_with_command_check_voice(prompt, orchestrator):
    global stt
    print(prompt)
    print("[VOICE] Listening for your command...")
    user_input = stt.listen_and_transcribe()  # Do not pass prompt as audio
    if not user_input:
        print("[VOICE] No speech detected. Please try again.")
        return None
    print(f"[VOICE] You said: {user_input}")
    command_entry = get_command_handler(user_input)
    if command_entry:
        handler = command_entry["handler"]
        interrupting = command_entry["interrupting"]
        if handler.__name__ == 'handle_cancel':
            result = handler(orchestrator.session)
        else:
            result = handler()
        if result and result.message:
            print(result.message)
        return result
    return user_input

def output_response_text(response):
    print(f"🤖 SAM: {response}")

tts_engine = None
def output_response_voice(response):
    global tts_engine
    if tts_engine is None:
        from v5.TTS.tts_engine import LocalTTSEngine
        tts_engine = LocalTTSEngine(speaker="p273", speed=1.1)
    tts_engine.speak(response)

def get_user_input_with_command_check(prompt, orchestrator):
    if MODE == "voice":
        return get_user_input_with_command_check_voice(prompt, orchestrator)
    else:
        return get_user_input_with_command_check_text(prompt, orchestrator)

def output_response(response):
    if MODE == "voice":
        output_response_voice(response)
    else:
        output_response_text(response)


def main():
    global stt, tts_engine
    select_mode()
    if MODE == "voice":
        # Suppress Vosk verbose logging in voice mode
        import logging
        logging.getLogger('vosk').setLevel(logging.CRITICAL)
        # Also suppress any other verbose loggers
        logging.getLogger('VoskAPI').setLevel(logging.CRITICAL)
        logging.getLogger('kaldi').setLevel(logging.CRITICAL)
        
        from v5.STT.vosk_stt import VoskSTT
        stt = VoskSTT()
        print("Sam is running in voice mode. Debug and extra output will be suppressed.")
    else:
        print("🤖 Sam v5 - LLM-Driven Assistant with Intent Classifier")
        print("Type 'quit' or 'exit' to stop.")
    import time
    loaders = {}
    def load_calendar():
        t = time.time()
        from v5.services.google_calendar import GoogleCalendarService
        obj = GoogleCalendarService()
        if MODE == "text":
            print(f"[TIMING] GoogleCalendarService loaded in {time.time() - t:.2f} seconds")
        return obj
    def load_llm():
        t = time.time()
        from v5.brain.unified_llm_client import UnifiedLLMClient
        obj = UnifiedLLMClient()
        # Pre-warm LLM
        _ = obj.generate_general_response("Hello, Sam is warming up.")
        if MODE == "text":
            print(f"[TIMING] UnifiedLLMClient loaded and pre-warmed in {time.time() - t:.2f} seconds")
        return obj
    def load_tts():
        t = time.time()
        from v5.TTS.tts_engine import LocalTTSEngine
        obj = LocalTTSEngine(speaker="p273", speed=1.1)
        # Suppress TTS verbose output in voice mode
        if MODE == "voice":
            obj.speak("Warming up.", play=False)
        else:
            obj.speak("Warming up.", play=False)
            print(f"[TIMING] TTS engine loaded and pre-warmed in {time.time() - t:.2f} seconds")
        return obj
    def load_intent_classifier():
        t = time.time()
        from v5.utils.intent_classifier import IntentClassifier
        obj = IntentClassifier()
        if MODE == "text":
            print(f"[TIMING] IntentClassifier loaded in {time.time() - t:.2f} seconds")
        return obj
    with ThreadPoolExecutor() as executor:
        futures = {
            'calendar_service': executor.submit(load_calendar),
            'llm_interface': executor.submit(load_llm),
            'intent_classifier': executor.submit(load_intent_classifier)
        }
        if MODE == "voice":
            futures['tts_engine'] = executor.submit(load_tts)
        results = {}
        for name, future in futures.items():
            results[name] = future.result()
    calendar_service = results['calendar_service']
    llm_client = results['llm_interface']
    intent_classifier = results['intent_classifier']
    tts_engine = results['tts_engine'] if MODE == "voice" else None
    t_orch = time.time()
    orchestrator = UnifiedOrchestrator(llm_client)
    print(f"[TIMING] Unified Orchestrator loaded in {time.time() - t_orch:.2f} seconds")
    while True:
        try:
            user_input = get_user_input_with_command_check("\n👤 You: ", orchestrator)
            if user_input is None:
                continue
            if isinstance(user_input, str) and user_input.lower() in ["quit", "exit", "bye"]:
                output_response("Goodbye! Sam v5 is shutting down.")
                break
            if not user_input:
                continue
            start_time = time.time()  # Start timing
            
            # --- Intent Classification ---
            intent, probs = intent_classifier.classify(user_input)
            if MODE == "text":
                print(f"[DEBUG] Intent: {intent} | Probabilities: {probs}")
            
            # --- Action Classification for Simple Intent ---
            action_name = None
            if intent == "simple":
                # ML-based Action Classification
                emb = simple_action_embedder.encode([user_input])
                pred = simple_action_clf.predict(emb)[0]
                action_name = simple_action_le.inverse_transform([pred])[0]
                if MODE == "text":
                    print(f"[DEBUG] Predicted action: {action_name}")
            
            # --- Unified Processing ---
            response = orchestrator.process_user_input(user_input, intent, action_name)
            
            # Check if we need to do slot-filling
            current_state = orchestrator.get_current_state()
            if current_state.get("simple_memory_active", False):
                # We're in slot-filling mode, output the follow-up question
                output_response(response)
                
                # Handle slot-filling follow-ups
                while current_state.get("simple_memory_active", False):
                    # Get user reply
                    user_reply = get_user_input_with_command_check("👤 You: ", orchestrator)
                    from v5.commands.handlers import CommandResult
                    if isinstance(user_reply, CommandResult):
                        if user_reply.abort:
                            # Interrupting command: abort the task
                            break
                        else:
                            # Non-interrupting command: re-ask the question
                            continue
                    
                    # Process the follow-up using unified orchestrator
                    response = orchestrator.process_simple_followup(user_reply)
                    
                    # Check if we're still in slot-filling mode
                    current_state = orchestrator.get_current_state()
                    if not current_state.get("simple_memory_active", False):
                        break
                    else:
                        # Still in slot-filling, output the next question
                        output_response(response)
            
            elapsed = (time.time() - start_time) * 1000  # ms
            # Only output response if we're not in slot-filling mode
            if not current_state.get("simple_memory_active", False):
                output_response(response)
            if MODE == "text":
                print(f"[DEBUG] Processing time: {elapsed:.1f} ms")
        except KeyboardInterrupt:
            output_response("Goodbye! Sam v5 is shutting down.")
            break
        except Exception as e:
            output_response(f"Error: {e}")


if __name__ == "__main__":
    main() 