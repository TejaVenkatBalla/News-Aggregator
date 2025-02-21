from celery import Celery
import os

# Initialize Celery with environment variables
celery_app = Celery(
    'tasks',
    #broker=os.getenv(f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0", redis://localhost:6379/0),
    #backend=os.getenv(f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0", redis://localhost:6379/0)
    # broker=os.getenv('CELERY_BROKER_URL', f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0"),
    # backend=os.getenv('CELERY_RESULT_BACKEND', f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0")
    broker=os.getenv('REDIS_URL'),
    backend=os.getenv('REDIS_URL'),
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
            'schedule': 10.0,  # 2 hours in seconds
            'options': {'queue': 'periodic_tasks'}
        },
    }
)

# Import tasks after app is created to avoid circular imports
celery_app.autodiscover_tasks()
