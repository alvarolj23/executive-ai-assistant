"""Script to run langgraph with proper environment loading."""
import os
import sys
from dotenv import load_dotenv
import subprocess

def main():
    # Load environment variables from .env
    load_dotenv()
    
    # Get the port from environment variable (Azure Web Apps uses WEBSITES_PORT)
    # or command line args, or default to 8081 for Azure
    port = os.environ.get("WEBSITES_PORT", "8081")
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = sys.argv[1]
    
    # Run langgraph with the loaded environment, binding to all interfaces
    cmd = ["langgraph", "dev", "--port", port, "--host", "0.0.0.0"]
    subprocess.run(cmd, env=os.environ)

if __name__ == "__main__":
    main() 