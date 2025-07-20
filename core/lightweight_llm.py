#!/usr/bin/env python3
"""
Lightweight LLM Client - Only for complex queries
"""

import requests
import json
from typing import Dict, Any
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import API_URL, MODEL_NAME

class LightweightLLM:
    """Minimal LLM client for complex queries only"""
    
    def __init__(self, mock_mode=False):
        self.api_url = API_URL
        self.model_name = MODEL_NAME
        self.mock_mode = mock_mode
    
    def classify_intent(self, query: str) -> Dict[str, Any]:
        """Classify intent for complex queries"""
        if self.mock_mode:
            # Intelligent intent classification
            query_lower = query.lower()
            
            # Handle single words with context
            if query_lower == "tomorrow":
                return {"action": "get_date", "confidence": 0.8}  # Most likely asking for date
            elif query_lower == "today":
                return {"action": "get_date", "confidence": 0.8}
            elif query_lower == "tonight":
                return {"action": "get_time", "confidence": 0.7}  # Could be time or date
            
            # Handle specific patterns
            if "time" in query_lower and "what" in query_lower:
                return {"action": "get_time", "confidence": 0.9}
            elif "date" in query_lower and "what" in query_lower:
                return {"action": "get_date", "confidence": 0.9}
            elif "day" in query_lower and "what" in query_lower:
                return {"action": "get_day", "confidence": 0.9}
            elif "create" in query_lower and ("event" in query_lower or "meeting" in query_lower):
                return {"action": "create_event", "confidence": 0.8}
            elif "new" in query_lower and ("event" in query_lower or "meeting" in query_lower):
                return {"action": "create_event", "confidence": 0.8}
            elif "hi" in query_lower or "hello" in query_lower:
                return {"action": "greeting", "confidence": 0.9}
            elif "event" in query_lower or "meeting" in query_lower:
                return {"action": "create_event", "confidence": 0.7}
            else:
                return {"action": "unknown", "confidence": 0.0}
        
        system_prompt = """Classify intent. Respond with: action|confidence
Examples:
- "What time is it?" → get_time|0.95
- "Create meeting tomorrow" → create_event|0.9
- "Hi there" → greeting|0.8"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        response = self._chat_completion(messages, max_tokens=20)
        
        try:
            parts = response.strip().split('|')
            if len(parts) >= 2:
                return {
                    "action": parts[0].strip(),
                    "confidence": float(parts[1].strip())
                }
        except:
            pass
        
        return {"action": "unknown", "confidence": 0.0}
    
    def extract_time(self, query: str) -> str:
        """Extract time information using centralized parser"""
        from utils.time_parser import extract_time_info
        time_info = extract_time_info(query)
        if time_info:
            return time_info
        else:
            return "today|"  # Default fallback
    
    def generate_response(self, result: str) -> str:
        """Generate natural response"""
        if self.mock_mode:
            # Intelligent response generation
            if "Hello! I'm SAM" in result:
                return result  # Greetings stay as-is
            elif "Event created" in result:
                return result  # Event confirmations stay as-is
            elif "No upcoming events" in result:
                return result  # Event responses stay as-is
            elif ":" in result and ("PM" in result or "AM" in result):
                return f"It's {result}"  # Time responses get "It's"
            elif result in ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                return result  # Day names stay as-is
            elif "July" in result or "August" in result or "September" in result:
                return result  # Date responses stay as-is
            else:
                return result  # Everything else stays as-is
        
        if any(phrase in result.lower() for phrase in ['events for', 'your next', 'no events', 'created for']):
            return result
        
        system_prompt = """Generate brief response. Examples:
- "2:30 PM" → "It's 2:30 PM"
- "July 19, 2025" → "July 19, 2025" """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Result: {result}"}
        ]
        
        return self._chat_completion(messages, max_tokens=15)
    
    def generate_general_response(self, query: str) -> str:
        """Generate a short, helpful response for general queries"""
        system_prompt = """You are SAM, a personal assistant. Respond naturally to each query as if it's a fresh conversation.

For factual questions (what is, how many, when, where): Give direct, concise answers.
For conversational comments (wow, that's cool, etc.): Respond naturally and conversationally.
For social questions (jokes, favorites, etc.): Be warm and engaging.
For complex questions (academic, technical, etc.): Be slightly more detailed, but still concise. 
Examples:
- "What's the moon's size?" → "The moon's diameter is 2,159 miles."
- "Wow, that's far!" → "Yeah, it really is! Space is pretty incredible."
- "Tell me a joke" → "Why don't scientists trust atoms? Because they make up everything!"
- "That's interesting" → "I think so too! What caught your attention?"

Keep responses natural and conversational (1-2 sentences)."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        return self._chat_completion(messages, max_tokens=60)
    
    def _chat_completion(self, messages: list, max_tokens: int = 20) -> str:
        """Send minimal chat completion request"""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=5
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            return f"Error: {str(e)}" 