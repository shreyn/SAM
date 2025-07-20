#!/usr/bin/env python3
"""
Two-Stage Intent Classification System
Stage 1: Intent Type (QUERY, ACTION, GREETING, UNKNOWN)
Stage 2: Specific Action within each type
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class IntentResult:
    """Result of intent classification"""
    intent_type: str  # QUERY, ACTION, GREETING, UNKNOWN
    action: str       # Specific action (get_events, create_event, etc.)
    confidence: float
    args: Dict[str, any] = None
    
    def __post_init__(self):
        if self.args is None:
            self.args = {}

class IntentClassifier:
    """Two-stage intent classification system"""
    
    def __init__(self):
        # Stage 1: Intent Type Classification
        self.intent_types = {
            'QUERY': [
                r'\bwhat\b', r'\bshow\b', r'\btell\b', r'\bdo i have\b', 
                r'\bare there\b', r'\bwhen\b', r'\bwhere\b', r'\bhow many\b',
                r'\bnext\b', r'\bupcoming\b', r'\bmy\b', r'\bevents?\b',
                r'\btime\b', r'\bdate\b', r'\bday\b'
            ],
            'ACTION': [
                r'\bcreate\b', r'\badd\b', r'\bmake\b', r'\bschedule\b', 
                r'\bbook\b', r'\bset up\b', r'\bnew\b', r'\bstart\b'
            ],
            'GREETING': [
                r'\bhi\b', r'\bhello\b', r'\bhey\b', r'\bgood morning\b',
                r'\bgood afternoon\b', r'\bgood evening\b'
            ]
        }
        
        # Stage 2: Query Actions
        self.query_actions = {
            'get_events': [
                r'\bevents?\b', r'\bmeetings?\b', r'\bappointments?\b', 
                r'\bschedule\b', r'\bcalendar\b'
            ],
            'get_time': [
                r'\btime\b', r'\bclock\b', r'\bhour\b', r'\bcurrent time\b'
            ],
            'get_date': [
                r'\bdate\b', r'\btoday\'s date\b', r'\bwhat date\b'
            ],
            'get_day': [
                r'\bday\b', r'\bwhat day\b', r'\bday of week\b'
            ],
            'get_notes': [
                r'\bnotes?\b', r'\bshow.*notes?\b', r'\bmy.*notes?\b', 
                r'\ball.*notes?\b', r'\blist.*notes?\b'
            ],
            'search_notes': [
                r'\bsearch.*notes?\b', r'\bfind.*notes?\b', r'\blook.*for.*notes?\b'
            ],
            'get_tags': [
                r'\btags?\b', r'\bshow.*tags?\b', r'\ball.*tags?\b'
            ]
        }
        
        # Stage 2: Action Actions
        self.action_actions = {
            'create_event': [
                r'\bevents?\b', r'\bmeetings?\b', r'\bappointments?\b'
            ],
            'create_task': [
                r'\btasks?\b', r'\btodos?\b', r'\breminders?\b'
            ],
            'create_note': [
                r'\bnotes?\b', r'\bmemos?\b', r'\breminders?\b', r'\bwrite.*note\b'
            ],
            'update_note': [
                r'\bedit.*note\b', r'\bupdate.*note\b', r'\bmodify.*note\b'
            ],
            'delete_note': [
                r'\bdelete.*note\b', r'\bremove.*note\b', r'\btrash.*note\b'
            ]
        }
    
    def classify(self, query: str) -> IntentResult:
        """Classify intent using two-stage approach"""
        query_lower = query.lower().strip()
        
        # Stage 1: Determine intent type
        intent_type, type_confidence = self._classify_intent_type(query_lower)
        
        # Stage 2: Determine specific action
        action, action_confidence = self._classify_action(query_lower, intent_type)
        
        # Calculate overall confidence
        overall_confidence = (type_confidence + action_confidence) / 2
        
        # If action is unknown, treat as UNKNOWN intent
        if action == 'unknown':
            intent_type = 'UNKNOWN'
            overall_confidence = 0.0
        
        # Extract arguments based on action
        args = self._extract_args(query_lower, action)
        
        return IntentResult(
            intent_type=intent_type,
            action=action,
            confidence=overall_confidence,
            args=args
        )
    
    def _classify_intent_type(self, query: str) -> Tuple[str, float]:
        """Stage 1: Classify intent type"""
        best_type = 'UNKNOWN'
        best_confidence = 0.0
        
        for intent_type, patterns in self.intent_types.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    # Calculate confidence based on pattern strength and query length
                    confidence = self._calculate_pattern_confidence(pattern, query)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_type = intent_type
        
        return best_type, best_confidence
    
    def _classify_action(self, query: str, intent_type: str) -> Tuple[str, float]:
        """Stage 2: Classify specific action within intent type"""
        if intent_type == 'QUERY':
            return self._classify_query_action(query)
        elif intent_type == 'ACTION':
            return self._classify_action_action(query)
        elif intent_type == 'GREETING':
            return 'greeting', 1.0
        else:
            return 'unknown', 0.0
    
    def _classify_query_action(self, query: str) -> Tuple[str, float]:
        """Classify query actions"""
        best_action = 'unknown'
        best_confidence = 0.0
        
        for action, patterns in self.query_actions.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    confidence = self._calculate_pattern_confidence(pattern, query)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_action = action
        
        # If no specific action found, return unknown
        if best_action == 'unknown':
            return 'unknown', 0.0
        
        return best_action, best_confidence
    
    def _classify_action_action(self, query: str) -> Tuple[str, float]:
        """Classify action actions"""
        best_action = 'unknown'
        best_confidence = 0.0
        
        for action, patterns in self.action_actions.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    confidence = self._calculate_pattern_confidence(pattern, query)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_action = action
        
        return best_action, best_confidence
    
    def _calculate_pattern_confidence(self, pattern: str, query: str) -> float:
        """Calculate confidence based on pattern strength and query context"""
        base_confidence = 0.8
        
        # Boost confidence for exact matches
        if pattern.strip('\\b') in query:
            base_confidence = 0.95
        
        # Boost confidence for longer, more specific patterns
        if len(pattern.split()) > 1:
            base_confidence += 0.1
        
        # Reduce confidence for very short queries
        if len(query.split()) <= 2:
            base_confidence *= 0.9
        
        return min(base_confidence, 1.0)
    
    def _extract_args(self, query: str, action: str) -> Dict[str, any]:
        """Extract arguments based on the action"""
        args = {}
        
        if action == 'get_events':
            # Extract date filters
            if 'today' in query:
                args['date'] = 'today'
            elif 'tomorrow' in query or 'tomororw' in query:  # Handle typo
                args['date'] = 'tomorrow'
            elif 'next' in query:
                # Check if it's "next X events" or "next day"
                next_match = re.search(r'next\s+(\d+)\s+events?', query)
                if next_match:
                    args['limit'] = int(next_match.group(1))
                    args['upcoming_only'] = True
                else:
                    day_match = re.search(r'next\s+(\w+)', query)
                    if day_match:
                        args['date'] = f"next {day_match.group(1)}"
            
            # Check for "next event" (singular) - single next event
            if re.search(r'\bnext\s+event\b(?!\w)', query, re.IGNORECASE):
                args['next_single'] = True
                args['limit'] = 1
                args['remaining_today'] = True  # Look for next event remaining today
            
            # Check for "next events" (plural) or "upcoming events" - remaining today
            elif re.search(r'\bnext\s+events\b', query, re.IGNORECASE) or re.search(r'\bupcoming\s+events?\b', query, re.IGNORECASE):
                args['remaining_today'] = True
                args['upcoming_only'] = True
                # Explicitly remove any limit for these queries
                if 'limit' in args:
                    del args['limit']
            
            # Check for general upcoming only
            elif any(word in query for word in ['upcoming', 'future']):
                args['upcoming_only'] = True
            
            # Check for limit (only if not already set by specific patterns)
            if 'limit' not in args:
                limit_match = re.search(r'(\d+)\s+events?', query)
                if limit_match:
                    args['limit'] = int(limit_match.group(1))
        
        elif action == 'create_event':
            # Extract title
            title = self._extract_title(query)
            if title:
                args['title'] = title
            
            # Extract time info
            time_info = self._extract_time_info(query)
            if time_info:
                args['start_time'] = time_info
        
        elif action == 'create_note':
            # Extract title
            title = self._extract_note_title(query)
            if title:
                args['title'] = title
            
            # Extract content
            content = self._extract_note_content(query)
            if content:
                args['content'] = content
            
            # Extract tags
            tags = self._extract_tags(query)
            if tags:
                args['tags'] = tags
        
        elif action == 'search_notes':
            # Extract search query
            query_text = self._extract_search_query(query)
            if query_text:
                args['query'] = query_text
        
        elif action == 'get_notes':
            # Extract filters
            if 'recent' in query:
                args['recent_only'] = True
            
            # Extract tag filter
            tag = self._extract_tag_filter(query)
            if tag:
                args['tag'] = tag
            
            # Extract limit
            limit_match = re.search(r'(\d+)\s+notes?', query)
            if limit_match:
                args['limit'] = int(limit_match.group(1))
        
        elif action in ['update_note', 'delete_note', 'get_note']:
            # Extract note ID
            note_id = self._extract_note_id(query)
            if note_id:
                args['note_id'] = note_id
        
        elif action in ['get_date', 'get_day']:
            # Extract target date/day
            if 'tomorrow' in query:
                args['target_date'] = 'tomorrow'
                args['target_day'] = 'tomorrow'
        
        return args
    
    def _extract_title(self, query: str) -> Optional[str]:
        """Extract event title from query"""
        # Look for "called" or "named" patterns
        patterns = [
            r'called\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:tomorrow|today|tonight|next|at|on|for|meeting|event|appointment))?',
            r'named\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:tomorrow|today|tonight|next|at|on|for|meeting|event|appointment))?',
            r'for\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:tomorrow|today|tonight|next|at|on|for|meeting|event|appointment))?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                title = match.group(1).strip()
                if title and title not in ['a', 'an', 'the', 'event', 'appointment']:
                    return title
        
        return None
    
    def _extract_time_info(self, query: str) -> Optional[str]:
        """Extract time information from query using centralized parser"""
        from utils.time_parser import extract_time_info
        return extract_time_info(query)
    
    def _extract_note_title(self, query: str) -> Optional[str]:
        """Extract note title from query"""
        patterns = [
            r'called\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:about|with|for|note|memo))?',
            r'named\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:about|with|for|note|memo))?',
            r'titled\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:about|with|for|note|memo))?',
            r'about\s+([^,\s]+(?:\s+[^,\s]+)*?)(?:\s+(?:note|memo))?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if title and title not in ['a', 'an', 'the', 'note', 'memo']:
                    return title
        
        return None
    
    def _extract_note_content(self, query: str) -> Optional[str]:
        """Extract note content from query"""
        # Look for content after "about" or "that says" or similar
        patterns = [
            r'about\s+(.+?)(?:\s+(?:called|named|titled|with|tags?))?$',
            r'that\s+says?\s+(.+?)(?:\s+(?:called|named|titled|with|tags?))?$',
            r'content\s+(.+?)(?:\s+(?:called|named|titled|with|tags?))?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                if content and len(content) > 3:
                    return content
        
        return None
    
    def _extract_tags(self, query: str) -> Optional[List[str]]:
        """Extract tags from query"""
        # Look for tags after "with tags" or "tagged as"
        patterns = [
            r'with\s+tags?\s+(.+?)(?:\s+(?:called|named|titled|about))?$',
            r'tagged\s+as\s+(.+?)(?:\s+(?:called|named|titled|about))?$',
            r'tags?\s+(.+?)(?:\s+(?:called|named|titled|about))?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                tags_text = match.group(1).strip()
                # Split by comma and clean up
                tags = [tag.strip() for tag in tags_text.split(',')]
                tags = [tag for tag in tags if tag and len(tag) > 0]
                if tags:
                    return tags
        
        return None
    
    def _extract_search_query(self, query: str) -> Optional[str]:
        """Extract search query from query"""
        # Look for search terms after "for" or "about"
        patterns = [
            r'for\s+(.+?)(?:\s+(?:notes?|memos?))?$',
            r'about\s+(.+?)(?:\s+(?:notes?|memos?))?$',
            r'containing\s+(.+?)(?:\s+(?:notes?|memos?))?$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                search_query = match.group(1).strip()
                if search_query and len(search_query) > 2:
                    return search_query
        
        return None
    
    def _extract_tag_filter(self, query: str) -> Optional[str]:
        """Extract tag filter from query"""
        # Look for tag after "with tag" or "tagged"
        patterns = [
            r'with\s+tag\s+(\w+)',
            r'tagged\s+(\w+)',
            r'tag\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                tag = match.group(1).strip()
                if tag:
                    return tag
        
        return None
    
    def _extract_note_id(self, query: str) -> Optional[str]:
        """Extract note ID from query"""
        # Look for note ID patterns
        patterns = [
            r'note\s+(note_\d{8}_\d{6})',
            r'id\s+(note_\d{8}_\d{6})',
            r'(note_\d{8}_\d{6})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                note_id = match.group(1).strip()
                if note_id:
                    return note_id
        
        return None 