import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.email.email_receiver import EmailReceiver
from src.email.config import EMAIL_CONFIG

def run_service(interval=60):
    """
    Runs the email receiving service at a specified interval.

    Args:
        interval (int): The interval in seconds between checking for new emails.
    """
    receiver = EmailReceiver(EMAIL_CONFIG)

    while True:
        print(f"Checking for new emails at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        if receiver.connect():
            receiver.fetch_emails()
            receiver.disconnect()
        
        print(f"Waiting for {interval} seconds before next check...")
        time.sleep(interval)

if __name__ == '__main__':
    # Run the service to check for emails every 5 minutes
    run_service(interval=300)