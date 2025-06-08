# tests/test_order_service/test_orders.py

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import AsyncMock, patch

from app import app  # Replace with the actual FastAPI app import

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../order-service/src")))

client = TestClient(app)

@pytest.fixture
def fake_order():
    return {
        "id": "order123",
        "customer_email": "test@example.com",
        "item": "Widget",
        "quantity": 2,
        "status": "PENDING",
    }


@patch("api.routes.orders.order_service.create_order", new_callable=AsyncMock)
def test_create_order_success(mock_create_order, fake_order):
    mock_create_order.return_value = fake_order

    order_data = {
        "customer_email": "test@example.com",
        "item": "Widget",
        "quantity": 2,
    }

    response = client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "order123"
    mock_create_order.assert_awaited_once()


@patch("api.routes.orders.order_service.list_orders", new_callable=AsyncMock)
def test_list_orders_success(mock_list_orders, fake_order):
    mock_list_orders.return_value = [fake_order]

    response = client.get("/orders")

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    mock_list_orders.assert_awaited_once()


@patch("api.routes.orders.order_service.get_order", new_callable=AsyncMock)
def test_get_order_success(mock_get_order, fake_order):
    mock_get_order.return_value = fake_order

    response = client.get("/orders/order123")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == "order123"
    mock_get_order.assert_awaited_once_with("order123", ANY)


@patch("api.routes.orders.order_service.update_order_status", new_callable=AsyncMock)
def test_update_order_status_success(mock_update_status):
    mock_update_status.return_value = True

    status_update = {"status": "SHIPPED"}
    response = client.put("/orders/order123/status", json=status_update)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Order status updated successfully"
    mock_update_status.assert_awaited_once()
