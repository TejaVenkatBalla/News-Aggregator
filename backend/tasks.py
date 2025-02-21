from celery import shared_task
from celery_config import celery_app
from sqlalchemy.orm import Session
from database import get_db
from news_fetch import fetch_and_store_articles
from news_scraper import scrape_and_store_articles
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_articles_task():
    """Celery task to fetch articles from NewsAPI"""
    try:
        db: Session = next(get_db())
        result = fetch_and_store_articles(db)
        logger.info(f"Fetch articles task completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in fetch_articles_task: {e}")
        raise

@shared_task
def scrape_articles_task():
    """Celery task to scrape articles from Google News"""
    try:
        db: Session = next(get_db())
        result = scrape_and_store_articles(db)
        logger.info(f"Scrape articles task completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in scrape_articles_task: {e}")
        raise

@shared_task
def rander():
    print("hello")
    logger.info(f"rander exexuted")
    return "hello"
    