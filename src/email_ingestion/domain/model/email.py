class Email:
    def __init__(self, subject, sender, content, attachments=None):
        self.subject = subject
        self.sender = sender
        self.content = content
        self.attachments = attachments or []