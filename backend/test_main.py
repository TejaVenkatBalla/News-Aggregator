import pytest
from fastapi.testclient import TestClient
from main import app
from models import UserDB

client = TestClient(app)

# Test user registration
def test_register_user():
    from database import get_db
    db = next(get_db())
    db.query(UserDB).filter(UserDB.email == "test@example.com").delete()
    db.commit()

    response = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_register_user_already_exists():
    from database import get_db
    db = next(get_db())
    db.query(UserDB).filter(UserDB.email == "test@example.com").delete()
    db.commit()

    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

# Test user login
def test_login_user():
    from database import get_db
    db = next(get_db())
    db.query(UserDB).filter(UserDB.email == "test@example.com").delete()
    db.commit()

    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    response = client.post("/auth/login", json={"username": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_user_invalid_credentials():
    from database import get_db
    db = next(get_db())
    db.query(UserDB).filter(UserDB.email == "test@example.com").delete()
    db.commit()

    response = client.post("/auth/login", json={"username": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

# Test fetching news articles without credentials
def test_get_news_without_credentials():
    response = client.get("/api/news")
    assert response.status_code == 401
    assert isinstance(response.json(), dict)  # Expecting a JSON response

# Test fetching news articles with credentials
def test_get_news():
    from database import get_db
    db = next(get_db())
    db.query(UserDB).filter(UserDB.email == "test@example.com").delete()
    db.commit()

    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    login_response = client.post("/auth/login", json={"username": "test@example.com", "password": "password123"})
    access_token = login_response.json()["access_token"]
    response = client.get("/api/news", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Clean up the test user after the test
    db.query(UserDB).filter(UserDB.email == "test@example.com").delete()
    db.commit()
