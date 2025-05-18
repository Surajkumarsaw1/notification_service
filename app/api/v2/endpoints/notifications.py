from fastapi import APIRouter, Depends, HTTPException, Path, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.db.models import NotificationStatus, NotificationPriority
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification_service import create_notification, get_notification_by_id

router = APIRouter()

@router.post("/", response_model=NotificationResponse)
async def send_notification_v2(
    notification: NotificationCreate,
    priority: NotificationPriority = Query(NotificationPriority.MEDIUM, description="Notification priority"),
    db: Session = Depends(get_db)
):
    """
    V2: Send a notification to a user with priority
    """
    try:
        # Add priority to metadata
        if not notification.metadata:
            notification.metadata = {}
        notification.metadata["priority"] = priority
        
        notification_id, status, task_id = create_notification(db, notification)
        return {
            "notification_id": notification_id,
            "status": status,
            "task_id": task_id,
            "timestamp": notification.schedule_time or datetime.utcnow(),
            "priority": priority,
            "version": "v2"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notification: {str(e)}"
        )

@router.get("/{notification_id}", response_model=Dict)
async def get_notification_status_v2(
    notification_id: UUID = Path(..., description="The ID of the notification to get"),
    include_body: bool = Query(False, description="Include notification body in response"),
    db: Session = Depends(get_db)
):
    """
    V2: Get a specific notification by ID with option to include body
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    response = {
        "notification_id": notification.id,
        "status": notification.status,
        "type": notification.type,
        "subject": notification.subject,
        "created_at": notification.created_at,
        "delivered_at": notification.delivered_at,
        "task_id": notification.task_id,
        "priority": notification.priority,
        "version": "v2"
    }
    
    # Include body if requested
    if include_body:
        response["body"] = notification.body
        
    return response

@router.post("/{notification_id}/cancel", response_model=Dict)
async def cancel_notification(
    notification_id: UUID = Path(..., description="The ID of the notification to cancel"),
    db: Session = Depends(get_db)
):
    """
    V2: Cancel a pending notification
    """
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    if notification.status not in [NotificationStatus.QUEUED, NotificationStatus.SENDING]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel notification with status '{notification.status}'"
        )
    
    # Here you would implement the cancellation logic using the Celery task ID
    # For simplicity, we'll just mark it as failed
    notification.status = NotificationStatus.FAILED
    db.commit()
    
    return {
        "notification_id": notification.id,
        "status": "cancelled",
        "version": "v2"
    }

@router.get("/", response_model=Dict)
async def get_notifications_v2(
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by type"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    V2: Get all notifications with advanced filtering options
    """
    # Here you would implement advanced search functionality
    # This is a placeholder for the actual implementation
    return {
        "notifications": [],
        "pagination": {
            "total": 0,
            "page": page,
            "pages": 0,
            "limit": limit
        },
        "filters": {
            "status": status,
            "type": type,
            "from_date": from_date,
            "to_date": to_date
        },
        "version": "v2"
    }
