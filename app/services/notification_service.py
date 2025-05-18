from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
import uuid
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

import logging

from app.db.models import Notification, User, NotificationStatus, NotificationType
from app.schemas.notification import NotificationCreate
from app.services.tasks.notification_tasks import (
    send_email_notification,
    send_sms_notification,
    send_in_app_notification
)

logger = logging.getLogger(__name__)

def create_notification(
    db: Session, 
    notification_data: NotificationCreate
) -> Tuple[uuid.UUID, str, str]:
    """
    Create notifications and queue them using Celery tasks
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == notification_data.user_id).first()
        if not user:
            # raise ValueError(f"User with ID {notification_data.user_id} not found")
            # Create new user if doesn't exist
            logger.info(f"User with ID {notification_data.user_id} not found, creating new user")
            
            # Generate default email from user_id if not provided
            default_email = f"user_{str(notification_data.user_id)}@example.com"
            
            # Create new user with default settings
            user = User(
                id=notification_data.user_id,
                email=default_email,  # Set default email
                phone=None,  # Phone is optional, can be updated later
                email_enabled=True,  # Enable email notifications by default
                sms_enabled=False,  # SMS disabled until phone number is provided
                in_app_enabled=True  # Enable in-app notifications by default
            )
            
            # Add to database
            db.add(user)
            db.flush()  # Flush to get the ID without committing transaction
            logger.info(f"Created new user with ID {user.id}")
        
        notification_records = []
        task_ids = []
        
        for channel in notification_data.channels:
            # Check if the channel is enabled for the user
            if channel == NotificationType.EMAIL and not user.email_enabled:
                continue
            if channel == NotificationType.SMS and not user.sms_enabled:
                continue
            if channel == NotificationType.IN_APP and not user.in_app_enabled:
                continue
            
            # Create notification record
            notification = Notification(
                id=uuid.uuid4(),
                user_id=user.id,
                type=channel,
                subject=notification_data.message.subject,
                body=notification_data.message.body,
                status=NotificationStatus.QUEUED,
                priority=notification_data.metadata.get("priority", "medium"),
            )
            
            db.add(notification)
            notification_records.append(notification)
    
    except SQLAlchemyError as e:  # More specific database exception
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred")
    
    db.commit()
    
    # Queue notifications using Celery tasks
    for notification in notification_records:
        try:
            task = None
            if notification.type == NotificationType.EMAIL:
                task = send_email_notification.apply_async(
                    args=[str(notification.id), str(user.id), notification.subject, notification.body],
                    eta=notification_data.schedule_time
                )
            elif notification.type == NotificationType.SMS:
                task = send_sms_notification.apply_async(
                    args=[str(notification.id), str(user.id), notification.body],
                    eta=notification_data.schedule_time
                )
            elif notification.type == NotificationType.IN_APP:
                task = send_in_app_notification.apply_async(
                    args=[str(notification.id), str(user.id), notification.subject, notification.body],
                    eta=notification_data.schedule_time
                )
                
            if task:
                notification.task_id = task.id
                task_ids.append(task.id)
        except Exception as e:
            logger.error(f"Failed to queue task for notification {notification.id}: {str(e)}")
    
    # Commit task IDs back to the database
    db.commit()
    
    return notification_records[0].id if notification_records else None, "queued", task_ids[0] if task_ids else None

def get_notification_by_id(db: Session, notification_id: uuid.UUID) -> Optional[Notification]:
    """
    Get a notification by ID
    """
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_user_notifications(
    db: Session, 
    user_id: uuid.UUID, 
    status_filter: str = "all",
    type_filter: str = "all",
    page: int = 1, 
    limit: int = 20
) -> Tuple[List[Notification], int, int]:
    """
    Get notifications for a specific user with pagination and filtering
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    # Apply filters if provided
    if status_filter != "all":
        query = query.filter(Notification.status == status_filter)
    
    if type_filter != "all":
        query = query.filter(Notification.type == type_filter)
    
    # Sort by created_at descending (newest first)
    query = query.order_by(Notification.created_at.desc())
    
    # Count total for pagination
    total = query.count()
    
    # Calculate total pages
    pages = (total + limit - 1) // limit
    
    # Apply pagination
    notifications = query.offset((page - 1) * limit).limit(limit).all()
    
    return notifications, total, pages

def update_notification_status(
    db: Session, 
    notification_id: uuid.UUID, 
    status: NotificationStatus,
    delivered_at: Optional[datetime] = None
) -> bool:
    """
    Update the status of a notification
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return False
    
    notification.status = status
    if status == NotificationStatus.DELIVERED and delivered_at:
        notification.delivered_at = delivered_at
    
    db.commit()
    return True

def mark_notification_as_read(db: Session, notification_id: uuid.UUID) -> bool:
    """
    Mark a notification as read
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return False
    
    notification.status = NotificationStatus.READ
    notification.read_at = datetime.utcnow()
    
    db.commit()
    return True
