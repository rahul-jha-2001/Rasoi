import os
import sys
import django
from pathlib import Path
import logging

# Add the project root directory to Python path
# project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(project_root)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

# Ensure logs directory exists
# logs_dir = Path(project_root) / 'logs'
# logs_dir.mkdir(exist_ok=True)

from utils.logger import Logger

def test_logger():
    print("Testing logger...")
    print(f"Logs will be written to: {Path('logs')}")
    
    # Force logger to handle logs immediately
    logging.getLogger('notifications').handlers[0].flush()
    
    # Test different logging levels with more obvious messages
    Logger.info("INFO TEST: This is a test info message")
    Logger.error("ERROR TEST: This is a test error", error=ValueError("Test error"))
    Logger.debug("DEBUG TEST: This is a test debug message")
    
    # Force flush any buffered logs
    for handler in logging.getLogger('notifications').handlers:
        handler.flush()
    
    # Verify log file
    log_file = Path('logs') / 'notifications.log'
    if log_file.exists():
        print(f"\nLog file created at: {log_file}")
        print("\nLog contents:")
        with open(log_file, 'r') as f:
            print(f.read())
    else:
        print("Warning: Log file was not created!")

if __name__ == "__main__":
    test_logger()