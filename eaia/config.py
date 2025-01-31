"""Central configuration for environment variables and settings."""
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI Settings
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o')
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-ada-002')

# LangSmith Settings
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'true').lower() == 'true'
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_ENDPOINT = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'email-calendar-assistant')

# Validate required environment variables
def validate_env():
    required_vars = [
        ('AZURE_OPENAI_API_KEY', AZURE_OPENAI_API_KEY),
        ('AZURE_OPENAI_ENDPOINT', AZURE_OPENAI_ENDPOINT),
    ]
    
    missing = [var_name for var_name, var_value in required_vars if not var_value]
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please ensure these are set in your .env file or environment."
        )

# Call validation on import
validate_env() 