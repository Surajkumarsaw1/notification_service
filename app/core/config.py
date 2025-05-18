import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Base settings
    API_PREFIX: str = "/api"
    DEBUG: bool = Field(default=True) # False in prod
    PROJECT_NAME: str = "notification-service"
    VERSION: str = "1.0.0"
    
    # API Versions
    CURRENT_API_VERSION: str = "v2"
    DEPRECATED_API_VERSIONS: list = Field(default=["v1"])  # Mark deprecated versions
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="amqp://guest:guest@rabbitmq:5672/")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")
    
    # Google Services - Gmail API
    GOOGLE_CLIENT_SECRET_FILE: str = Field(..., env="GOOGLE_CLIENT_SECRET_FILE")
    GOOGLE_TOKEN_FILE: str = Field(default="token.json")
    GMAIL_SENDER: str = Field(..., env="GMAIL_SENDER")
    
    # SMS
    TWILIO_ACCOUNT_SID: str = Field(..., env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = Field(..., env="TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER: str = Field(..., env="TWILIO_FROM_NUMBER")
    
    # Retry settings
    MAX_RETRIES: int = Field(default=3)
    RETRY_DELAYS: list = Field(default=[300, 1800, 7200])  # in seconds: 5min, 30min, 2h
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
