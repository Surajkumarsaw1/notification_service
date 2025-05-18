from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in-app"

class NotificationStatus(str, Enum):
    QUEUED = "queued"
    SENDING = "sending"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class NotificationMessage(BaseModel):
    subject: str
    body: str

class NotificationCreate(BaseModel):
    user_id: UUID4
    channels: List[NotificationType]
    message: NotificationMessage
    metadata: Optional[Dict] = {}
    schedule_time: Optional[datetime] = None

class NotificationResponse(BaseModel):
    notification_id: UUID4
    status: NotificationStatus
    timestamp: datetime
    task_id: Optional[str] = None
    version: Optional[str] = None

class NotificationDetail(BaseModel):
    notification_id: UUID4
    type: NotificationType
    message: NotificationMessage
    status: NotificationStatus
    created_at: datetime
    delivered_at: Optional[datetime] = None
    task_id: Optional[str] = None

class PaginationInfo(BaseModel):
    total: int
    page: int
    pages: int
    limit: int

class UserNotificationsResponse(BaseModel):
    user_id: UUID4
    notifications: List[NotificationDetail]
    pagination: PaginationInfo
    version: Optional[str] = None
    filters: Optional[Dict] = None

    class Config:
        orm_mode = True
