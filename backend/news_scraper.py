import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import NewsArticleDB
import logging
import os
import re

logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """Remove invalid characters from filenames."""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace invalid characters with `_`
    filename = re.sub(r'\s+', '_', filename.strip())  # Replace spaces with `_`
    return filename # Replace invalid characters with `_`

def scrape_and_store_articles(db: Session):
    """Scrape articles from Google News and store in database"""
    try:
        # Google News search URL
        url = os.getenv("GOOGLE_NEWS_URL", 'https://news.google.com/search?q=2025%20super%20bowl&hl=en-IN&gl=IN&ceid=IN%3Aen')
        
        # Send GET request
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find news articles
        articles = soup.select("article")

        for article in articles:
            title_tag = article.select_one("a.JtKRv")
            timestamp_tag = article.select_one("time.hvbAAd")
            source_tag = article.select_one("div.vr1PYe")
            url_tag = article.select_one("a.WwrzSb") 
            image_tag = article.select_one("img.Quavad")
            
            if title_tag and url_tag:
                title = title_tag.get_text(strip=True)
                url = "https://news.google.com" + url_tag["href"].replace("./", "/")
                timestamp_str = timestamp_tag["datetime"] if timestamp_tag and timestamp_tag.has_attr("datetime") else ""
                source = source_tag.get_text(strip=True) if source_tag else ""
                
                # Extract first image URL from srcset
                imageurl = ""
                if image_tag and image_tag.has_attr("src"):
                    imageurl = "https://news.google.com" + image_tag["srcset"].split(",")[0].split(" ")[0]
                
                # Download the image and save it locally
                if imageurl:
                    image_response = requests.get(imageurl, stream=True)  # Stream to handle large images
                    if image_response.status_code == 200:
                        sanitized_title = sanitize_filename(title)  # Sanitize title for filename


                        # Use an absolute path inside Docker to store images in the shared volume
                        STATIC_DIR = "/app/static/images"
                        os.makedirs(STATIC_DIR, exist_ok=True)  # Ensure directory exists

                        # Save image in the shared static directory
                        image_filename = os.path.join(STATIC_DIR, f"{sanitized_title}.jpg")


                        # Save the image
                        with open(image_filename, 'wb') as f:
                            f.write(image_response.content)

                        # Update image URL to the saved local path
                        imageurl = f"/static/images/{sanitized_title}.jpg"

                                
                # Check if article already exists

                existing = db.query(NewsArticleDB).filter_by(url=url).first()
                if existing:
                    continue

                # Create new article record
                new_article = NewsArticleDB(
                    title=title,
                    source=source,
                    url=url,
                    summary="",  # Google News doesn't provide summaries
                    timestamp=datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ") if timestamp_str else datetime.utcnow(),
                    imageurl=imageurl
                    # Save the local path of the image

                )
                db.add(new_article)

        db.commit()
        return {"status": "success", "message": "Articles scraped and stored successfully"}

    except requests.exceptions.RequestException as e:
        logger.error(f"Scraping request failed: {e}")
        return {"status": "error", "message": "Failed to scrape articles"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        return {"status": "error", "message": "Failed to store articles"}
