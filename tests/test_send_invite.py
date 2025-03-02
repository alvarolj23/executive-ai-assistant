"""
Simple test script for sending calendar invites.

This script allows manual testing of the calendar invite functionality.
You can run it directly to send a test invite and view it in your calendar.
"""

import logging
import sys
from datetime import datetime, timedelta
import argparse
from pathlib import Path
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the calendar function
from eaia.gmail import send_calendar_invite, get_events_for_days, get_calendar_id

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test Google Calendar invite functionality')
    
    parser.add_argument(
        '--email',
        type=str,
        default=os.environ.get('TEST_EMAIL'),
        help='Your email address (will be used as the organizer)'
    )
    
    parser.add_argument(
        '--participants',
        type=str,
        default='',
        help='Comma-separated list of participant emails'
    )
    
    parser.add_argument(
        '--title',
        type=str,
        default=f'Test Calendar Event {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        help='Title of the calendar event'
    )
    
    parser.add_argument(
        '--start-offset',
        type=int,
        default=30,
        help='Minutes from now to schedule the event start (default: 30)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=30,
        help='Duration of the event in minutes (default: 30)'
    )
    
    parser.add_argument(
        '--timezone',
        type=str,
        default='America/Los_Angeles',
        help='Timezone for the event (default: America/Los_Angeles)'
    )
    
    parser.add_argument(
        '--calendar',
        type=str,
        default='primary',
        help='Name of the calendar to use (default: primary)'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify the event was added to the calendar after sending'
    )
    
    return parser.parse_args()

def get_calendar_events(date_str, calendar_name="primary"):
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

def main():
    """Run the calendar invite test."""
    args = parse_args()
    
    # Validate email
    if not args.email:
        logger.error("Email is required. Set TEST_EMAIL environment variable or use --email")
        return 1
        
    # Parse participants
    participants = []
    if args.participants:
        participants = [email.strip() for email in args.participants.split(',')]
    
    # Always include self as a participant
    participants.append(args.email)
    
    # Calculate start and end times
    now = datetime.now()
    start_time = (now + timedelta(minutes=args.start_offset)).isoformat()
    end_time = (now + timedelta(minutes=args.start_offset + args.duration)).isoformat()
    
    logger.info(f"Creating calendar invite with the following details:")
    logger.info(f"Title: {args.title}")
    logger.info(f"Start time: {start_time}")
    logger.info(f"End time: {end_time}")
    logger.info(f"Timezone: {args.timezone}")
    logger.info(f"Organizer: {args.email}")
    logger.info(f"Participants: {participants}")
    logger.info(f"Calendar: {args.calendar}")
    
    # Send the calendar invite
    result = send_calendar_invite(
        emails=participants,
        title=args.title,
        start_time=start_time,
        end_time=end_time,
        email_address=args.email,
        timezone=args.timezone,
        calendar_name=args.calendar
    )
    
    if result:
        logger.info("✅ Calendar invite sent successfully!")
        
        # Verify if requested
        if args.verify:
            # Wait a moment for the event to propagate
            logger.info("Waiting 5 seconds for the event to propagate...")
            import time
            time.sleep(5)
            
            # Get the event date for verification
            event_date = datetime.fromisoformat(start_time).strftime("%d-%m-%Y")
            
            # Get events for the day using our helper function
            events_string = get_calendar_events(event_date, args.calendar)
            
            logger.info(f"Events for {event_date}:")
            logger.info(events_string)
            
            if args.title in events_string:
                logger.info("✅ Event verified in calendar!")
            else:
                logger.warning("⚠️ Event not found in calendar. It may take some time to appear.")
    else:
        logger.error("❌ Failed to send calendar invite")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 