#!/usr/bin/env python3
"""
Planning Prompts - Prompt templates for the planning agent
"""

from typing import Dict, Any

def build_planning_prompt(user_goal: str, actions_schema: Dict[str, Any]) -> str:
    """
    Build a comprehensive prompt for the planning agent.
    
    Args:
        user_goal: Natural language description of what the user wants
        actions_schema: Dictionary of available actions and their specifications
        
    Returns:
        Formatted planning prompt
    """
    
    # Format available actions for the LLM
    actions_description = _format_actions_for_llm(actions_schema)
    
    prompt = f"""You are a planning agent that creates structured execution plans from user goals.

AVAILABLE ACTIONS:
{actions_description}

TASK: Create a step-by-step plan to accomplish the user's goal.

INSTRUCTIONS:
1. Analyze the goal carefully and break it down into logical steps
2. Use the available actions to create a plan
3. Consider what information might be needed (e.g., check availability before creating events)
4. Use reasoning steps when you need to process data or make decisions
5. Store intermediate results using the "save_as" field when needed
6. Use template variables like ${{variable_name}} to reference stored data
7. CRITICAL: Every step that produces data needed by later steps MUST include a "save_as" field
8. Return ONLY a valid JSON object with this exact structure:

{{
    "goal": "description of the user's goal",
    "steps": [
        {{
            "id": "s1",
            "action": "action_name",
            "args": {{"arg1": "value1"}},
            "save_as": "variable_name"
        }},
        {{
            "id": "s2", 
            "reasoning": "process the data to find the best time",
            "save_as": "result_variable"
        }},
        {{
            "id": "s3",
            "action": "create_event",
            "args": {{"title": "dinner", "start_time": "${{result_variable}}"}}
        }}
    ]
}}

EXAMPLES:

User: "create a dinner event tonight when im free"
{{
    "goal": "Create a dinner event for tonight when the user is available",
    "steps": [
        {{
            "id": "s1",
            "action": "get_events",
            "args": {{"date": "today"}},
            "save_as": "events_list"
        }},
        {{
            "id": "s2",
            "reasoning": "Find first available 1-hour slot between 6 PM and 10 PM from the events list",
            "save_as": "free_slot"
        }},
        {{
            "id": "s3",
            "action": "create_event",
            "args": {{"title": "dinner", "start_time": "${{free_slot}}"}}
        }}
    ]
}}

User: "add the most important tasks to my todo list"
{{
    "goal": "Add important tasks to the user's todo list",
    "steps": [
        {{
            "id": "s1",
            "action": "list_notes",
            "args": {{}},
            "save_as": "notes_list"
        }},
        {{
            "id": "s2",
            "reasoning": "Identify the most important tasks from the notes list",
            "save_as": "important_tasks"
        }},
        {{
            "id": "s3",
            "action": "add_todo",
            "args": {{"item": "${{important_tasks}}"}}
        }}
    ]
}}

User: "read my homework note and create an event with the subject name"
{{
    "goal": "Read homework note content and create an event with the subject",
    "steps": [
        {{
            "id": "s1",
            "action": "list_notes",
            "args": {{}},
            "save_as": "notes_list"
        }},
        {{
            "id": "s2",
            "reasoning": "Find the note titled 'homework' from the notes list",
            "save_as": "homework_note_title"
        }},
        {{
            "id": "s3",
            "action": "read_note",
            "args": {{"title": "${{homework_note_title}}"}},
            "save_as": "homework_content"
        }},
        {{
            "id": "s4",
            "reasoning": "Extract the subject name from the homework content",
            "save_as": "subject_name"
        }},
        {{
            "id": "s5",
            "action": "create_event",
            "args": {{"title": "${{subject_name}}", "start_time": "9:00 PM"}}
        }}
    ]
}}

IMPORTANT: Every step that produces data needed by later steps MUST include a "save_as" field to store the result in memory.

User: "{user_goal}"

Return ONLY the JSON plan:"""
    
    return prompt

def _format_actions_for_llm(actions_schema: Dict[str, Any]) -> str:
    """
    Format the action schema in a way that's easy for the LLM to understand.
    
    Args:
        actions_schema: Dictionary of available actions
        
    Returns:
        Formatted string representation of actions
    """
    formatted_actions = []
    
    for action_name, action_info in actions_schema.items():
        required_args = ", ".join(action_info["required_args"]) if action_info["required_args"] else "none"
        optional_args = ", ".join(action_info["optional_args"]) if action_info["optional_args"] else "none"
        
        # Add specific usage notes for key actions
        usage_note = ""
        if action_name == "list_notes":
            usage_note = " (returns numbered list of note titles, not content)"
        elif action_name == "read_note":
            usage_note = " (returns the actual content of a specific note)"
        elif action_name == "get_events":
            usage_note = " (returns event details, not just titles)"
        
        formatted_action = f"""- {action_name}:
  Description: {action_info['description']}{usage_note}
  Required args: {required_args}
  Optional args: {optional_args}"""
        
        formatted_actions.append(formatted_action)
    
    return "\n".join(formatted_actions) 