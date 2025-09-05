#!/usr/bin/env python3
"""
Google Calendar Integration for SAM
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from ..utils.config import CRED_PATH, TOKEN_PATH, SCOPES, TIMEZONE

@dataclass
class CalendarEvent:
    """Represents a Google Calendar event"""
    id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

class GoogleCalendarService:
    """Google Calendar service integration"""
    
    def __init__(self):
        self.service = None
        self.calendar_id = 'primary'
        # Use paths from configuration
        self.token_path = TOKEN_PATH
        self.creds_path = CRED_PATH
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        if not GOOGLE_AVAILABLE:
            print("Google Calendar API not available")
            return
        
        creds = None
        token_path = self.token_path
        creds_path = self.creds_path
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(creds_path):
                    print(f"Error: {creds_path} not found. Please set up Google Calendar credentials.")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            print("✅ Google Calendar authentication successful")
        except Exception as e:
            print(f"❌ Google Calendar authentication failed: {e}")
    
    def get_events(self, filters: Dict[str, Any] = None) -> List[CalendarEvent]:
        """Get events from Google Calendar with optional filters"""
        if not self.service:
            print("Google Calendar service not available")
            return []
        
        try:
            # Build time range using centralized parser
            from v4.utils.time_parser import get_date_range
            
            # Use local time for date calculations, not UTC
            now = datetime.now()
            
            # Apply filters
            if filters:
                if filters.get('date') == 'today':
                    start, end = get_date_range('today', now)
                elif filters.get('date') == 'tomorrow':
                    start, end = get_date_range('tomorrow', now)
                elif filters.get('remaining_today', False) or filters.get('next_single', False):
                    # Both "next event" and "upcoming events" should use remaining_today logic
                    start, end = get_date_range('remaining_today', now)
                elif filters.get('upcoming_only', False):
                    start, end = get_date_range('upcoming', now)
                else:
                    start, end = get_date_range('upcoming', now)
            else:
                # Default: upcoming events
                start, end = get_date_range('upcoming', now)
            
            # Use Los Angeles timezone for Google Calendar API
            try:
                import pytz
                # Set timezone to Los Angeles
                la_tz = pytz.timezone(TIMEZONE)
                
                # Make local time timezone-aware in Los Angeles timezone
                start_la = la_tz.localize(start)
                end_la = la_tz.localize(end)
                
                time_min = start_la.isoformat()
                time_max = end_la.isoformat()
            except ImportError:
                # Fallback to standard library if pytz is not available
                from datetime import timezone
                # Use PDT/PST offset for Los Angeles (UTC-8 or UTC-7)
                # For simplicity, we'll use UTC-8 (PST)
                la_offset = timezone(timedelta(hours=-8))
                
                start_la = start.replace(tzinfo=la_offset)
                end_la = end.replace(tzinfo=la_offset)
                
                time_min = start_la.isoformat()
                time_max = end_la.isoformat()
            
            # Get events from Google Calendar
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convert to CalendarEvent objects
            calendar_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Parse datetime with proper timezone handling
                if 'T' in start:  # Has time
                    # Parse the datetime string
                    start_dt = datetime.fromisoformat(start)
                    
                    # If it's timezone-aware, convert to Los Angeles timezone
                    if start_dt.tzinfo is not None:
                        try:
                            la_tz = pytz.timezone(TIMEZONE)
                            start_dt = start_dt.astimezone(la_tz)
                        except ImportError:
                            # Fallback to standard library
                            from datetime import timezone
                            la_offset = timezone(timedelta(hours=-8))
                            start_dt = start_dt.astimezone(la_offset)
                    
                    # Convert to naive datetime in Los Angeles time
                    start_dt = start_dt.replace(tzinfo=None)
                else:  # All-day event
                    start_dt = datetime.fromisoformat(start)
                
                if end and 'T' in end:
                    # Parse end time with proper timezone handling
                    end_dt = datetime.fromisoformat(end)
                    
                    # If it's timezone-aware, convert to Los Angeles timezone
                    if end_dt.tzinfo is not None:
                        try:
                            la_tz = pytz.timezone(TIMEZONE)
                            end_dt = end_dt.astimezone(la_tz)
                        except ImportError:
                            # Fallback to standard library
                            from datetime import timezone
                            la_offset = timezone(timedelta(hours=-8))
                            end_dt = end_dt.astimezone(la_offset)
                    
                    # Convert to naive datetime in Los Angeles time
                    end_dt = end_dt.replace(tzinfo=None)
                elif end:
                    end_dt = datetime.fromisoformat(end)
                else:
                    end_dt = None
                
                calendar_event = CalendarEvent(
                    id=event['id'],
                    title=event['summary'],
                    start_time=start_dt,
                    end_time=end_dt,
                    description=event.get('description'),
                    location=event.get('location')
                )
                calendar_events.append(calendar_event)
            
            # Apply additional filters
            if filters:
                # Filter for future events (for next event, upcoming events, etc.)
                if filters.get('upcoming_only', False) or filters.get('next_single', False) or filters.get('remaining_today', False):
                    # Use the same 'now' value that was used for date range calculation
                    # Filter out events that have already started
                    calendar_events = [e for e in calendar_events if e.start_time > now]
                # Filter by specific date if requested
                if filters.get('date') == 'today':
                    today = datetime.now().date()
                    calendar_events = [e for e in calendar_events if e.start_time.date() == today]
                elif filters.get('date') == 'tomorrow':
                    tomorrow = (datetime.now() + timedelta(days=1)).date()
                    calendar_events = [e for e in calendar_events if e.start_time.date() == tomorrow]
                # Apply limit after filtering
                if filters.get('limit'):
                    calendar_events = calendar_events[:filters['limit']]
            
            return calendar_events
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def create_event(self, title: str, start_time: str, description: str = None, location: str = None) -> bool:
        """Create a new event in Google Calendar"""
        if not self.service:
            print("Google Calendar service not available")
            return False
        
        try:
            # Parse the start time
            start_dt = self._parse_time_string(start_time)
            end_dt = start_dt + timedelta(hours=1)  # Default 1 hour duration
            
            event = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': TIMEZONE,
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': TIMEZONE,
                },
            }
            
            event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            print(f"✅ Event created: {event.get('htmlLink')}")
            return True
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def _parse_time_string(self, time_str: str) -> datetime:
        """Parse time string into datetime object using centralized parser"""
        from v4.utils.time_parser import parse_datetime
        return parse_datetime(time_str)
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event from Google Calendar"""
        if not self.service:
            print("Google Calendar service not available")
            return False
        
        try:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
            print("✅ Event deleted successfully")
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False 