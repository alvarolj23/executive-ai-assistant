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
    client = get_client(url=langgraph_url)
    
    # Fetch and process emails
    for email_data in fetch_group_emails(
        email,
        minutes_since=minutes_since,
        gmail_token=gmail_token,
        gmail_secret=gmail_secret,
    ):
        thread_id = str(
            uuid.UUID(hex=hashlib.md5(email_data["thread_id"].encode("UTF-8")).hexdigest())
        )
        
        try:
            thread_info = await client.threads.get(thread_id)
        except httpx.HTTPStatusError as e:
            if "user_respond" in email_data:
                continue
            if e.response.status_code == 404:
                thread_info = await client.threads.create(thread_id=thread_id)
            else:
                raise e

        if "user_respond" in email_data:
            await client.threads.update_state(thread_id, None, as_node="__end__")
            continue

        recent_email = thread_info["metadata"].get("email_id")
        if recent_email == email_data["id"]:
            continue

        await client.threads.update(thread_id, metadata={"email_id": email_data["id"]})
        
        # Create new run for processing the email
        await client.runs.create(
            thread_id,
            "main",
            input={"email": email_data},
            multitask_strategy="rollback",
        )

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

        if not all([langgraph_url, email_address, gmail_token, gmail_secret]):
            raise ValueError("Missing required environment variables")

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
        logging.error('Error processing emails: %s', str(e))
        raise 