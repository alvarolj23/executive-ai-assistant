from pathlib import Path
import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the scopes required for Gmail and Calendar access
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

def setup_credentials():
    """
    Set up Google API credentials using OAuth flow.
    
    This function will:
    1. Look for existing token.json file
    2. If not found or invalid, initiate OAuth flow using client secrets
    3. Save the credentials to token.json
    """
    # Get paths
    root = Path(__file__).parent.parent.absolute()
    secrets_dir = root / "eaia" / ".secrets"
    secrets_path = secrets_dir / "secrets.json"
    token_path = secrets_dir / "token.json"
    
    # Ensure secrets directory exists
    if not secrets_dir.exists():
        logger.info(f"Creating secrets directory at {secrets_dir}")
        secrets_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if secrets.json exists
    if not secrets_path.exists():
        raise FileNotFoundError(
            f"Client secrets file not found at {secrets_path}. "
            "Please download the client secret from Google Cloud Console "
            "and save it to this location."
        )
    
    creds = None
    # Check if token file exists and is valid
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
            logger.info("Found existing token file.")
        except Exception as e:
            logger.warning(f"Error loading existing token: {str(e)}")
            creds = None
    
    # If no valid credentials available, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Error refreshing token: {str(e)}")
                creds = None
        
        if not creds:
            logger.info("Starting OAuth flow to generate new token...")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(secrets_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Error during OAuth flow: {str(e)}")
                raise
        
        # Save the credentials for future use
        with open(token_path, "w") as token:
            token.write(creds.to_json())
            logger.info(f"Token successfully saved to {token_path}")
    
    return creds

if __name__ == "__main__":
    try:
        logger.info("Setting up Gmail credentials...")
        creds = setup_credentials()
        logger.info("Gmail credentials setup completed successfully!")
    except Exception as e:
        logger.error(f"Error setting up Gmail credentials: {str(e)}")
        raise
