# SAM v5 — Voice-First AI Assistant with Agentic Reasoning

SAM v5 is a sophisticated AI assistant designed for natural, real-time voice interaction. It combines fast machine learning with advanced planning and reasoning capabilities to handle both simple tasks and complex multi-step workflows.

## Overview

SAM v5 is built around four core pillars:

1. **Voice Integration** - Seamless speech-to-text and text-to-speech for natural conversation
2. **Agentic Pipeline** - Advanced planning and reasoning for complex workflows  
3. **Unified Architecture** - Clean, maintainable codebase with consistent patterns
4. **Human Reinforcement Learning** - Continuous improvement through user feedback

## 1. Voice Integration

### Text-to-Speech (TTS)
**Implementation**: Local TTS using the `TTS` library with speaker "p273" at 1.1x speed
**Why Local**: Sub-100ms latency for immediate response, no network dependency
**Quality**: Natural-sounding voice optimized for conversational interaction
**Integration**: Automatic TTS in voice mode, text output in debug mode

### Speech-to-Text (STT) 
**Implementation**: Vosk offline speech recognition
**Why Offline**: Real-time processing, no privacy concerns, works without internet
**Performance**: ~200-500ms latency for speech recognition
**Mode Support**: Voice mode with STT, text mode for development

### Voice-First Design Philosophy
All optimizations serve the voice experience:
- **Fast slot-filling** (hardcoded templates) for immediate responses
- **Efficient intent classification** (~10ms) for quick routing
- **Streamlined agent pipeline** for complex voice requests
- **Natural language responses** optimized for speech output

## 2. Agentic Planning and Reasoning Pipeline

### Overview
The agentic pipeline handles complex, multi-step workflows that require reasoning, analysis, and planning. Unlike simple actions that execute immediately, agentic requests are broken down into structured plans with reasoning steps.

### Core Components

#### Planning Agent
- **Purpose**: Converts natural language goals into structured JSON execution plans
- **Input**: User request like "create a dinner event tonight when I'm free"
- **Output**: Structured plan with action and reasoning steps
- **Example Plan**:
  ```json
  {
    "goal": "Create dinner event tonight when free",
    "steps": [
      {"id": "s1", "action": "get_events", "args": {}, "save_as": "events_list"},
      {"id": "s2", "reasoning": "Find free time slot tonight from events_list", "save_as": "free_slot"},
      {"id": "s3", "action": "create_event", "args": {"title": "Dinner", "time": "${free_slot}"}}
    ]
  }
  ```

#### Reasoning Engine
- **Purpose**: Executes reasoning steps using LLM with context from previous steps
- **Input**: Reasoning instruction + current memory state
- **Output**: Parsed result (stripped of quotes, formatted consistently)
- **Example**: "Find free time slot tonight from events_list" → "8:00 PM - 10:00 PM"

#### Plan Memory
- **Purpose**: Stores and retrieves variables across plan execution steps
- **Implementation**: Simple variable store with `${variable_name}` template substitution
- **Usage**: Each step can save results with `save_as` field, later steps reference stored data

#### Plan Executor
- **Purpose**: Orchestrates step-by-step execution of generated plans
- **Features**: Error handling, timing, validation, memory management
- **Flow**: Execute step → store result → validate → continue to next step

### How It Works

1. **Intent Classification**: Routes user input to "simple", "query", or "agent"
2. **Planning**: Planning agent generates structured JSON plan from natural language goal
3. **Execution**: Plan executor runs each step sequentially
4. **Memory**: Results are stored in plan memory for later steps
5. **Reasoning**: When step type is "reasoning", reasoning engine processes with LLM
6. **Completion**: Final result is formatted and returned to user

### Example Workflow
```
User: "create an event tonight at 9 PM with the subject from my homework note"

Agent Pipeline:
1. Planning: Generate plan to get notes, find homework note, create event
2. Execution: List all notes (returns "1. homework\n2. club things\n3. to do")
3. Reasoning: "Find the note titled 'homework' from the notes list" → extracts "homework"
4. Execution: Create event with title "homework" at 9 PM tonight
5. Result: "Event created: homework at 9 PM tonight"
```

### Supported Complex Workflows
- **Schedule Optimization**: "find the best time for a meeting this week"
- **Data Analysis**: "analyze my calendar and suggest productivity improvements"
- **Multi-Step Creation**: "create a study session for my most important todo item"
- **Contextual Actions**: "read my notes about the project and create a meeting for it"

## 3. Unified Architecture

### Unified LLM Client
**Problem**: The codebase had 4+ different ways to call the LLM with inconsistent configurations, error handling, and logging.

**Solution**: Single `UnifiedLLMClient` class that handles all LLM interactions:
- `extract_arguments()` - Slot-filling argument extraction
- `generate_followup_question()` - Hardcoded templates for speed
- `extract_argument_from_reply()` - Follow-up processing
- `generate_plan()` - Agentic planning
- `execute_reasoning()` - Reasoning steps
- `generate_general_response()` - General queries

