#!/usr/bin/env python3
"""
Comprehensive SAM Test Suite
Tests all current capabilities of SAM including:
- Time and date queries
- Event creation and management
- Follow-up conversations
- LLM fallback for unknown queries
- Day-of-week parsing
- Edge cases and error handling
"""

import time
from core.brain import SAMBrain

class ComprehensiveSAMTest:
    """Comprehensive test suite for SAM"""
    
    def __init__(self):
        self.sam = SAMBrain()
        self.test_results = []
        self.current_section = ""
        
    def log_test(self, query: str, response: str, expected_type: str = "success"):
        """Log a test result"""
        result = {
            'section': self.current_section,
            'query': query,
            'response': response,
            'type': expected_type
        }
        self.test_results.append(result)
        
        # Print the test
        print(f"👤 Query: {query}")
        print(f"🤖 Response: {response}")
        print(f"📊 Type: {expected_type}")
        print("-" * 60)
        
        # Add delay to avoid overwhelming the API
        time.sleep(0.5)
    
    def test_greetings(self):
        """Test greeting functionality"""
        self.current_section = "Greetings"
        print(f"\n{'='*20} TESTING GREETINGS {'='*20}")
        
        greetings = [
            "hi",
            "hello",
            "hey there",
            "good morning",
            "good afternoon",
            "good evening"
        ]
        
        for greeting in greetings:
            response = self.sam.process_message(greeting)
            self.log_test(greeting, response, "greeting")
    
    def test_time_queries(self):
        """Test time-related queries"""
        self.current_section = "Time Queries"
        print(f"\n{'='*20} TESTING TIME QUERIES {'='*20}")
        
        time_queries = [
            "what time is it",
            "time",
            "tell me the time",
            "current time",
            "what's the time"
        ]
        
        for query in time_queries:
            response = self.sam.process_message(query)
            self.log_test(query, response, "time_query")
    
    def test_date_queries(self):
        """Test date-related queries"""
        self.current_section = "Date Queries"
        print(f"\n{'='*20} TESTING DATE QUERIES {'='*20}")
        
        date_queries = [
            "what date is it",
            "date",
            "today's date",
            "what's the date today",
            "current date"
        ]
        
        for query in date_queries:
            response = self.sam.process_message(query)
            self.log_test(query, response, "date_query")
    
    def test_day_queries(self):
        """Test day-of-week queries"""
        self.current_section = "Day Queries"
        print(f"\n{'='*20} TESTING DAY QUERIES {'='*20}")
        
        day_queries = [
            "what day is it",
            "day",
            "what day of the week",
            "today's day",
            "what day is today"
        ]
        
        for query in day_queries:
            response = self.sam.process_message(query)
            self.log_test(query, response, "day_query")
    
    def test_event_queries(self):
        """Test event querying functionality"""
        self.current_section = "Event Queries"
        print(f"\n{'='*20} TESTING EVENT QUERIES {'='*20}")
        
        event_queries = [
            "do i have events today",
            "show my events",
            "what events do i have",
            "my schedule",
            "upcoming events",
            "next event",
            "next events",
            "events tomorrow",
            "do i have any meetings",
            "show my calendar"
        ]
        
        for query in event_queries:
            response = self.sam.process_message(query)
            self.log_test(query, response, "event_query")
    
    def test_simple_event_creation(self):
        """Test simple event creation with all info provided"""
        self.current_section = "Simple Event Creation"
        print(f"\n{'='*20} TESTING SIMPLE EVENT CREATION {'='*20}")
        
        simple_events = [
            "create event called team meeting tomorrow at 2pm",
            "schedule a dentist appointment today at 3:30 pm",
            "add event called lunch meeting tonight at 12 pm",
            "create meeting called weekly standup tomorrow at 9 am",
            "schedule event called study session today at 7 pm"
        ]
        
        for query in simple_events:
            response = self.sam.process_message(query)
            self.log_test(query, response, "simple_event_creation")
    
    def test_day_of_week_event_creation(self):
        """Test event creation with day-of-week parsing"""
        self.current_section = "Day-of-Week Event Creation"
        print(f"\n{'='*20} TESTING DAY-OF-WEEK EVENT CREATION {'='*20}")
        
        day_events = [
            "create event called team meeting monday at 4 pm",
            "schedule dentist appointment tuesday at 3:30",
            "add event called lunch meeting wednesday at 12 pm",
            "create meeting called weekly review thursday at 2 pm",
            "schedule event called study session friday at 7 pm",
            "4 pm on monday",
            "3:30 on tuesday",
            "wednesday at 2 pm",
            "thursday at 10 am",
            "friday at 5 pm"
        ]
        
        for query in day_events:
            response = self.sam.process_message(query)
            self.log_test(query, response, "day_of_week_event_creation")
    
    def test_event_creation_follow_ups(self):
        """Test event creation with follow-up conversations"""
        self.current_section = "Event Creation Follow-ups"
        print(f"\n{'='*20} TESTING EVENT CREATION FOLLOW-UPS {'='*20}")
        
        # Test 1: Create event without title
        print("Test 1: Create event without title")
        response1 = self.sam.process_message("create an event tomorrow at 3pm")
        self.log_test("create an event tomorrow at 3pm", response1, "follow_up_start")
        
        response2 = self.sam.process_message("team meeting")
        self.log_test("team meeting", response2, "follow_up_title")
        
        # Test 2: Create event without time
        print("\nTest 2: Create event without time")
        response3 = self.sam.process_message("create event called doctor appointment")
        self.log_test("create event called doctor appointment", response3, "follow_up_start")
        
        response4 = self.sam.process_message("tomorrow at 10 am")
        self.log_test("tomorrow at 10 am", response4, "follow_up_time")
        
        # Test 3: Create event with just action
        print("\nTest 3: Create event with just action")
        response5 = self.sam.process_message("create event")
        self.log_test("create event", response5, "follow_up_start")
        
        response6 = self.sam.process_message("lunch meeting")
        self.log_test("lunch meeting", response6, "follow_up_title")
        
        response7 = self.sam.process_message("friday at 1 pm")
        self.log_test("friday at 1 pm", response7, "follow_up_time")
    
    def test_llm_fallback(self):
        """Test LLM fallback for unknown queries"""
        self.current_section = "LLM Fallback"
        print(f"\n{'='*20} TESTING LLM FALLBACK {'='*20}")
        
        unknown_queries = [
            "what is the size of the moon",
            "tell me a joke",
            "what's the weather like",
            "who won the world cup",
            "what is the capital of France",
            "how do I make coffee",
            "what's the meaning of life",
            "can you help me with math",
            "what's the best pizza place",
            "how do I learn to code"
        ]
        
        for query in unknown_queries:
            response = self.sam.process_message(query)
            self.log_test(query, response, "llm_fallback")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        self.current_section = "Edge Cases"
        print(f"\n{'='*20} TESTING EDGE CASES {'='*20}")
        
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "a",  # Single character
            "123",  # Numbers only
            "!@#$%^&*()",  # Special characters only
            "tomorrow",  # Single word that could be ambiguous
            "today",  # Single word that could be ambiguous
            "tonight",  # Single word that could be ambiguous
            "next",  # Incomplete phrase
            "create",  # Incomplete action
            "event",  # Single word
            "meeting",  # Single word
            "time",  # Single word
            "date",  # Single word
            "day"  # Single word
        ]
        
        for query in edge_cases:
            response = self.sam.process_message(query)
            self.log_test(query, response, "edge_case")
    
    def test_complex_queries(self):
        """Test complex, multi-part queries"""
        self.current_section = "Complex Queries"
        print(f"\n{'='*20} TESTING COMPLEX QUERIES {'='*20}")
        
        complex_queries = [
            "can you please create a meeting called quarterly review for next monday at 2:30 pm in the conference room",
            "i need to schedule a dentist appointment for tuesday afternoon around 3 pm",
            "please add an event for my team standup meeting tomorrow morning at 9 am",
            "create a calendar event for the project kickoff meeting on wednesday at 10:30 am",
            "schedule a lunch meeting with the client on friday at 12:30 pm",
            "i want to create an event called study session for tonight at 7 pm",
            "please add a reminder for my doctor's appointment tomorrow at 11 am",
            "create a meeting called weekly planning session for thursday at 3 pm"
        ]
        
        for query in complex_queries:
            response = self.sam.process_message(query)
            self.log_test(query, response, "complex_query")
    
    def test_mixed_conversation(self):
        """Test mixed conversation flow"""
        self.current_section = "Mixed Conversation"
        print(f"\n{'='*20} TESTING MIXED CONVERSATION {'='*20}")
        
        conversation = [
            "hi there",
            "what time is it",
            "do i have events today",
            "create event called team meeting tomorrow at 3pm",
            "what day is it",
            "tell me a joke",
            "what's the weather like",
            "create event called lunch meeting friday at 12pm",
            "what date is it",
            "who won the world cup"
        ]
        
        for query in conversation:
            response = self.sam.process_message(query)
            self.log_test(query, response, "mixed_conversation")
    
    def run_all_tests(self):
        """Run all test categories"""
        print("🚀 STARTING COMPREHENSIVE SAM TEST SUITE")
        print("=" * 80)
        
        try:
            self.test_greetings()
            self.test_time_queries()
            self.test_date_queries()
            self.test_day_queries()
            self.test_event_queries()
            self.test_simple_event_creation()
            self.test_day_of_week_event_creation()
            self.test_event_creation_follow_ups()
            self.test_llm_fallback()
            self.test_edge_cases()
            self.test_complex_queries()
            self.test_mixed_conversation()
            
            self.print_summary()
            
        except Exception as e:
            print(f"❌ Test suite failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*20} TEST SUMMARY {'='*20}")
        
        # Count by section
        sections = {}
        types = {}
        
        for result in self.test_results:
            section = result['section']
            test_type = result['type']
            
            sections[section] = sections.get(section, 0) + 1
            types[test_type] = types.get(test_type, 0) + 1
        
        print(f"Total tests run: {len(self.test_results)}")
        print(f"Test sections: {len(sections)}")
        print(f"Test types: {len(types)}")
        
        print("\n📊 Tests by Section:")
        for section, count in sections.items():
            print(f"  {section}: {count} tests")
        
        print("\n📊 Tests by Type:")
        for test_type, count in types.items():
            print(f"  {test_type}: {count} tests")
        
        print(f"\n✅ Comprehensive test suite completed!")

if __name__ == "__main__":
    test_suite = ComprehensiveSAMTest()
    test_suite.run_all_tests() 