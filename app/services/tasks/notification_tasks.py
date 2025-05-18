import logging
from celery import shared_task
from datetime import datetime
from uuid import UUID

from app.db.database import SessionLocal
from app.db.models import Notification, User, NotificationStatus
from app.services.email_service import email_service
from app.services.sms_service import sms_service
from app.services.in_app_service import in_app_service

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    name="send_email_notification",
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600  # 10 minutes
)
def send_email_notification(self, notification_id: str, user_id: str, subject: str, body: str):
    """
    Task to send email notification
    """
    logger.info(f"Processing email notification {notification_id} for user {user_id}")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get notification and user
        notification = db.query(Notification).filter(
            Notification.id == UUID(notification_id)
        ).first()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found in database")
            return False
        
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        
        if not user:
            logger.error(f"User {user_id} not found in database")
            notification.status = NotificationStatus.FAILED
            db.commit()
            return False
            
        # Update status to sending
        notification.status = NotificationStatus.SENDING
        db.commit()
        
        # Send email
        success = email_service.send_email(user.email, subject, body)
            
        # Update notification status based on result
        if success:
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.utcnow()
            db.commit()
            logger.info(f"Email notification {notification_id} delivered successfully")
            return True
        else:
            # Mark as failed (will be retried by Celery automatically)
            notification.status = NotificationStatus.FAILED
            db.commit()
            logger.warning(f"Email notification {notification_id} failed, will retry")
            raise Exception("Failed to send email")
            
    except Exception as e:
        logger.error(f"Error processing email notification {notification_id}: {str(e)}")
        # Update notification status to failed
        try:
            if notification:
                notification.status = NotificationStatus.FAILED
                db.commit()
        except:
            pass
        
        # Re-raise the exception for Celery to handle retry
        raise
    finally:
        db.close()

@shared_task(
    bind=True,
    name="send_sms_notification",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600
)
def send_sms_notification(self, notification_id: str, user_id: str, body: str):
    """
    Task to send SMS notification
    """
    logger.info(f"Processing SMS notification {notification_id} for user {user_id}")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get notification and user
        notification = db.query(Notification).filter(
            Notification.id == UUID(notification_id)
        ).first()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found in database")
            return False
        
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        
        if not user:
            logger.error(f"User {user_id} not found in database")
            notification.status = NotificationStatus.FAILED
            db.commit()
            return False
            
        if not user.phone:
            logger.error(f"User {user_id} does not have a phone number")
            notification.status = NotificationStatus.FAILED
            db.commit()
            return False
            
        # Update status to sending
        notification.status = NotificationStatus.SENDING
        db.commit()
        
        # Send SMS
        success = sms_service.send_sms(user.phone, body)
            
        # Update notification status based on result
        if success:
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.utcnow()
            db.commit()
            logger.info(f"SMS notification {notification_id} delivered successfully")
            return True
        else:
            # Mark as failed
            notification.status = NotificationStatus.FAILED
            db.commit()
            logger.warning(f"SMS notification {notification_id} failed, will retry")
            raise Exception("Failed to send SMS")
            
    except Exception as e:
        logger.error(f"Error processing SMS notification {notification_id}: {str(e)}")
        # Update notification status to failed
        try:
            if notification:
                notification.status = NotificationStatus.FAILED
                db.commit()
        except:
            pass
        
        # Re-raise the exception for Celery to handle retry
        raise
    finally:
        db.close()

@shared_task(
    bind=True,
    name="send_in_app_notification",
    max_retries=2,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_in_app_notification(self, notification_id: str, user_id: str, subject: str, body: str):
    """
    Task to send in-app notification
    """
    logger.info(f"Processing in-app notification {notification_id} for user {user_id}")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get notification
        notification = db.query(Notification).filter(
            Notification.id == UUID(notification_id)
        ).first()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found in database")
            return False
            
        # Update status to sending
        notification.status = NotificationStatus.SENDING
        db.commit()
        
        # Send in-app notification
        success = in_app_service.send_in_app_notification(
            user_id, 
            {"id": notification_id, "subject": subject, "body": body}
        )
            
        # Update notification status based on result
        if success:
            notification.status = NotificationStatus.DELIVERED
            notification.delivered_at = datetime.utcnow()
            db.commit()
            logger.info(f"In-app notification {notification_id} delivered successfully")
            return True
        else:
            # Mark as failed
            notification.status = NotificationStatus.FAILED
            db.commit()
            logger.warning(f"In-app notification {notification_id} failed, will retry")
            raise Exception("Failed to send in-app notification")
            
    except Exception as e:
        logger.error(f"Error processing in-app notification {notification_id}: {str(e)}")
        # Update notification status to failed
        try:
            if notification:
                notification.status = NotificationStatus.FAILED
                db.commit()
        except:
            pass
        
        # Re-raise the exception for Celery to handle retry
        raise
    finally:
        db.close()
