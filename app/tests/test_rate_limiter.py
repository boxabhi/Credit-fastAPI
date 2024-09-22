import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app, get_db  # Adjust this import based on your app structure
from ..models import Base, User

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def test_app():
    yield TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    # Create a new database session for a test
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.mark.asyncio
async def test_rate_limiter(test_app, db_session):
    # Add a test user to the database
    test_user = User(email="test@example.com", name="Test User", password="hashed_password", limit=5, window_seconds=60)
    db_session.add(test_user)
    db_session.commit()

    # Simulate authentication (adjust based on your auth logic)
    auth_token = "Bearer some_token"  # You may need to generate a valid token here

    # Send requests to test the rate limiter
    for _ in range(5):
        response = test_app.get("/some_endpoint", headers={"Authorization": auth_token})
        assert response.status_code == 200  # Expecting successful response

    # The next request should trigger the rate limit
    response = test_app.get("/some_endpoint", headers={"Authorization": auth_token})
    assert response.status_code == 429  # Expecting rate limit exceeded response
    assert "Rate limit exceeded" in response.text  # Check if the message is correct

@pytest.mark.asyncio
async def test_register(test_app, db_session):
    response = test_app.post("/register/", json={
        "email": "new_user@example.com",
        "name": "New User",
        "password": "password123",
        "limit": 5,
        "window_seconds": 60
    })
    
    assert response.status_code == 201  # Expecting successful registration
    assert response.json()["status"] is True  # Check success status
