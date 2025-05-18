from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.db.database import get_db
from app.schemas.notification import UserNotificationsResponse, NotificationStatus, NotificationType
from app.services.notification_service import get_user_notifications

router = APIRouter()

@router.get("/{user_id}/notifications", response_model=UserNotificationsResponse)
async def get_user_notifications_endpoint(
    user_id: UUID = Path(..., description="The ID of the user to get notifications for"),
    status: Optional[str] = Query("all", description="Filter by notification status"),
    type: Optional[str] = Query("all", description="Filter by notification type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get all notifications for a specific user with pagination and filtering options
    """
    # Validate status if provided
    if status != "all" and status not in [s.value for s in NotificationStatus]:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    
    # Validate type if provided
    if type != "all" and type not in [t.value for t in NotificationType]:
        raise HTTPException(status_code=400, detail="Invalid notification type filter")
    
    notifications, total, pages = get_user_notifications(
        db, user_id, status, type, page, limit
    )
    
    # Convert SQLAlchemy models to Pydantic compatible format
    notification_list = []
    for notification in notifications:
        notification_list.append({
            "notification_id": notification.id,
            "type": notification.type,
            "message": {
                "subject": notification.subject,
                "body": notification.body
            },
            "status": notification.status,
            "created_at": notification.created_at,
            "delivered_at": notification.delivered_at,
            "task_id": notification.task_id
        })
    
    response = {
        "user_id": user_id,
        "notifications": notification_list,
        "pagination": {
            "total": total,
            "page": page,
            "pages": pages,
            "limit": limit
        },
        "version": "v1"
    }
    
    return response

