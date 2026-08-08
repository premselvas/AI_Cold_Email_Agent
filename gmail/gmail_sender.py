from gmail.gmail_send import send_message

class GmailSender:
    """Class wrapper for sending emails via Gmail API."""

    def send_email(self, to, subject, body, cc=None, bcc=None, attachments=None) -> bool:
        """Send email with attachments."""
        try:
            send_message(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc,
                attachments=attachments
            )
            return True
        except Exception as e:
            print(f"GmailSender error: {e}")
            raise e
