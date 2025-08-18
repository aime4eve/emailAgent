import unittest
import os
import sys
import poplib
from unittest.mock import patch, MagicMock
from email.message import EmailMessage

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.email_ingestion.infrastructure.pop3_adapter import POP3Adapter
from src.email_ingestion.application.email_service import EmailAppService
from src.email_ingestion.domain.model.email import Email
from src.shared.config import Config

class TestPOP3Adapter(unittest.TestCase):

    def setUp(self):
        """Set up test environment."""
        self.config = Config().get('email')
        self.email_service = MagicMock(spec=EmailAppService)
        self.adapter = POP3Adapter(self.config, self.email_service)

    @patch('src.email_ingestion.infrastructure.pop3_adapter.poplib.POP3')
    def test_connect_success(self, mock_pop3):
        """Test successful connection to POP3 server."""
        mock_instance = mock_pop3.return_value
        mock_instance.user.return_value = b'+OK'
        mock_instance.pass_.return_value = b'+OK'
        
        self.assertTrue(self.adapter.connect())
        mock_pop3.assert_called_with(self.config['server'])
        mock_instance.user.assert_called_with(self.config['user'])
        mock_instance.pass_.assert_called_with(self.config['password'])

    @patch('src.email_ingestion.infrastructure.pop3_adapter.poplib.POP3')
    def test_connect_fail(self, mock_pop3):
        """Test failed connection to POP3 server."""
        mock_pop3.side_effect = poplib.error_proto('Connection failed')
        self.assertFalse(self.adapter.connect())

    @patch('src.email_ingestion.infrastructure.pop3_adapter.poplib.POP3')
    def test_fetch_emails(self, mock_pop3):
        """Test fetching emails and passing them to the email service."""
        # Mock POP3 server and its methods
        mock_server = mock_pop3.return_value
        self.adapter.pop3_server = mock_server

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
        self.adapter.fetch_emails()

        # Verify that the email service was called with the correct email entity
        self.email_service.save_email.assert_called_once()
        saved_email = self.email_service.save_email.call_args[0][0]
        self.assertIsInstance(saved_email, Email)
        self.assertEqual(saved_email.subject, 'Test Subject')
        self.assertEqual(saved_email.sender, 'sender@example.com')
        self.assertEqual(saved_email.content, 'This is the body of the email.\n')

if __name__ == '__main__':
    unittest.main()