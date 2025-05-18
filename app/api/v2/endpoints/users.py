from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime

from app.db.database import get_db
from app.schemas.notification import UserNotificationsResponse, NotificationStatus, NotificationType
from app.schemas.user import NotificationPreferences
from app.services.notification_service import get_user_notifications

router = APIRouter()

@router.get("/{user_id}/notifications", response_model=UserNotificationsResponse)
async def get_user_notifications_v2(
    user_id: UUID = Path(..., description="The ID of the user to get notifications for"),
    status: Optional[str] = Query("all", description="Filter by notification status"),
    type: Optional[str] = Query("all", description="Filter by notification type"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    V2: Get all notifications for a specific user with enhanced filtering
    """
    # Validate status if provided
    if status != "all" and status not in [s.value for s in NotificationStatus]:
        raise HTTPException(status_code=400, detail="Invalid status filter")
    
    # Validate type if provided
    if type != "all" and type not in [t.value for t in NotificationType]:
        raise HTTPException(status_code=400, detail="Invalid notification type filter")
    
    # In V2, we would implement enhanced filtering including date range
    # For now, we'll reuse the existing function but add version info
    notifications, total, pages = get_user_notifications(
        db, user_id, status, type, page, limit
    )
    
    response = {
        "user_id": user_id,
        "notifications": notifications,
        "pagination": {
            "total": total,
            "page": page,
            "pages": pages,
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
    
    return response

@router.get("/{user_id}/preferences", response_model=NotificationPreferences)
async def get_user_preferences(
    user_id: UUID = Path(..., description="The ID of the user"),
    db: Session = Depends(get_db)
):
    """
    V2: Get user notification preferences
    """
    from app.db.models import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "email_enabled": user.email_enabled,
        "sms_enabled": user.sms_enabled,
        "in_app_enabled": user.in_app_enabled
    }

@router.put("/{user_id}/preferences", response_model=NotificationPreferences)
async def update_user_preferences(
    preferences: NotificationPreferences,
    user_id: UUID = Path(..., description="The ID of the user"),
    db: Session = Depends(get_db)
):
    """
    V2: Update user notification preferences
    """
    from app.db.models import User
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user preferences
    user.email_enabled = preferences.email_enabled
    user.sms_enabled = preferences.sms_enabled
    user.in_app_enabled = preferences.in_app_enabled
    
    db.commit()
    
    return {
        "email_enabled": user.email_enabled,
        "sms_enabled": user.sms_enabled,
        "in_app_enabled": user.in_app_enabled
    }
