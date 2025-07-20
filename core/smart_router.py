#!/usr/bin/env python3
"""
Smart Router - Decides when to use pattern matching vs LLM
"""

from typing import Dict, Any
from .fast_matcher import FastMatcher, IntentMatch
from .lightweight_llm import LightweightLLM

class SmartRouter:
    """Smart router that optimizes between pattern matching and LLM"""
    
    def __init__(self, mock_mode=False):
        self.fast_matcher = FastMatcher()
        self.llm = LightweightLLM(mock_mode=mock_mode)
        self.confidence_threshold = 0.8
    
    def route(self, query: str) -> Dict[str, Any]:
        """Route query to appropriate handler"""
        # Step 1: Try fast pattern matching
        pattern_match = self.fast_matcher.match(query)
        
        # Step 2: Check if we need LLM
        if self._needs_llm(pattern_match, query):
            # Use lightweight LLM for complex cases
            llm_result = self.llm.classify_intent(query)
            
            # Prefer LLM if pattern match was low confidence
            if pattern_match.confidence < 0.5:
                return llm_result
            else:
                # Use pattern match but enhance if needed
                return {
                    "action": pattern_match.action,
                    "confidence": pattern_match.confidence
                }
        else:
            # Use pattern match result directly
            return {
                "action": pattern_match.action,
                "confidence": pattern_match.confidence
            }
    
    def _needs_llm(self, pattern_match: IntentMatch, query: str) -> bool:
        """Determine if LLM is needed"""
        # Always use LLM if no pattern matched
        if pattern_match.confidence == 0.0:
            return True
        
        # Use LLM if confidence is below threshold
        if pattern_match.confidence < self.confidence_threshold:
            return True
        
        # Use LLM for complex queries
        if len(query.split()) > 8:
            return True
        
        return False
    
    def generate_response(self, result: str) -> str:
        """Generate response using lightweight LLM"""
        return self.llm.generate_response(result)
    
    def extract_time(self, query: str) -> str:
        """Extract time information"""
        return self.llm.extract_time(query) 