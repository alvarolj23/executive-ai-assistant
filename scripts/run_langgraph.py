"""Script to run langgraph with proper environment loading."""
import os
import sys
from dotenv import load_dotenv
import subprocess

def main():
    # Load environment variables from .env
    load_dotenv()
    
    # Get the port from command line args or use default
    port = "2024"
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = sys.argv[1]
    
    # Run langgraph with the loaded environment
    cmd = ["langgraph", "dev", "--port", port]
    subprocess.run(cmd, env=os.environ)

if __name__ == "__main__":
    main() 