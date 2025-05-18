import logging
from typing import Dict, Any
import json
import aioredis  # For WebSocket broadcasting via Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class InAppNotificationService:
    def __init__(self):
        self.redis = None
        
    async def initialize(self):
        """Initialize Redis connection for pub/sub"""
        if not self.redis:
            self.redis = await aioredis.create_redis_pool("redis://redis:6379")
    
    def send_in_app_notification(self, user_id: str, notification: Dict[str, Any]) -> bool:
        """
        Send an in-app notification via Redis pub/sub
        
        Args:
            user_id: user identifier
            notification: notification data
            
        Returns:
            bool: True if notification was published successfully, False otherwise
        """
        try:
            import redis
            # Use synchronous Redis client for Celery tasks
            r = redis.Redis(host='redis', port=6379, db=0)
            
            # Channel name for the specific user
            channel_name = f"user:{user_id}:notifications"
            
            # Publish notification
            r.publish(
                channel_name, 
                json.dumps(notification)
            )
            
            logger.info(f"In-app notification sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send in-app notification to user {user_id}: {str(e)}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

# Create a singleton instance
in_app_service = InAppNotificationService()
