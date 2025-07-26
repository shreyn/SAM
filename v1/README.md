# SAM - Smart Assistant Manager

A modular, extensible AI assistant for natural language productivity, featuring intelligent intent classification, Google Calendar integration, and local notes management.

---

## 🚀 Features

- **Two-Stage Intent Classification**: Fast, pattern-based detection of user intent and action, with fallback to LLM for ambiguous queries.
- **Follow-up System**: Multi-turn conversations with automatic tracking of missing arguments and context-aware follow-up questions.
- **Google Calendar Integration**: Create and query events using natural language, with support for relative dates and time zone configuration.
- **Notes Management**: Create, read, update, delete, and search notes, stored locally as JSON files.
- **Time & Date Intelligence**: Handles queries about current time, date, and day, with advanced natural language parsing.
- **LLM Fallback**: Uses a local LLM (e.g., Mistral via LM Studio) for complex or unknown queries.
- **Configurable & Extensible**: Modular architecture for easy addition of new actions and integrations.

---

## 🏗️ Architecture

- **main.py**: CLI entry point for the assistant.
- **core/brain.py**: Main orchestrator (SAMBrain) for intent classification, task state, follow-ups, and action execution.
- **core/intent_classifier.py**: Two-stage intent classifier with regex-based pattern matching and argument extraction.
- **core/task_state.py**: Manages current task, arguments, follow-up state, and expiration.
- **core/action_registry.py**: Registers all available actions and their required/optional arguments.
- **core/google_calendar.py**: Handles Google Calendar authentication, event creation, and querying, with time zone support.
- **core/notes_service.py**: Manages notes as local JSON files, providing CRUD operations and search.
- **core/lightweight_llm.py**: Minimal client for LLM-based intent classification and response generation.
- **utils/time_parser.py**: Centralized time parsing and formatting using parsedatetime.
- **utils/config.py**: Loads configuration from environment variables and .env files, including API URLs and TIMEZONE.

---

## ⚙️ Setup

### Prerequisites
- Python 3.8+
- [LM Studio](https://lmstudio.ai) (for LLM fallback, optional but recommended)
- Google Calendar API credentials (for calendar features)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd SAM

# Create and activate virtual environment
python -m venv sam_env
source sam_env/bin/activate  # On Windows: sam_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Google Calendar Setup
1. Create a Google Cloud project and enable the Google Calendar API.
2. Create OAuth 2.0 credentials (Desktop application) and download `credentials.json`.
3. Place `credentials.json` in the `data/` directory.
4. On first run, authenticate in the browser when prompted.

### LLM Setup (Optional)
1. Download and install LM Studio.
2. Load a compatible model (e.g., `mistralai/mistral-nemo-instruct-2407-q3_k_l`).
3. Start the API server on port 1234.

---

## 🖥️ Usage

### Start the Assistant
```bash
./start_sam.sh
# or manually
source sam_env/bin/activate
python main.py
```

### Example Commands
- `What time is it?`
- `Create an event called team meeting tomorrow at 2pm`
- `Show my notes`
- `Create a note about project ideas`
- `Search notes for python`
- `reset` (reset current task)
- `help` (show help)
- `quit` or `exit` (exit SAM)

---

## 🔧 Configuration

Edit `.env` or set environment variables to customize:
- `API_URL` (default: `http://127.0.0.1:1234`)
- `MODEL_NAME` (default: `mistralai/mistral-nemo-instruct-2407`)
- `TIMEZONE` (default: `America/Los_Angeles`)

---

## 🧩 Extensibility

- **Add New Actions**: Register new actions in `core/action_registry.py` and implement their logic in `core/brain.py`.
- **Integrate More Services**: Add new service modules and connect them via the orchestrator.
- **Customize LLM**: Point to any local or remote LLM API by changing `API_URL` and `MODEL_NAME`.

---

## 📁 Data Storage

- **Notes**: Stored in `data/notes/` as individual JSON files, indexed by `index.json`.
- **Google Calendar**: Credentials in `data/credentials.json`, OAuth token in `data/token.pickle`.

---

## 🛠️ Testing

- Comprehensive test suites for notes and overall assistant functionality are included (see test files).

---

## 📝 License

This project is licensed under the MIT License. 