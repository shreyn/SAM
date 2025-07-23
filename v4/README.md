# SAM v3 — Hybrid AI Assistant Pipeline

SAM v3 is a local, schema-grounded AI assistant that combines fast machine learning with language models to deliver a robust, extensible, and efficient user experience. This version introduces a hybrid pipeline that intelligently routes user input for maximum speed and accuracy, especially for simple, common actions.

---

## Full Pipeline Overview

### 1. **User Input**
- The user types or speaks a request (e.g., "What time is it?", "Add buy milk to my todo list", "Explain entropy").

### 2. **Intent Classification (Fast ML)**
- The input is embedded using a pretrained MiniLM model (384D vector).
- A logistic regression classifier predicts the intent class:
  - `simple`: Direct assistant commands (e.g., time, notes, todos)
  - `query`: General knowledge or open-ended questions
  - `agent`: Reasoning-based, vague, or multi-step tasks (future work)
- **Speed:** This step is extremely fast (~5–10ms).

### 3. **Routing**
- **simple** → Simple Pipeline (see below)
- **query** → LLM Q&A mode (conversational, fact-based answer)
- **agent** → (Currently not implemented; will support tool-chaining and reasoning in the future)

### 4. **Simple Pipeline: Action Selection & Slot-Filling**
- **Action Selection:**
  - Uses KNN (cosine similarity) over precomputed action embeddings to find the most likely action.
  - Heuristics resolve ambiguity (e.g., prefer `show_todo` if "todo" is mentioned). (This was an attempt of fixing a problem explained below, didn't work...)
- **Argument Extraction:**
  - LLM is used to extract required arguments for the action. (a little slow)
  - If any required arguments are missing, the LLM generates a follow-up question and extracts the answer from the user's reply.
- **Execution:**
  - Once all required arguments are filled, the corresponding service (calendar, notes, todo) is called.

### 5. **Query Pipeline**
- For general knowledge or open-ended questions, the LLM generates a conversational, factual response (no tool use).

### 6. **Agent Pipeline (Planned)**
- For complex, multi-step, or reasoning-based tasks, the system will eventually support tool-chaining and more advanced workflows. (Currently, this path is a placeholder.)

---

## What's NEW in v3?

- **Hybrid Routing:** Combines fast ML intent classification, KNN action selection, and LLM slot-filling for optimal speed and accuracy.
- **Speed for Simple Actions:** Most common commands (time, date, listing notes) are handled in ~ 50-100 milliseconds, with the LLM only used for argument extraction (~1000ms).
- **Heuristic Disambiguation:** Special logic to resolve ambiguous cases (e.g., distinguishing between notes and todos). (didnt work!)
- **Extensible:** Each stage (intent, action, LLM) can be improved or swapped independently.
- **Debuggability:** Detailed debug output at every stage (intent, action, LLM response).

---

## Why is this better than v2?

- **Speed:** Simple actions are routed and executed much faster, as the LLM is only used for argument extraction, not for intent or action selection.
- **Accuracy:** ML classifier and KNN reduce LLM hallucination and improve handling of short/ambiguous queries.
- **Separation of Concerns:** Each pipeline stage is modular and focused, making the system easier to maintain and extend.

---

## ⚠️ Current Limitations

- **Nuance in Action Selection:** The simple vector cosine similarity used for action selection can struggle to detect subtle differences in user intent, especially for nuanced or overlapping actions.
- **Agent Pipeline:** The `agent` intent path is currently a placeholder and does not yet support advanced tool-chaining or reasoning. This will be added in a future release.

---

## 📂 Project Structure (Key Files)

- `main.py` — Entry point, full pipeline logic
- `utils/intent_classifier.py` — ML-based intent classification
- `utils/simple_action_knn.py` — KNN-based action selection
- `brain/llm_interface.py` — LLM slot-filling and argument extraction
- `services/` — Integrations for calendar, notes, todo
- `models/` — Model artifacts (classifier, embeddings)
- `scripts/` — Training and utility scripts
- `data/` — Training data and persistent storage

---

## 🛠️ Example Usage

- "What time is it?" → Fast intent classification, KNN selects `get_time`, instant response.
- "Add buy milk to my todo list" → KNN selects `add_todo`, LLM extracts item, todo updated.
- "Explain entropy" → Routed to LLM for a conversational answer.

---

## 📈 Future Directions
- Improve action selection with more advanced semantic models or fine-tuned embeddings.
- Implement the agentic pipeline for complex, multi-step tasks.
- Expand the schema and add more integrations.

