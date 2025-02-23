from celery import Celery
import os

# Initialize Celery with environment variables
celery_app = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL'),
    backend=os.getenv('REDIS_URL'),
    include=["tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    broker_connection_retry_on_startup = True,
    beat_schedule={
        'fetch-articles-every-30-min': {
            'task': 'tasks.fetch_articles_task',
            'schedule': 1800.0,  # 30 minutes in seconds
            'options': {'queue': 'periodic_tasks'}
        },
        'scrape-articles-every-hour': {
            'task': 'tasks.scrape_articles_task',
            'schedule': 3600.0,  # 1 hour in seconds
            'options': {'queue': 'periodic_tasks'}
        },
        'rander-every-10-sec': {
            'task': 'tasks.rander',
            'schedule': 10.0,  # 10 sec in seconds
            'options': {'queue': 'periodic_tasks'}
        },
    }
)

