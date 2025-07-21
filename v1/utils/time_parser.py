#!/usr/bin/env python3
"""
Centralized Time Parser using parsedatetime
Handles all date/time parsing across the SAM system
"""

import parsedatetime as pdt
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import re

# Module-level Calendar instance
_CAL = pdt.Calendar()

def parse_datetime(text: str, base: datetime = None) -> datetime:
    """
    Parse a fuzzy date/time string into a datetime.
    - text: the raw user phrase, e.g. "tonight at 8pm".
    - base: reference 'now' (defaults to datetime.now()).
    Returns a naive datetime (no tzinfo) representing the parsed moment.
    """
    if base is None:
        base = datetime.now()
    dt, status = _CAL.parseDT(text, base)
    return dt

def parse_time_range(text: str, base: datetime = None) -> Tuple[datetime, datetime]:
    """
    Parse a time range from text.
    Returns (start_time, end_time) tuple.
    """
    if base is None:
        base = datetime.now()
    
    # Parse the main datetime
    start_time = parse_datetime(text, base)
    
    # Default duration is 1 hour
    end_time = start_time + timedelta(hours=1)
    
    # Look for duration indicators
    duration_patterns = [
        (r'(\d+)\s*hours?', lambda x: timedelta(hours=int(x))),
        (r'(\d+)\s*minutes?', lambda x: timedelta(minutes=int(x))),
        (r'(\d+)\s*days?', lambda x: timedelta(days=int(x))),
        (r'(\d+)\s*weeks?', lambda x: timedelta(weeks=int(x))),
    ]
    
    for pattern, duration_func in duration_patterns:
        match = re.search(pattern, text.lower())
        if match:
            duration = duration_func(match.group(1))
            end_time = start_time + duration
            break
    
    return start_time, end_time

def extract_date_filter(text: str) -> Optional[str]:
    """
    Extract date filter from text for event queries.
    Returns: 'today', 'tomorrow', 'next_week', etc.
    """
    text_lower = text.lower()
    
    # Simple date filters
    if 'today' in text_lower:
        return 'today'
    elif 'tomorrow' in text_lower or 'tomororw' in text_lower:  # Handle typo
        return 'tomorrow'
    elif 'tonight' in text_lower:
        return 'tonight'
    elif 'next week' in text_lower:
        return 'next_week'
    elif 'this week' in text_lower:
        return 'this_week'
    elif 'next month' in text_lower:
        return 'next_month'
    
    # Day of week patterns
    day_pattern = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text_lower)
    if day_pattern:
        return f"next_{day_pattern.group(1)}"
    
    return None

def get_next_day_of_week(day_name: str, base: datetime = None) -> datetime:
    """
    Get the next occurrence of a specific day of the week.
    If today is the specified day, returns next week's occurrence.
    """
    if base is None:
        base = datetime.now()
    
    # Day name to number mapping (Monday=0, Sunday=6)
    day_mapping = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3, 'thurs': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }
    
    day_name_lower = day_name.lower()
    if day_name_lower not in day_mapping:
        return base  # Fallback to current time
    
    target_day = day_mapping[day_name_lower]
    current_day = base.weekday()
    
    # Calculate days to add
    if target_day > current_day:
        # Target day is later this week
        days_to_add = target_day - current_day
    elif target_day == current_day:
        # Target day is today, so get next week's occurrence
        days_to_add = 7
    else:
        # Target day is earlier this week, so get next week's occurrence
        days_to_add = 7 - current_day + target_day
    
    return base + timedelta(days=days_to_add)

def normalize_time_format(time_str: str) -> str:
    """
    Normalize time format to ensure proper AM/PM interpretation.
    If no AM/PM is specified, assume PM for times that could be ambiguous.
    """
    time_str = time_str.strip().lower()
    
    # If AM/PM is already specified, return as is
    if 'am' in time_str or 'pm' in time_str:
        return time_str
    
    # Parse the time
    time_match = re.match(r'(\d{1,2})(?::(\d{2}))?', time_str)
    if not time_match:
        return time_str
    
    hour = int(time_match.group(1))
    minute = time_match.group(2) if time_match.group(2) else '00'
    
    # If hour is 12 or less, assume PM (more common for scheduling)
    # If hour is 0, it's midnight (12 AM)
    if hour == 0:
        return f"12:{minute} am"
    elif hour <= 12:
        return f"{hour}:{minute} pm"
    else:
        return f"{hour}:{minute}"

