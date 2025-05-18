import os
import base64
import logging
import json
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from app.core.config import settings

logger = logging.getLogger(__name__)

# Define the SCOPES - If modifying these, delete token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailService:
    def __init__(self):
        self.service = None
        self.sender = settings.GMAIL_SENDER

    async def initialize(self):
        """
        Initialize Gmail API service with OAuth2 credentials
        """
        try:
            creds = None
            # Check if token.json file exists with stored credentials
            if os.path.exists(settings.GOOGLE_TOKEN_FILE):
                creds = Credentials.from_authorized_user_info(
                    json.load(open(settings.GOOGLE_TOKEN_FILE)), SCOPES)
            else:
                logger.warning(f"token.json not found. {os.path.abspath(settings.GOOGLE_TOKEN_FILE)}")
            
            # If no valid credentials available, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        settings.GOOGLE_CLIENT_SECRET_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(settings.GOOGLE_TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the Gmail API service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Gmail API service: {str(e)}")
            raise

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send an email notification using Gmail API
        
        Args:
            to_email: recipient email address
            subject: email subject
            body: email body content (HTML)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            if not self.service:
                logger.error("Gmail API service not initialized")
                return False
                
            # Create message
            message = MIMEText(body, 'html')
            message['to'] = to_email
            message['from'] = self.sender
            message['subject'] = subject
            
            # Encode message to base64
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create message body
            message_body = {'raw': encoded_message}
            
            # Send message
            sent_message = self.service.users().messages().send(
                userId='me', body=message_body).execute()
            
            logger.info(f"Email sent to {to_email}, Message ID: {sent_message['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

# Create a singleton instance
email_service = EmailService()
