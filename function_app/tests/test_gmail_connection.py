import os
import json
import logging
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gmail_connection():
    # Get credentials from environment variables
    gmail_token = os.getenv('GMAIL_TOKEN')
    if not gmail_token:
        raise ValueError("GMAIL_TOKEN environment variable is not set")
    
    try:
        # Parse the token JSON
        logger.info("Parsing Gmail token...")
        token_info = json.loads(gmail_token)
        logger.info("Token structure: %s", json.dumps({k: '...' for k in token_info.keys()}, indent=2))
        
        # Create credentials object
        logger.info("Creating credentials object...")
        creds = Credentials(
            token=token_info["token"],
            refresh_token=token_info["refresh_token"],
            token_uri=token_info["token_uri"],
            client_id=token_info["client_id"],
            client_secret=token_info["client_secret"],
            scopes=token_info["scopes"]
        )
        
        # Initialize Gmail API service
        logger.info("Initializing Gmail service...")
        service = build('gmail', 'v1', credentials=creds)
        
        # Try to list recent emails
        logger.info("Attempting to list recent emails...")
        after_time = int((datetime.now() - timedelta(minutes=60)).timestamp())
        results = service.users().messages().list(
            userId='me',
            q=f'after:{after_time}'
        ).execute()
        
        messages = results.get('messages', [])
        logger.info(f"Successfully retrieved {len(messages)} messages")
        
        # Try to get details of the first message if any exist
        if messages:
            first_msg = service.users().messages().get(
                userId='me',
                id=messages[0]['id']
            ).execute()
            logger.info("Successfully retrieved details of first message")
            
            # Print some basic info about the first message
            headers = first_msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No subject')
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown sender')
            logger.info(f"Sample email - Subject: {subject}, From: {from_email}")
        
        return True
        
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Gmail token JSON: %s", str(e))
        logger.error("Token value: %s", gmail_token[:100] + "..." if len(gmail_token) > 100 else gmail_token)
        raise
        
    except Exception as e:
        logger.error("Error testing Gmail connection: %s", str(e), exc_info=True)
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting Gmail connection test...")
        success = test_gmail_connection()
        logger.info("Gmail connection test completed successfully!")
    except Exception as e:
        logger.error("Gmail connection test failed!")
        raise 