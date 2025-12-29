"""Pytest configuration and shared fixtures for the Tax Filing System.

This module provides:
- Database fixtures with test isolation
- Async database fixtures
- Authentication fixtures
- Common test utilities
"""
import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only_32_chars_min"
os.environ["ENCRYPTION_KEY"] = "dGVzdF9lbmNyeXB0aW9uX2tleV9mb3JfdGVzdGluZw=="

from app.database import Base
from app.config import Settings, get_settings
from app.security import create_access_token


# =============================================================================
# Test Database Configuration
# =============================================================================

TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_DATABASE_URL_ASYNC = "sqlite+aiosqlite:///./test.db"

# Synchronous test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "async_test: mark test as async")


# =============================================================================
# Event Loop Fixture
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test.
    
    Creates all tables before the test and drops them after.
    Provides full test isolation.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="module")
def test_db_module() -> Generator[Session, None, None]:
    """
    Create a database that persists across a module's tests.
    
    Useful for integration tests where you need data to persist
    across multiple test functions.
    """
    Base.metadata.create_all(bind=test_engine)
    
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


# =============================================================================
# FastAPI Test Client Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database override.
    
    Provides a fresh database for each test.
    """
    from app.database import get_db
    from backend.main import app
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(test_db: Session) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client.
    
    For testing async endpoints.
    """
    from app.database import get_db
    from backend.main import app
    
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def test_user(test_db: Session) -> dict:
    """
    Create a test user and return user data with auth token.
    
    Returns:
        dict with user info and access_token
    """
    from app import models
    from app.security import get_password_hash
    
    # Create user
    user = models.User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create profile
    profile = models.UserProfile(
        user_id=user.id,
        preferred_mode="novice",
        theme="light",
        language="en",
    )
    test_db.add(profile)
    test_db.commit()
    
    # Generate token
    token = create_access_token(data={"sub": user.email})
    
    return {
        "user": user,
        "email": user.email,
        "password": "testpassword123",
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def authenticated_client(client: TestClient, test_user: dict) -> TestClient:
    """
    Create a test client with authentication headers pre-set.
    """
    client.headers.update(test_user["headers"])
    return client


# =============================================================================
# Tax Form Fixtures
# =============================================================================

@pytest.fixture
def test_tax_form(test_db: Session, test_user: dict) -> "models.TaxForm":
    """Create a test tax form."""
    from app import models
    
    form = models.TaxForm(
        owner_id=test_user["user"].id,
        year=2024,
        filing_status="single",
        status="in_progress",
        form_data={},
        total_income=50000.0,
        adjusted_gross_income=45000.0,
        taxable_income=32000.0,
        total_tax=4800.0,
        total_payments=5000.0,
        refund_or_amount_owed=200.0,
    )
    test_db.add(form)
    test_db.commit()
    test_db.refresh(form)
    return form


# =============================================================================
# Mock Settings Fixture
# =============================================================================

@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        ENVIRONMENT="testing",
        DEBUG=True,
        DATABASE_URL=TEST_DATABASE_URL,
        SECRET_KEY="test_secret_key_for_testing_only_32_chars_min",
        CORS_ORIGINS=["http://localhost:3000"],
    )


# =============================================================================
# Utility Functions
# =============================================================================

def create_test_user_data(
    email: str = "test@example.com",
    password: str = "testpassword123",
    full_name: str = "Test User"
) -> dict:
    """Helper to create user registration data."""
    return {
        "email": email,
        "password": password,
        "full_name": full_name,
    }


def create_test_tax_form_data(
    year: int = 2024,
    filing_status: str = "single"
) -> dict:
    """Helper to create tax form data."""
    return {
        "year": year,
        "filing_status": filing_status,
    }
