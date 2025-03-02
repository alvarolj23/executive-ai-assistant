"""Test script to verify Google Calendar invite functionality."""

import logging
import unittest
from datetime import datetime, timedelta
import pytz
from typing import List
import os
from pathlib import Path

# Local imports
from eaia.gmail import send_calendar_invite, get_events_for_days, get_calendar_id

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestCalendarInvite(unittest.TestCase):
    """Test case for calendar invite functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Email to use for testing - adjust this to your email
        self.test_email = os.environ.get("TEST_EMAIL", "your_test_email@example.com")
        
        # Test participants (add test email addresses you control)
        self.test_participants = [
            self.test_email,  # Include self as a participant
            os.environ.get("PARTICIPANT_EMAIL_1", "participant1@example.com")
        ]
        
        # Calendar name - uses primary by default
        self.calendar_name = os.environ.get("TEST_CALENDAR_NAME", "primary")
        
        # Setup test event times (30 minutes from now)
        now = datetime.now()
        self.start_time = (now + timedelta(minutes=30)).isoformat()
        self.end_time = (now + timedelta(minutes=60)).isoformat()
        
        # Test timezone - adjust to your local timezone
        self.timezone = os.environ.get("TEST_TIMEZONE", "America/Los_Angeles")
    
    def get_calendar_events(self, date_str, calendar_name="primary"):
        """
        Get calendar events for a specific date using the get_events_for_days LangChain tool.
        
        Args:
            date_str: Date string in dd-mm-yyyy format
            calendar_name: Name of the calendar to check
            
        Returns:
            String containing the events for the day
        """
        # Properly invoke the LangChain tool with the correct input format
        input_data = {"date_strs": [date_str]}
        
        # For LangChain tools, we need to use the invoke method
        try:
            # First try the new invoke method (LangChain ≥ 0.1.47)
            if hasattr(get_events_for_days, 'invoke'):
                return get_events_for_days.invoke(input_data)
            # Fall back to direct call for older LangChain versions
            else:
                return get_events_for_days(input_data)
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            # Try a direct approach by accessing the underlying function
            if hasattr(get_events_for_days, '_run'):
                return get_events_for_days._run(date_strs=[date_str], calendar_name=calendar_name)
            else:
                raise
    
    def test_send_calendar_invite(self):
        """Test sending a calendar invite and verify it appears in the calendar."""
        # Generate a unique test event title with timestamp
        test_title = f"Test Calendar Invite {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        logger.info(f"Creating test calendar invite: {test_title}")
        logger.info(f"Start time: {self.start_time}")
        logger.info(f"End time: {self.end_time}")
        logger.info(f"Participants: {self.test_participants}")
        
        # Send the calendar invite
        result = send_calendar_invite(
            emails=self.test_participants,
            title=test_title,
            start_time=self.start_time,
            end_time=self.end_time,
            email_address=self.test_email,
            timezone=self.timezone,
            calendar_name=self.calendar_name
        )
        
        # Verify the invite was sent successfully
        self.assertTrue(result, "Failed to send calendar invite")
        logger.info("Calendar invite sent successfully")
        
        # Get the event date for verification
        event_date = datetime.fromisoformat(self.start_time).strftime("%d-%m-%Y")
        
        # Verify the event exists in the calendar
        self.verify_event_in_calendar(event_date, test_title)
        
        logger.info(f"Test completed successfully: {test_title}")
    
    def verify_event_in_calendar(self, event_date: str, event_title: str):
        """
        Verify that an event exists in the calendar.
        
        Args:
            event_date: Date of the event in dd-mm-yyyy format
            event_title: Title of the event to search for
        """
        # Use our helper method to get events
        events_string = self.get_calendar_events(
            date_str=event_date,
            calendar_name=self.calendar_name
        )
        
        logger.info(f"Found events for {event_date}:\n{events_string}")
        
        # Check if the event title appears in the events string
        self.assertIn(
            event_title, 
            events_string, 
            f"Event '{event_title}' not found in calendar for date {event_date}"
        )

def run_tests():
    """Run the tests."""
    unittest.main()

if __name__ == "__main__":
    run_tests() 