import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from gmail.gmail_auth import get_gmail_credentials

def send_message(to, subject, body, cc=None, bcc=None, attachments=None):
    """Create and send email message via Gmail API."""
    creds = get_gmail_credentials()
    if not creds:
        raise RuntimeError("Gmail authentication required. Please configure OAuth credentials or authorize access.")

    service = build('gmail', 'v1', credentials=creds)
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc
    if bcc:
        message['bcc'] = bcc

    message.attach(MIMEText(body, 'plain', 'utf-8'))

    if attachments:
        for attachment in attachments:
            try:
                part = MIMEBase('application', 'octet-stream')
                if hasattr(attachment, 'read'):
                    content = attachment.read()
                    filename = getattr(attachment, 'name', 'attachment.pdf')
                    if hasattr(attachment, 'seek'):
                        attachment.seek(0)
                elif isinstance(attachment, str) and os.path.exists(attachment):
                    with open(attachment, 'rb') as f:
                        content = f.read()
                    filename = os.path.basename(attachment)
                else:
                    continue

                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                message.attach(part)
            except Exception as e:
                print(f"Attachment error: {e}")

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent_message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
    return sent_message