**Benefits**: Consistent configuration, standardized error handling, unified logging, easier debugging.

### Unified Orchestrator
**Problem**: Two separate orchestrators with overlapping responsibilities and fragmented control flow.

**Solution**: Single `UnifiedOrchestrator` with clear routing logic:
- `process_user_input()` - Main entry point for all requests
- `_handle_simple_action()` - Fast slot-filling for simple actions
- `_handle_agentic_request()` - Complex planning/reasoning workflows
- `_handle_general_query()` - General knowledge queries
- Maintains separate memory systems (fast simple memory vs. rich agent memory)

**Benefits**: Cleaner architecture, single point of control, easier to understand flow, eliminates redundancy.

### Performance Optimizations

#### Slot-Filling Improvements
- **Timing Analysis**: Detailed timing logs to identify bottlenecks
- **Hardcoded Templates**: Replaced LLM-based follow-up generation with fast templates
- **Argument Extraction**: Improved prompts to reject generic values, only accept specific arguments
- **Impact**: Eliminated unnecessary LLM calls, reduced slot-filling latency

#### Intent Classification
- **Fast ML Classifier**: ~10ms intent classification using sentence transformers
- **Action Classification**: ML-based action prediction for simple intents
- **Routing**: Efficient routing to appropriate pipeline (simple/agentic/query)

## 4. Human Reinforcement Learning (Future)

### Problem
The intent classifier struggles to distinguish between "simple" and "agent" intents due to:
- Limited training data for complex multi-step workflows
- Ambiguous examples that could be either simple or agent
- No real-world feedback on classification accuracy
- Users often know better than the classifier when they need agent reasoning

### Solution: "Sam Agent" Command System
A human reinforcement learning system that leverages user expertise to improve the machine learning model.

#### How It Works
1. **User Override**: When classifier predicts "simple" but user needs agent reasoning, say "sam agent"
2. **Automatic Logging**: System logs the user input, original intent prediction, and override action
3. **Training Data Collection**: Logs become high-quality training examples for intent classifier
4. **Continuous Improvement**: Periodically retrain classifier with collected data

#### Implementation Details
- **"Sam Agent" Command**: Manual override capability for users
- **Failure Detection**: Automatic detection of simple action failures
- **Logging System**: Comprehensive logging of overrides and failures
- **Review Process**: Manual review for quality control
- **Retraining Pipeline**: Automated improvement process

#### Example Flow
```
User: "read my homework note"
[Classifier predicts: simple]
🤖 SAM: "I couldn't find a note titled 'homework'."

User: "sam agent"
🤖 SAM: "Switching to agent mode for: 'read my homework note'"
🤖 SAM: "Let me help you find your homework note. First, I'll list all your notes..."

[System logs: "read my homework note" (simple -> agent)]
```

#### Benefits
- **Real User Data**: Collects actual user behavior and language patterns
- **Targeted Improvement**: Focuses on the specific "agent" class that needs help
- **User Control**: Gives users direct control over when they need agent reasoning
- **Graceful Degradation**: System still works even when classifier is wrong
- **Continuous Learning**: Improves over time with real usage

## Technical Architecture

### File Structure
```
v5/
├── brain/
│   ├── unified_llm_client.py      # Single LLM interface
│   ├── unified_orchestrator.py    # Main orchestrator
│   ├── planning_agent.py          # Plan generation
│   ├── reasoning_engine.py        # Reasoning execution
│   ├── plan_executor.py           # Plan orchestration
│   ├── plan_memory.py             # Variable storage
│   └── execution.py               # Action execution
├── services/
│   ├── google_calendar.py         # Calendar integration
│   └── notes_service.py           # Notes management
├── STT/
│   └── vosk_stt.py                # Speech recognition
├── TTS/
│   └── tts_engine.py              # Text-to-speech
└── main.py                        # Entry point
```

### Key Design Principles
- **Voice-First**: All optimizations serve natural voice interaction
- **Performance**: Fast response times through careful LLM usage
- **Reliability**: Graceful degradation and error handling
- **Maintainability**: Clean architecture with unified components
- **Extensibility**: Easy to add new actions and capabilities

## Current Status

### What Works Well
- ✅ Voice integration with low-latency TTS/STT
- ✅ Fast slot-filling with hardcoded templates
- ✅ Agentic planning and reasoning pipeline
- ✅ Unified architecture with clean separation
- ✅ Intent classification and routing
- ✅ Google Calendar and notes integration

### What's Next
- 🔄 Implement "sam agent" command system
- 🔄 Add comprehensive logging for intent classifier improvements
- 🔄 Expand agent training data with real user examples
- 🔄 Optimize slot-filling performance further
- 🔄 Add more complex reasoning examples

---

**SAM v5 represents a sophisticated evolution from simple action-based assistance to a voice-first AI that can handle complex, multi-step reasoning while maintaining the speed and reliability needed for natural conversation.**