def extract_time_info(text: str) -> Optional[str]:
    """
    Extract time information from text for event creation.
    Returns a string that can be parsed by parse_datetime.
    """
    text_lower = text.lower()
    
    # Pattern for "time on day" (e.g., "4 pm on monday", "3:30 on tuesday")
    day_time_pattern = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)', text_lower)
    if day_time_pattern:
        time_part = day_time_pattern.group(1)
        day_part = day_time_pattern.group(2)
        
        # Normalize time format
        normalized_time = normalize_time_format(time_part)
        
        # Get the next occurrence of that day
        next_day = get_next_day_of_week(day_part)
        
        # Format the date and time
        date_str = next_day.strftime('%Y-%m-%d')
        return f"{date_str} {normalized_time}"
    
    # Pattern for "day at time" (e.g., "monday at 4 pm", "tuesday at 3:30")
    time_day_pattern = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', text_lower)
    if time_day_pattern:
        day_part = time_day_pattern.group(1)
        time_part = time_day_pattern.group(2)
        
        # Normalize time format
        normalized_time = normalize_time_format(time_part)
        
        # Get the next occurrence of that day
        next_day = get_next_day_of_week(day_part)
        
        # Format the date and time
        date_str = next_day.strftime('%Y-%m-%d')
        return f"{date_str} {normalized_time}"
    
    # Common time patterns (existing logic)
    time_patterns = [
        r'(today|tomorrow|tonight)\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
        r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(today|tomorrow|tonight)',
        r'(next\s+\w+)\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',
        r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)',  # Just time
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                date_part, time_part = match.groups()
                normalized_time = normalize_time_format(time_part)
                return f"{date_part} {normalized_time}".strip()
            else:
                # Just time, assume today
                time_part = match.group(1)
                normalized_time = normalize_time_format(time_part)
                return f"today {normalized_time}".strip()
    
    return None

def format_datetime(dt: datetime, format_type: str = 'default') -> str:
    """
    Format datetime for display.
    """
    if format_type == 'time_only':
        return dt.strftime('%I:%M %p')
    elif format_type == 'date_only':
        return dt.strftime('%B %d, %Y')
    elif format_type == 'day_only':
        return dt.strftime('%A')
    elif format_type == 'event_display':
        return dt.strftime('%B %d at %I:%M %p')
    else:  # default
        return dt.strftime('%B %d, %Y at %I:%M %p')

def get_date_range(filter_type: str, base: datetime = None) -> Tuple[datetime, datetime]:
    """
    Get date range for event filtering.
    """
    if base is None:
        base = datetime.now()
    
    if filter_type == 'today':
        start = datetime.combine(base.date(), datetime.min.time())
        end = datetime.combine(base.date(), datetime.max.time())
    elif filter_type == 'tomorrow':
        tomorrow = base.date() + timedelta(days=1)
        start = datetime.combine(tomorrow, datetime.min.time())
        end = datetime.combine(tomorrow, datetime.max.time())
    elif filter_type == 'tonight':
        start = base
        end = datetime.combine(base.date(), datetime.max.time())
    elif filter_type == 'remaining_today':
        start = base
        end = datetime.combine(base.date(), datetime.max.time())
    elif filter_type == 'upcoming':
        start = base
        end = base + timedelta(days=30)
    else:
        # Default to upcoming
        start = base
        end = base + timedelta(days=30)
    
    return start, end

def test_parse_datetime():
    """
    Smoke-test parse_datetime() against a fixed baseline.
    """
    NOW = datetime(2025, 7, 18, 12, 0, 0)
    examples = [
        # simple
        ("tonight",               "2025-07-18T21:00:00"),
        ("tonight at 8pm",        "2025-07-18T20:00:00"),
        ("tomorrow at 9:00 AM",   "2025-07-19T09:00:00"),
        ("this friday at 7 pm",   "2025-07-18T19:00:00"),
        ("next monday at noon",   "2025-07-21T12:00:00"),
        ("in 2 days at 14:30",    "2025-07-20T14:30:00"),
        ("today at 6",            "2025-07-18T18:00:00"),  # 18:00 is 6 PM
        # embedded
        ("Let's meet tomorrow at 3pm for coffee", "2025-07-19T15:00:00"),
        ("Schedule dinner this Friday at 8",       "2025-07-18T20:00:00"),
        ("In two weeks on Tuesday at 10:00",        "2025-08-01T10:00:00"),
        ("I need a reminder tonight at midnight",   "2025-07-19T00:00:00"),
    ]

    all_pass = True
    for txt, expected_iso in examples:
        dt = parse_datetime(txt, base=NOW)
        result_iso = dt.isoformat(timespec='seconds')
        ok = result_iso == expected_iso
        print(f"{txt!r:45} → {result_iso}  "
              f"{'✔' if ok else '✘ expected '+expected_iso}")
        if not ok:
            all_pass = False

    if all_pass:
        print("\nAll parse_datetime tests passed ✅")
    else:
        print("\nSome tests failed ❌")

if __name__ == "__main__":
    test_parse_datetime() 