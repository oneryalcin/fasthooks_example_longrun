import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.security import hash_password, token_blacklist

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def db():
    """Provide a test database session"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    """Provide a test client"""
    # Clear token blacklist for each test
    token_blacklist.clear()
    return TestClient(app)

@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        email="testuser@example.com",
        hashed_password=hash_password("TestPassword123"),
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_user_data():
    """Provide test user data"""
    return {
        "email": "newuser@example.com",
        "password": "TestPassword123",
        "full_name": "New User"
    }

@pytest.fixture
def auth_headers(client, test_user):
    """Get authorization headers with valid token"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "TestPassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
