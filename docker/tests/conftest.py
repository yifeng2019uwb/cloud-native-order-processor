# docker/tests/conftest.py
"""
Pytest configuration and fixtures for Order Processor API tests.
This version doesn't require FastAPI but is ready for when you add it.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add the api directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))


@pytest.fixture
def sample_order_data():
    """Sample order data for tests"""
    return {
        'order_id': 'ORD-001',
        'customer_email': 'test@example.com',
        'customer_name': 'John Doe',
        'items': [
            {'product_id': 'PROD-001', 'name': 'Widget', 'quantity': 2, 'price': 10.00},
            {'product_id': 'PROD-002', 'name': 'Gadget', 'quantity': 1, 'price': 25.00}
        ],
        'total_amount': 45.00,
        'status': 'pending',
        'created_at': '2024-01-15T10:30:00'
    }


@pytest.fixture
def sample_order():
    """Create a sample Order instance"""
    from models import Order  # Adjust import based on your structure
    
    return Order(
        order_id='ORD-001',
        customer_email='test@example.com',
        customer_name='John Doe',
        items=[
            {'product_id': 'PROD-001', 'name': 'Widget', 'quantity': 2, 'price': 10.00},
            {'product_id': 'PROD-002', 'name': 'Gadget', 'quantity': 1, 'price': 25.00}
        ],
        total_amount=45.00,
        status='pending',
        created_at='2024-01-15T10:30:00'
    )


@pytest.fixture
def empty_order_data():
    """Empty order data for tests"""
    return {
        'order_id': 'ORD-002',
        'customer_email': 'empty@example.com',
        'customer_name': 'Jane Smith',
        'items': [],
        'total_amount': 0.0,
        'status': 'pending',
        'created_at': '2024-01-15T11:00:00'
    }


# Future FastAPI fixtures (uncomment when you start using FastAPI)
"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_client():
    '''Create a test client for FastAPI app'''
    from main import app  # Import your FastAPI app
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_db():
    '''Create a test database'''
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    # Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal()
    
    engine.dispose()
"""