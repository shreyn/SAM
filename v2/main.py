from v2.brain.orchestrator import Orchestrator
import time


def main():
    print("🤖 SAM v2 - LLM-Driven Assistant")
    print("Type 'quit' or 'exit' to stop.")
    orchestrator = Orchestrator()
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("👋 Goodbye! SAM v2 is shutting down.")
                break
            if not user_input:
                continue
            start_time = time.time()  # Start timing
            response = orchestrator.process_user_input(user_input)
            elapsed = (time.time() - start_time) * 1000  # ms
            print(f"🤖 SAM: {response}")
            print(f"[DEBUG] Processing time: {elapsed:.1f} ms")
        except KeyboardInterrupt:
            print("\n👋 Goodbye! SAM v2 is shutting down.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 