# SAM v5 Plan Generator

This is a standalone plan generator that converts natural language prompts into structured JSON plans using SAM v5's available actions and LLM interface.

## Overview

The plan generator takes a natural language request (like "Create an event to eat dinner when I'm free tonight") and converts it into a structured plan with multiple steps, each using available actions from SAM v5's action schema. It integrates seamlessly with v5's existing LLM interface and patterns.

## Files

- `plan_generator.py` - Main plan generator implementation (v5 integrated)
- `test_plan_generator.py` - Comprehensive test script with multiple modes
- `planning_requirements.txt` - Dependencies including v5 requirements
- `PLANNING_README.md` - This file

## Installation

1. Install dependencies:
```bash
pip install -r planning_requirements.txt
```

2. Make sure you have a local LLM server running (like Ollama) at `http://127.0.0.1:1234`

3. Ensure v5 directory is accessible (the plan generator imports from v5)

## Usage

### Basic Usage

```python
from plan_generator import PlanGenerator

generator = PlanGenerator()
plan = generator.generate_plan("Create an event to eat dinner when I'm free tonight")
print(plan.to_json())
```

### Test Scripts

Run the basic test:
```bash
python test_plan_generator.py
```

Run interactive mode:
```bash
python test_plan_generator.py --interactive
```

Run comprehensive testing:
```bash
python test_plan_generator.py --comprehensive
```

Run edge case testing:
```bash
python test_plan_generator.py --edge-cases
```

## v5 Integration Features

### **LLM Interface Integration**
- Uses v5's `LightweightLLM` class for API calls
- Follows v5's timing and debugging patterns
- Uses v5's configuration (API_URL, MODEL_NAME, MAX_RESPONSE_LENGTH)

### **Action Schema Integration**
- Directly imports and uses v5's `ACTIONS` schema
- Validates plans against actual v5 actions
- Ensures argument compatibility with v5's execution engine

### **Prompt Engineering**
- Follows v5's concise, example-driven prompt style
- Uses v5's error handling and logging patterns
- Maintains consistency with v5's LLM interaction patterns

## Plan Structure

A generated plan has this structure:

```json
{
  "goal": "Create an event to eat dinner when user is free tonight",
  "steps": [
    {
      "step_id": 1,
      "action": "get_events",
      "arguments": {
        "date": "today",
        "upcoming_only": true
      },
      "reasoning": "Check user's calendar to see what events are scheduled for tonight",
      "expected_output": "List of events after 5 PM today"
    },
    {
      "step_id": 2,
      "action": "create_event",
      "arguments": {
        "title": "Dinner",
        "start_time": "7:00 PM",
        "description": "Dinner event"
      },
      "reasoning": "Based on free time found, create the dinner event",
      "expected_output": "Confirmation of dinner event creation",
      "depends_on": [1],
      "conditional": "If free time found at 7 PM"
    }
  ]
}
```

## How It Works

1. **v5 Integration**: Loads v5's action schema and LLM interface
2. **Prompt Engineering**: Creates detailed prompts using v5's style with:
   - All available actions from v5's schema
   - Required and optional arguments for each action
   - Examples of how to create plans
   - Clear instructions for the LLM
3. **LLM Call**: Uses v5's `LightweightLLM` for API calls
4. **Plan Parsing**: Extracts and validates the JSON response
5. **Validation**: Ensures the plan only uses valid v5 actions and arguments

## Testing Modes

### **Single Test** (`--single`)
Tests the basic functionality with your example prompt.

### **Interactive Mode** (`--interactive`)
Allows you to enter prompts interactively and see generated plans with summaries.

### **Comprehensive Testing** (`--comprehensive`)
Tests multiple scenarios and validates that expected actions are present in generated plans.

### **Edge Case Testing** (`--edge-cases`)
Tests edge cases like empty prompts, greetings, and complex requests.

## Example Output

For the prompt "Create an event to eat dinner when I'm free tonight", the generator should create a plan like:

```json
{
  "goal": "Create an event to eat dinner when user is free tonight",
  "steps": [
    {
      "step_id": 1,
      "action": "get_events",
      "arguments": {
        "date": "today",
        "upcoming_only": true
      },
      "reasoning": "Check user's calendar to see what events are scheduled for tonight",
      "expected_output": "List of events after 5 PM today"
    },
    {
      "step_id": 2,
      "action": "create_event",
      "arguments": {
        "title": "Dinner",
        "start_time": "7:00 PM",
        "description": "Dinner event"
      },
      "reasoning": "Based on free time found, create the dinner event",
      "expected_output": "Confirmation of dinner event creation",
      "depends_on": [1],
      "conditional": "If free time found at 7 PM"
    }
  ]
}
```

## Available Actions in v5

The plan generator can use all actions from v5's schema:
- **Calendar**: `create_event`, `get_events`
- **Notes**: `create_note`, `read_note`, `edit_note`, `delete_note`, `list_notes`
- **Todos**: `add_todo`, `show_todo`, `clear_todo`, `remove_todo_item`
- **Time/Date**: `get_time`, `get_date`, `get_day`
- **General**: `greeting`, `unknown`

## Next Steps

This is just the plan generation part. The next steps would be:

1. **Plan Execution**: Execute each step in the plan using v5's execution engine
2. **Output Processing**: Parse the output of each step
3. **Conditional Logic**: Handle conditional steps based on previous outputs
4. **User Interaction**: Ask for confirmation when needed
5. **Integration**: Integrate this into SAM v5's main loop

## Troubleshooting

- **LLM Connection Error**: Make sure your local LLM server is running at `http://127.0.0.1:1234`
- **v5 Import Error**: Ensure the v5 directory is accessible and contains the required modules
- **Invalid Plan**: The generator includes validation to ensure plans only use valid v5 actions
- **JSON Parsing Error**: The LLM might add extra text - the parser tries to extract just the JSON part

## v5 Compatibility

This plan generator is designed to work seamlessly with SAM v5:
- Uses the same LLM interface and configuration
- Validates against the actual v5 action schema
- Follows v5's coding patterns and conventions
- Ready for integration into v5's main execution loop 