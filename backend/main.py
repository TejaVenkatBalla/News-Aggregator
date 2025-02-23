from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles

from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from database import get_db
from models import NewsArticle, NewsArticleDB, UserDB, UserCreate, User
from news_fetch import fetch_and_store_articles
from news_scraper import scrape_and_store_articles
from passlib.context import CryptContext
import os

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY",'f8c93b1a5e92df23b7a1d66c917b5e6ebde124f9e2b4c0986b40e1d22a3b2c1f')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)  # Create the folder if it doesn't exist
    
app = FastAPI()


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db_client():
    try:
        from database import engine
        from models import NewsArticleDB, UserDB
        NewsArticleDB.metadata.create_all(bind=engine)
        UserDB.metadata.create_all(bind=engine)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Startup error: {e}")

# Authentication utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Authentication routes
@app.post("/auth/register", response_model=User)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = pwd_context.hash(user.password)
    db_user = UserDB(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login")
async def login(credentials: dict, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == credentials.get("username")).first()
    if not user or not pwd_context.verify(credentials.get("password"), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# News routes
@app.get("/api/news", response_model=List[NewsArticle])
async def get_news(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        articles = db.query(NewsArticleDB).order_by(NewsArticleDB.timestamp.desc()).all()
        return articles
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Error fetching news articles")

@app.post("/api/fetch_news", status_code=200)
async def trigger_fetch_news(db: Session = Depends(get_db)):
    """Trigger news fetch and store operation"""
    result = fetch_and_store_articles(db)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return {"status": "success", "message": result["message"]}

@app.post("/api/scrape_news", status_code=200)
async def trigger_scrape_news(db: Session = Depends(get_db)):
    """Trigger news scrape operation"""
    result =scrape_and_store_articles(db)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return {"status": "success", "message": result["message"]}

# Root route
@app.get("/", status_code=200)
def index():
    return {"message": "Hello, World!"}
