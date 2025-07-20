# SAM - Smart Assistant Manager

A robust, modular AI assistant with intelligent intent classification and follow-up management.

## 🚀 Features

### **Two-Stage Intent Classification**
- **Stage 1**: Intent Type Detection (QUERY, ACTION, GREETING, UNKNOWN)
- **Stage 2**: Specific Action Classification within each type
- Handles semantic similarity correctly (e.g., "do i have events today" vs "create an event today")

### **Modular Follow-up System**
- Tracks missing arguments for each action
- Intelligently asks for missing information
- Supports multi-turn conversations
- Automatic task state management

### **Event Management**
- Create events with natural language
- Query events with intelligent filtering
- Support for relative dates (today, tomorrow, next Monday)
- Persistent storage with JSON backend

### **Notes Management**
- Create, read, update, and delete notes
- Full-text search across titles, content, and tags
- Tag-based organization and filtering
- Local file-based storage with JSON format
- Natural language note creation and management

### **Time & Date Intelligence**
- Current time, date, and day queries
- Context-aware responses
- Natural language time parsing

## 🏗️ Architecture

### Core Components

1. **IntentClassifier** (`core/intent_classifier.py`)
   - Two-stage classification system
   - Pattern-based with confidence scoring
   - Argument extraction from queries

2. **TaskState** (`core/task_state.py`)
   - Manages current task and missing arguments
   - Follow-up tracking and timeout handling
   - Automatic question generation

3. **ActionRegistry** (`core/action_registry.py`)
   - Defines required and optional arguments per action
   - Action validation and argument management
   - Extensible action system

4. **EventStore** (`core/event_store.py`)
   - Event creation, storage, and retrieval
   - Intelligent time parsing and filtering
   - JSON-based persistence

5. **SAMBrain** (`core/brain.py`)
   - Main orchestrator
   - Follow-up logic and action execution
   - Natural language processing

## 🎯 Supported Actions

### Queries
- `get_events` - Query calendar events
- `get_notes` - List all notes or filter by tag
- `search_notes` - Search notes by query
- `get_tags` - Get all available tags
- `get_time` - Get current time
- `get_date` - Get current date
- `get_day` - Get current day of week

### Actions
- `create_event` - Create calendar events
- `create_note` - Create notes with title, content, and tags
- `update_note` - Update existing notes
- `delete_note` - Delete notes
- `create_task` - Create tasks (planned)

### System
- `greeting` - Handle greetings
- `unknown` - Handle unknown intents

## 💬 Example Conversations

### Event Creation with Follow-ups
```
User: Create an event
SAM: What should I call this event?
User: Team meeting
SAM: When should this event start?
User: Tomorrow at 2pm
SAM: ✅ Event 'Team meeting' has been created for July 20 at 02:00 PM.
```

### Event Queries
```
User: Do I have events today?
SAM: You have no events scheduled for today.

User: Next event?
SAM: You have 1 event: 'Team meeting' on July 20 at 02:00 PM.
```

### Note Management
```
User: Create a note about Python programming
SAM: What should the note say?
User: Learn Python basics, data structures, and OOP
SAM: ✅ Note 'Python programming' has been created with ID: note_20250120_143022.

User: Show my notes
SAM: 1. 📝 Python programming
   🆔 note_20250120_143022
   📅 2025-01-20 14:30

User: Search notes for python
SAM: 1. 📝 Python programming
   🆔 note_20250120_143022
   📅 2025-01-20 14:30
```

### Time & Date
```
User: What time is it?
SAM: The current time is 06:36 PM.

User: What day is it?
SAM: Today is Saturday.
```

## 🛠️ Installation & Usage

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd SAM

# Create virtual environment
python -m venv sam_env
source sam_env/bin/activate  # On Windows: sam_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running SAM
```bash
python main.py
```

### Available Commands
- `help` - Show help information
- `debug` - Show debug information
- `reset` - Reset current task
- `quit` or `exit` - Exit SAM

## 🔧 Technical Details

### Intent Classification Algorithm
1. **Pattern Matching**: Fast regex-based classification
2. **Confidence Scoring**: Based on pattern strength and context
3. **Two-Stage Processing**: Intent type → Specific action
4. **Fallback Handling**: Unknown intents gracefully handled

### Follow-up System
1. **Task State Tracking**: Maintains current task and missing args
2. **Argument Extraction**: Intelligent parsing of follow-up responses
3. **Question Generation**: Context-aware follow-up questions
4. **Timeout Management**: Automatic task expiration

### Event System
1. **Natural Language Parsing**: Handles various time formats
2. **Relative Date Support**: Today, tomorrow, next [day]
3. **Intelligent Filtering**: Date, upcoming, limit-based queries
4. **Persistent Storage**: JSON-based event persistence

## 🧪 Testing

The system includes comprehensive testing for:
- Intent classification accuracy
- Follow-up logic functionality
- Event creation and querying
- Time and date handling
- Error handling and edge cases

## 🔮 Future Enhancements

- **Google Calendar Integration**: Real calendar sync
- **LLM Integration**: Enhanced natural language understanding
- **Voice Interface**: Speech-to-text and text-to-speech
- **Task Management**: Todo list and reminder system
- **Note Taking**: Rich text note creation
- **Multi-language Support**: Internationalization

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
