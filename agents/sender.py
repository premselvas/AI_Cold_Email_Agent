class EmailSenderAgent:
    """Agent overseeing email dispatch."""

    def __init__(self, sender_backend=None):
        self.sender_backend = sender_backend

    def send(self, to_email: str, subject: str, body: str, attachments=None):
        """Send an email using configured backend."""
        if self.sender_backend:
            return self.sender_backend.send_email(
                to=to_email,
                subject=subject,
                body=body,
                attachments=attachments
            )
        return False
