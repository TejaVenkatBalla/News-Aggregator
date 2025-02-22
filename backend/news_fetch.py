import requests
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import NewsArticleDB
import logging
import os

logger = logging.getLogger(__name__)

def fetch_and_store_articles(db: Session):
    """Fetch articles from NewsAPI and store in database"""
    try:
        # API endpoint and parameters
        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": os.getenv("NEWS_API_KEY",'899e4e23f4404bb38efcac044b654665'),
            "q": "SuperBowl-2025",
            "language": "en",
            "sortBy": "popularity",
            "searchIn": "title,description"
        }

        # Make API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Process and store articles
        for article in data.get('articles', []):
            # Check if article already exists
            existing = db.query(NewsArticleDB).filter_by(url=article['url']).first()
            if existing:
                continue

            # Create new article record
            new_article = NewsArticleDB(
                title=article['title'],
                source=article['source']['name'],
                url=article['url'],
                summary=article['description'],
                timestamp=datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ"),
                imageurl=article['urlToImage'] if article['urlToImage'] else None  # Extracting image URL

            )

            db.add(new_article)

        db.commit()
        return {"status": "success", "message": f"Added {len(data['articles'])} new articles"}

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {"status": "error", "message": "Failed to fetch articles"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        return {"status": "error", "message": "Failed to store articles"}
