import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import Config

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_credentials():
    """Obtain or refresh Google OAuth2 credentials."""
    creds = None
    token_path = os.path.join(Config.DATA_DIR, 'token.json')
    
    # Check for direct refresh token in .env
    if Config.GMAIL_CLIENT_ID and Config.GMAIL_CLIENT_SECRET and Config.GMAIL_REFRESH_TOKEN:
        try:
            creds = Credentials(
                token=Config.GMAIL_ACCESS_TOKEN,
                refresh_token=Config.GMAIL_REFRESH_TOKEN,
                token_uri=Config.GMAIL_TOKEN_URI,
                client_id=Config.GMAIL_CLIENT_ID,
                client_secret=Config.GMAIL_CLIENT_SECRET,
                scopes=SCOPES
            )
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            return creds
        except Exception:
            pass

    # Check token.json
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            cred_file = 'credentials.json' if os.path.exists('credentials.json') else 'credentials.json.json'
            if os.path.exists(cred_file):
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"Gmail Auth Flow notice: {e}")

    return creds
