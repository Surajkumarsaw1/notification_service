from twilio.rest import Client
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_FROM_NUMBER
        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, to_number: str, body: str) -> bool:
        """
        Send an SMS notification
        
        Args:
            to_number: recipient phone number in E.164 format
            body: message text
            
        Returns:
            bool: True if SMS was sent successfully, False otherwise
        """
        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent to {to_number}, SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return False

# Create a singleton instance
sms_service = SMSService()
