import unittest
import os
import sys
import poplib
from unittest.mock import patch
from email.message import EmailMessage

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.email.email_receiver import EmailReceiver
from src.email.config import EMAIL_CONFIG, SAVE_DIRECTORY

class TestEmailReceiver(unittest.TestCase):

    def setUp(self):
        """Set up test environment."""
        self.config = EMAIL_CONFIG
        self.receiver = EmailReceiver(self.config)
        # Ensure the save directory exists
        if not os.path.exists(SAVE_DIRECTORY):
            os.makedirs(SAVE_DIRECTORY)

    def tearDown(self):
        """Clean up after tests."""
        # Clean up any created files
        for file in os.listdir(SAVE_DIRECTORY):
            os.remove(os.path.join(SAVE_DIRECTORY, file))

    @patch('src.email.email_receiver.poplib.POP3')
    def test_connect_success(self, mock_pop3):
        """Test successful connection to POP3 server."""
        mock_instance = mock_pop3.return_value
        mock_instance.user.return_value = b'+OK'
        mock_instance.pass_.return_value = b'+OK'
        
        self.assertTrue(self.receiver.connect())
        mock_pop3.assert_called_with(self.config['server'])
        mock_instance.user.assert_called_with(self.config['user'])
        mock_instance.pass_.assert_called_with(self.config['password'])

    @patch('src.email.email_receiver.poplib.POP3')
    def test_connect_fail(self, mock_pop3):
        """Test failed connection to POP3 server."""
        mock_pop3.side_effect = poplib.error_proto('Connection failed')
        self.assertFalse(self.receiver.connect())

    @patch('src.email.email_receiver.poplib.POP3')
    def test_fetch_and_save_email(self, mock_pop3):
        """Test fetching and saving a single email."""
        # Mock POP3 server and its methods
        mock_server = mock_pop3.return_value
        self.receiver.pop3_server = mock_server

        # Create a sample email message
        msg = EmailMessage()
        msg['From'] = 'sender@example.com'
        msg['Subject'] = 'Test Subject'
        msg['Date'] = 'Mon, 1 Jan 2024 12:00:00 +0000'
        msg.set_content('This is the body of the email.')
        
        raw_email = msg.as_bytes()
        
        mock_server.list.return_value = (b'+OK', [b'1 123'])
        mock_server.retr.return_value = (b'+OK', raw_email.split(b'\n'), 123)

        # Call the method to test
        self.receiver.fetch_emails()

        # Check if the email was saved correctly
        saved_files = os.listdir(SAVE_DIRECTORY)
        self.assertEqual(len(saved_files), 1)
        self.assertTrue(saved_files[0].startswith('20240101_120000'))
        self.assertIn('senderexamplecom', saved_files[0])
        self.assertIn('Test Subject', saved_files[0])
        self.assertTrue(saved_files[0].endswith('.eml'))

        # Verify the content of the saved file
        with open(os.path.join(SAVE_DIRECTORY, saved_files[0]), 'rb') as f:
            saved_content = f.read()
        self.assertEqual(saved_content, raw_email)

if __name__ == '__main__':
    unittest.main()