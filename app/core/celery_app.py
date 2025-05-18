from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "notification_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.tasks.notification_tasks",
        "app.services.tasks.scheduled_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5 minutes
    broker_connection_retry_on_startup=True,
)

# Configure Celery Beat for scheduled tasks
celery_app.conf.beat_schedule = {
    'scheduled-digests': {
        'task': 'app.services.tasks.scheduled_tasks.send_daily_digest',
        'schedule': 3600.0 * 24,  # Run once per day
    },
    'cleanup-old-notifications': {
        'task': 'app.services.tasks.scheduled_tasks.cleanup_old_notifications',
        'schedule': 3600.0 * 24 * 7,  # Run once per week
    },
}

# Set default queues
celery_app.conf.task_default_queue = 'default'
celery_app.conf.task_queues = {
    'high': {'exchange': 'high', 'routing_key': 'high'},
    'default': {'exchange': 'default', 'routing_key': 'default'},
    'low': {'exchange': 'low', 'routing_key': 'low'}
}
celery_app.conf.task_routes = {
    'app.services.tasks.notification_tasks.send_email_notification': {'queue': 'high'},
    'app.services.tasks.notification_tasks.send_sms_notification': {'queue': 'high'},
    'app.services.tasks.notification_tasks.send_in_app_notification': {'queue': 'default'},
    'app.services.tasks.scheduled_tasks.*': {'queue': 'low'},
}
