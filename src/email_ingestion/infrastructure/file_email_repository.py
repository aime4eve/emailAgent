import os
from ..domain.repository.email_repository import EmailRepository

class FileEmailRepository(EmailRepository):
    def __init__(self, save_path='data/myemails'):
        self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def save(self, email):
        filename = os.path.join(self.save_path, f"{email.subject}.txt")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"From: {email.sender}\n")
            f.write(f"Subject: {email.subject}\n\n")
            f.write(email.content)