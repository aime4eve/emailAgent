import poplib
import email
from email.header import decode_header
from datetime import datetime
from ..application.email_service import EmailAppService
from ..domain.model.email import Email

class POP3Adapter:
    def __init__(self, config, email_service: EmailAppService):
        self.config = config
        self.email_service = email_service
        self.pop3_server = None

    def connect(self):
        try:
            self.pop3_server = poplib.POP3(self.config['server'])
            self.pop3_server.user(self.config['user'])
            self.pop3_server.pass_(self.config['password'])
            print(f"Successfully connected to {self.config['server']}")
            return True
        except poplib.error_proto as e:
            print(f"Error connecting to POP3 server: {e}")
            return False

    def fetch_emails(self):
        if not self.pop3_server:
            print("Not connected to POP3 server.")
            return

        try:
            num_messages = len(self.pop3_server.list()[1])
            print(f"Found {num_messages} new emails.")

            for i in range(num_messages):
                raw_email = b'\n'.join(self.pop3_server.retr(i + 1)[1])
                msg = email.message_from_bytes(raw_email)
                
                subject = self.decode_header_field(msg["Subject"])
                sender = self.decode_header_field(msg["From"])
                body = self.get_email_body(msg)

                email_entity = Email(subject=subject, sender=sender, content=body)
                self.email_service.save_email(email_entity)


        except poplib.error_proto as e:
            print(f"Error fetching emails: {e}")

    def decode_header_field(self, header_field):
        if header_field is None:
            return ""
        decoded_parts = decode_header(header_field)
        decoded_string = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding if encoding else 'utf-8', errors='ignore')
            else:
                decoded_string += part
        return decoded_string

    def get_email_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" not in content_disposition and "text/plain" in content_type:
                    try:
                        return part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                    except:
                        return ""
        else:
            try:
                return msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
            except:
                return ""
        return ""

    def disconnect(self):
        if self.pop3_server:
            self.pop3_server.quit()
            print("Disconnected from POP3 server.")

            if content_type == "text/plain" and "attachment" not in content_disposition:
                    charset = part.get_content_charset()
                    if charset:
                        return part.get_payload(decode=True).decode(charset, errors='ignore')
                    else:
                        return part.get_payload(decode=True).decode(errors='ignore')
        else:
            charset = msg.get_content_charset()
            if charset:
                return msg.get_payload(decode=True).decode(charset, errors='ignore')
            else:
                return msg.get_payload(decode=True).decode(errors='ignore')
        return ""


    def disconnect(self):
        if self.pop3_server:
            self.pop3_server.quit()
            print("Disconnected from POP3 server.")

if __name__ == '__main__':
    receiver = EmailReceiver(EMAIL_CONFIG)
    if receiver.connect():
        receiver.fetch_emails()
        receiver.disconnect()