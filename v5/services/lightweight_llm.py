#!/usr/bin/env python3
"""
Lightweight LLM Client - Only for complex queries
"""

import requests
from v5.utils.config import API_URL, MODEL_NAME, MAX_RESPONSE_LENGTH

class LightweightLLM:
    """Minimal LLM client for prompt/response generation"""
    def __init__(self):
        self.api_url = API_URL
        self.model_name = MODEL_NAME

    def generate_response(self, prompt: str, max_tokens: int = None) -> str:
        if max_tokens is None:
            max_tokens = MAX_RESPONSE_LENGTH
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        return self._chat_completion(messages, max_tokens=max_tokens)

    def generate_general_response(self, query: str) -> str:
        system_prompt = (
            "You are SAM, a personal assistant. Respond naturally to each query as if it's a fresh conversation.\n"
            "For factual, info questions (what is, how many, when, where): Give direct, concise answers.\n"
            "For conversational comments (wow, that's cool, etc.): Respond naturally and conversationally.\n"
            "For social questions (jokes, favorites, etc.): Be warm and engaging.\n"
            "For complex questions (academic, technical, etc.): Be slightly more detailed, but still concise.\n"
            "Examples:\n"
            "- 'What's the moon's size?' → 'The moon's diameter is 2,159 miles.'\n"
            "- 'Wow, that's far!' → 'Yeah, it really is! Space is pretty incredible.'\n"
            "- 'Tell me a joke' → 'Why don't scientists trust atoms? Because they make up everything!'\n"
            "- 'That's interesting' → 'I think so too! What caught your attention?'\n"
            "Keep responses natural and conversational (1-2 sentences)."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        return self._chat_completion(messages)

    def _chat_completion(self, messages: list, max_tokens: int = None) -> str:
        if max_tokens is None:
            max_tokens = MAX_RESPONSE_LENGTH
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