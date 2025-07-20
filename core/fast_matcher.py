#!/usr/bin/env python3
"""
Fast Pattern Matcher - Handles 90% of queries without LLM
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class IntentMatch:
    action: Optional[str] = None
    confidence: float = 0.0
    args: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = {}

class FastMatcher:
    """Fast pattern-based intent matcher"""
    
    def __init__(self):
        # Simple patterns for common queries (order matters - more specific first)
        self.patterns = {
            'get_events': [
                r'\bshow.*events?\b',
                r'\bwhat.*events?\b',
                r'\bwhat do i have\b',
                r'\bupcoming.*events?\b',
                r'\bmy.*events?\b',
                r'\bevents.*today\b',
                r'\bevents.*tomorrow\b',
                r'\bevents.*next\b',
                r'\bnext.*events?\b',
                r'\bnext event\b',
                r'\bwhat.*next event\b',
                r'\bmy.*next event\b',
                r'\bupcoming\b',
                r'\bevents\b(?!\s+(?:called|named|for|at|on|tomorrow|today|tonight))'
            ],
            'create_event': [
                r'\bcreate.*event\b',
                r'\bcreate.*meeting\b',
                r'\bschedule.*meeting\b',
                r'\badd.*event\b',
                r'\bnew event\b',
                r'\bnew meeting\b',
                r'\bcreate.*new.*event\b'
            ],
            'get_time': [
                r'\bwhat time\b',
                r'\btime\b',
                r'\btell me the time\b'
            ],
            'get_date': [
                r'\bwhat date\b',
                r'\bdate\b',
                r'\btoday\'s date\b'
            ],
            'get_day': [
                r'\bwhat day\b',
                r'\bday\b',
                r'\btomorrow.*day\b'
            ],
            'greeting': [
                r'\bhi\b',
                r'\bhello\b',
                r'\bhey\b'
            ]
        }
    
    def match(self, query: str) -> IntentMatch:
        """Match query to intent with context awareness"""
        query_lower = query.lower().strip()
        
        # Check for single words that need context
        if query_lower in ['tomorrow', 'today', 'tonight']:
            # These could be date, day, or time queries - need LLM
            return IntentMatch(confidence=0.0)
        
        # Check patterns in order (more specific first)
        for action, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    confidence = self._calculate_confidence(query_lower, action)
                    return IntentMatch(action=action, confidence=confidence)
        
        return IntentMatch(confidence=0.0)
    
    def _calculate_confidence(self, query: str, action: str) -> float:
        """Calculate confidence based on query complexity and action type"""
        base_confidence = 0.8
        
        # Simple queries get higher confidence
        if len(query.split()) <= 3:
            base_confidence = 0.9
        
        # Time/date queries are very reliable
        if action in ['get_time', 'get_date', 'get_day']:
            base_confidence = 0.95
        
        # Complex queries get lower confidence
        if len(query.split()) > 6:
            base_confidence *= 0.9
        
        return min(base_confidence, 1.0) 