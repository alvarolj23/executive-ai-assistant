"""Test script to verify Google Calendar integration and list upcoming events."""

import logging
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Any
from pathlib import Path
import yaml

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Load configuration from config.yaml."""
    root = Path(__file__).parent.parent.absolute()
    config_path = root / "eaia" / "main" / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def get_calendar_service():
    """Initialize and return the Google Calendar service."""
    try:
        # Get token path
        root = Path(__file__).parent.parent.absolute()
        token_path = root / "eaia" / ".secrets" / "token.json"
        
        if not token_path.exists():
            raise FileNotFoundError(
                f"No token file found at {token_path}. Please run setup_google_auth.py first."
            )
        
        creds = Credentials.from_authorized_user_file(
            str(token_path),
            ["https://www.googleapis.com/auth/calendar"]
        )
        
        return build('calendar', 'v3', credentials=creds)
    
    except Exception as e:
        logger.error(f"Failed to create calendar service: {str(e)}")
        raise

def list_calendars() -> None:
    """List all available calendars and their IDs."""
    try:
        service = get_calendar_service()
        calendar_list = service.calendarList().list().execute()
        
        print("\nAvailable Calendars:")
        print("=" * 50)
        
        for calendar in calendar_list['items']:
            print(f"\nCalendar Name: {calendar['summary']}")
            print(f"Calendar ID: {calendar['id']}")
            print(f"Access Role: {calendar['accessRole']}")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"Failed to list calendars: {str(e)}")
        raise

def get_calendar_id(calendar_name: str) -> str:
    """
    Get the calendar ID for a given calendar name.
    
    Args:
        calendar_name: Display name of the calendar
        
    Returns:
        Calendar ID if found, otherwise returns 'primary'
    """
    try:
        service = get_calendar_service()
        calendar_list = service.calendarList().list().execute()
        
        # First look for exact match
        for calendar in calendar_list['items']:
            if calendar['summary'].lower() == calendar_name.lower():
                logger.info(f"Found calendar: {calendar['summary']} with ID: {calendar['id']}")
                return calendar['id']
        
        # If not found, return primary
        logger.warning(f"Calendar '{calendar_name}' not found, using primary calendar")
        return 'primary'
        
    except Exception as e:
        logger.error(f"Failed to get calendar ID: {str(e)}")
        return 'primary'

def get_upcoming_events(
    days: int = 7,
    max_results: int = 10,
    calendar_id: str = 'primary'
) -> List[Dict[Any, Any]]:
    """
    Retrieve upcoming calendar events.
    
    Args:
        days: Number of days to look ahead
        max_results: Maximum number of events to retrieve
        calendar_id: ID of the calendar to fetch events from
        
    Returns:
        List of calendar events
    """
    try:
        service = get_calendar_service()
        config = load_config()
        
        # Get timezone from config
        timezone = pytz.timezone(config.get('timezone', 'UTC'))
        
        # Calculate time bounds
        now = datetime.now(timezone)
        time_min = now.isoformat()
        time_max = (now + timedelta(days=days)).isoformat()
        
        logger.info(f"Fetching events from {time_min} to {time_max}")
        logger.info(f"Using calendar: {calendar_id}")
        
        # Call the Calendar API
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            logger.info("No upcoming events found.")
            return []
            
        # Process and format events
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'summary': event.get('summary', 'No title'),
                'start': start,
                'end': end,
                'attendees': event.get('attendees', []),
                'location': event.get('location', 'No location'),
                'description': event.get('description', 'No description')
            })
            
        return formatted_events
        
    except HttpError as error:
        logger.error(f"Google Calendar API error: {str(error)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

def print_events(events: List[Dict[Any, Any]]) -> None:
    """Pretty print the events."""
    print("\nUpcoming events:")
    print("=" * 50)
    
    for event in events:
        print(f"\nEvent: {event['summary']}")
        print(f"Start: {event['start']}")
        print(f"End: {event['end']}")
        print(f"Location: {event['location']}")
        
        if event['attendees']:
            print("\nAttendees:")
            for attendee in event['attendees']:
                print(f"- {attendee.get('email')}")
        
        print("-" * 50)

def main():
    """Main function to test calendar integration."""
    try:
        # First, list all available calendars
        print("\nListing all available calendars:")
        list_calendars()
        
        # Then proceed with event fetching
        config = load_config()
        calendar_name = config.get('calendar_name', 'primary')
        calendar_id = get_calendar_id(calendar_name)
        
        print(f"\nFetching events for calendar: {calendar_name}")
        # Test connection and get events for the next 7 days
        events = get_upcoming_events(
            days=7,
            max_results=10,
            calendar_id=calendar_id
        )
        print_events(events)
        
    except Exception as e:
        logger.error(f"Failed to retrieve calendar events: {str(e)}")
        raise

if __name__ == "__main__":
    main() 