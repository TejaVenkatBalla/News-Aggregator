from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from pydantic import BaseModel, EmailStr
from datetime import datetime
from database import Base
from passlib.context import CryptContext
from typing import Optional

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    """Pydantic model for users"""
    email: EmailStr

class UserCreate(UserBase):
    """Pydantic model for creating users"""
    password: str

class User(UserBase):
    """Pydantic model for reading users"""
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class UserDB(Base):
    """SQLAlchemy model for users"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

class NewsArticleBase(BaseModel):
    """Pydantic model for news articles"""
    title: str
    source: str
    url: str
    summary: str
    timestamp: datetime
    imageurl: Optional[str] = None


class NewsArticleCreate(NewsArticleBase):
    """Pydantic model for creating news articles"""
    pass

class NewsArticle(NewsArticleBase):
    """Pydantic model for reading news articles"""
    id: int

    class Config:
        orm_mode = True

class NewsArticleDB(Base):
    """SQLAlchemy model for news articles"""
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False)
    url = Column(String(2083), nullable=False)
    summary = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    imageurl = Column(String(2083))  

    def __repr__(self):
        return f"<NewsArticleDB(id={self.id}, title={self.title}, source={self.source})>"
