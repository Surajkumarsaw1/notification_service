import logging
from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy import func
from typing import List

from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import Notification, User, NotificationStatus, NotificationPriority, NotificationType
from app.services.tasks.notification_tasks import send_email_notification

logger = logging.getLogger(__name__)

@shared_task(name="send_daily_digest")
def send_daily_digest():
    """
    Send a daily digest of notifications to users
    """
    logger.info("Starting daily digest task")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get users who have unread notifications from the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Find users with unread notifications
        users_with_notifications = db.query(User).join(
            Notification, User.id == Notification.user_id
        ).filter(
            Notification.created_at >= yesterday,
            Notification.status != NotificationStatus.READ,
            User.email_enabled == True  # Only send to users with email enabled
        ).distinct().all()
        
        logger.info(f"Found {len(users_with_notifications)} users with unread notifications")
        
        for user in users_with_notifications:
            # Get unread notifications for this user
            notifications = db.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.created_at >= yesterday,
                Notification.status != NotificationStatus.READ
            ).all()
            
            # If user has notifications, send a digest
            if notifications:
                # Create a digest notification
                notification = Notification(
                    user_id=user.id,
                    type=NotificationType.EMAIL,
                    subject="Your Daily Notification Digest",
                    body=_create_digest_body(notifications),
                    status=NotificationStatus.QUEUED,
                    priority=NotificationPriority.LOW,
                )
                
                db.add(notification)
                db.commit()
                
                # Queue the digest email
                send_email_notification.delay(
                    str(notification.id),
                    str(user.id),
                    notification.subject,
                    notification.body
                )
                
                logger.info(f"Scheduled digest email for user {user.id}")
        
        return True
    except Exception as e:
        logger.error(f"Error sending daily digests: {str(e)}")
        return False
    finally:
        db.close()

@shared_task(name="cleanup_old_notifications")
def cleanup_old_notifications():
    """
    Clean up old notifications (older than 90 days)
    """
    logger.info("Starting cleanup of old notifications")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Define cutoff date (90 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Get count of old notifications
        count = db.query(func.count(Notification.id)).filter(
            Notification.created_at < cutoff_date
        ).scalar()
        
        logger.info(f"Found {count} old notifications to cleanup")
        
        # Delete old notifications
        if count > 0:
            db.query(Notification).filter(
                Notification.created_at < cutoff_date
            ).delete(synchronize_session=False)
            db.commit()
        
        logger.info(f"Cleaned up {count} old notifications")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {str(e)}")
        return False
    finally:
        db.close()

def _create_digest_body(notifications: List[Notification]) -> str:
    """
    Create the HTML body for the daily digest email
    """
    html_body = f"""
    
        Your Daily Notification Digest
        You have the following unread notifications:
        
    """
    
    for notification in notifications:
        html_body += f"""
        
{notification.subject}: {notification.body[:100]}...
        
"""
    
    html_body += """
        
        Login to your account to view all notifications.
    
    
    """
    
    return html_body
