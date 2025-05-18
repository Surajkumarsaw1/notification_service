from pydantic import BaseModel, Field, UUID4, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    pass

class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = True
    in_app_enabled: bool = True

class User(UserBase):
    id: UUID4
    email_enabled: bool
    sms_enabled: bool
    in_app_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
