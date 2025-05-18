import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.db.models import NotificationStatus
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification_service import create_notification, get_notification_by_id

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=NotificationResponse)
async def send_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """
    Send a notification to a user
    """
    try:
        notification_id, status, task_id = create_notification(db, notification)
        return {
            "notification_id": notification_id,
            "status": status,
            "task_id": task_id,
            "timestamp": notification.schedule_time or datetime.utcnow(),
            "version": "v1"
        }
    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in send_notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{notification_id}", response_model=dict)
async def get_notification_status(
    notification_id: UUID = Path(..., description="The ID of the notification to get"),
    db: Session = Depends(get_db)
):
    """
    Get a specific notification by ID
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "notification_id": notification.id,
        "status": notification.status,
        "type": notification.type,
        "created_at": notification.created_at,
        "delivered_at": notification.delivered_at,
        "task_id": notification.task_id,
        "version": "v1"
    }
