"""
Configuration settings for the email receiver service.
"""

import os

# Email server settings for POP3 connection
EMAIL_CONFIG = {
    'server': 'pop.126.com',
    'user': 'wulogic@126.com',
    'password': 'QVpz4kTVC2kTZ4Lh',  # IMPORTANT: Replace with your actual email password or use a secure method to load it.
    'mailbox': 'INBOX',  # Mailbox to fetch emails from
}

# Directory to save incoming emails
# This constructs an absolute path to the 'data/myemails' directory.
SAVE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'myemails'))

# Ensure the save directory exists. If not, create it.
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)