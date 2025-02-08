import azure.functions as func
import logging
import asyncio
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from langgraph_sdk import get_client
from eaia.gmail import fetch_group_emails
import httpx
import uuid
import hashlib

# Load environment variables
load_dotenv()

async def process_emails(
    langgraph_url: str,
    minutes_since: int = 60,
    gmail_token: Optional[str] = None,
    gmail_secret: Optional[str] = None,
    email: Optional[str] = None,
) -> None:
    """Process emails from Gmail and send them to LangGraph server."""
    logging.info(f"Starting email processing with LangGraph URL: {langgraph_url}")
    logging.info(f"Looking for emails in the last {minutes_since} minutes for {email}")
    
    client = get_client(url=langgraph_url)
    logging.info("LangGraph client initialized")
    
    try:
        email_count = 0
        for email_data in fetch_group_emails(
            email,
            minutes_since=minutes_since,
            gmail_token=gmail_token,
            gmail_secret=gmail_secret,
        ):
            email_count += 1
            logging.info(f"Processing email {email_count} with ID: {email_data.get('id')} from thread: {email_data.get('thread_id')}")
            
            thread_id = str(
                uuid.UUID(hex=hashlib.md5(email_data["thread_id"].encode("UTF-8")).hexdigest())
            )
            
            try:
                thread_info = await client.threads.get(thread_id)
                logging.info(f"Retrieved existing thread info for {thread_id}")
            except httpx.HTTPStatusError as e:
                if "user_respond" in email_data:
                    logging.info(f"Skipping user response in thread {thread_id}")
                    continue
                if e.response.status_code == 404:
                    logging.info(f"Creating new thread for {thread_id}")
                    thread_info = await client.threads.create(thread_id=thread_id)
                else:
                    logging.error(f"HTTP error while getting thread {thread_id}: {str(e)}")
                    raise e

            if "user_respond" in email_data:
                logging.info(f"Marking thread {thread_id} as ended due to user response")
                await client.threads.update_state(thread_id, None, as_node="__end__")
                continue

            recent_email = thread_info["metadata"].get("email_id")
            if recent_email == email_data["id"]:
                logging.info(f"Skipping already processed email {email_data['id']}")
                continue

            logging.info(f"Updating thread {thread_id} with new email {email_data['id']}")
            await client.threads.update(thread_id, metadata={"email_id": email_data["id"]})
            
            logging.info(f"Creating new run for email {email_data['id']} in thread {thread_id}")
            await client.runs.create(
                thread_id,
                "main",
                input={"email": email_data},
                multitask_strategy="rollback",
            )
        
        logging.info(f"Completed processing {email_count} emails")
    except Exception as e:
        logging.error(f"Error in process_emails: {str(e)}", exc_info=True)
        raise

async def main(mytimer: func.TimerRequest) -> None:
    """Azure Function main entry point."""
    utc_timestamp = datetime.utcnow().replace(tzinfo=None).isoformat()
    logging.info('Email ingestion timer trigger function started at %s', utc_timestamp)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    try:
        # Get configuration from environment variables
        langgraph_url = os.getenv('LANGGRAPH_URL')
        email_address = os.getenv('EMAIL_ADDRESS')
        gmail_token = os.getenv('GMAIL_TOKEN')
        gmail_secret = os.getenv('GMAIL_SECRET')
        minutes_since = int(os.getenv('MINUTES_SINCE', '60'))

        # Log configuration (excluding sensitive data)
        logging.info(f"Configuration: LANGGRAPH_URL={langgraph_url}, EMAIL_ADDRESS={email_address}, MINUTES_SINCE={minutes_since}")
        logging.info("Gmail credentials are present" if gmail_token and gmail_secret else "Gmail credentials are missing")

        if not all([langgraph_url, email_address, gmail_token, gmail_secret]):
            missing = [
                var for var, val in {
                    'LANGGRAPH_URL': langgraph_url,
                    'EMAIL_ADDRESS': email_address,
                    'GMAIL_TOKEN': bool(gmail_token),
                    'GMAIL_SECRET': bool(gmail_secret)
                }.items() if not val
            ]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # Process emails
        await process_emails(
            langgraph_url=langgraph_url,
            minutes_since=minutes_since,
            gmail_token=gmail_token,
            gmail_secret=gmail_secret,
            email=email_address
        )

        logging.info('Email ingestion completed successfully at %s', utc_timestamp)
    except Exception as e:
        logging.error('Error processing emails: %s', str(e), exc_info=True)
        raise 