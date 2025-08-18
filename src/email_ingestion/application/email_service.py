from ..domain.model.email import Email
from ..domain.repository.email_repository import EmailRepository

class EmailAppService:
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository

    def fetch_and_save_emails(self):
        # This is a placeholder. The actual email fetching logic will be in the pop3_adapter.
        # The adapter will call this service to save the emails.
        pass

    def save_email(self, email: Email):
        self.email_repository.save(email)