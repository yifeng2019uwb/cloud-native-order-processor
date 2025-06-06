# docker/tests/conftest.py
"""
Shared pytest fixtures for all tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Import your app (adjust import based on your structure)
# from api.main import app
# from api.database import Base, get_db

@pytest.fixture(scope="session")
def test_db():
    """Create a test database"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    # Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal()
    
    # Cleanup
    engine.dispose()

@pytest.fixture
def client(test_db):
    """Create a test client"""
    # Override the database dependency
    # app.dependency_overrides[get_db] = lambda: test_db
    
    # with TestClient(app) as client:
    #     yield client
    pass

@pytest.fixture
def sample_order_data():
    """Sample order data for tests"""
    return {
        "order_id": "ORD-001",
        "customer_email": "test@example.com",
        "customer_name": "Test User",
        "items": [
            {"product_id": "PROD-001", "quantity": 2, "price": 10.00}
        ],
        "total_amount": 20.00,
        "status": "pending"
    }
