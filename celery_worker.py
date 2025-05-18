from app.core.celery_app import celery_app

# This module is the entry point for Celery workers
if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=info"])
