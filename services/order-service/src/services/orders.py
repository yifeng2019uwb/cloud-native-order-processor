import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "common")
)

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from database import get_db
from models.order import OrderCreate, OrderResponse, OrderStatusUpdate, OrderStatus
from services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])
order_service = OrderService()


@router.post("", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, db=Depends(get_db)):
    """Create a new order"""
    try:
        order = await order_service.create_order(order_data, db)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    limit: int = 50,
    status: Optional[str] = None,
    customer_email: Optional[str] = None,
    db=Depends(get_db),
):
    """List orders with optional filtering"""
    try:
        orders = await order_service.list_orders(db, limit, status, customer_email)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list orders: {str(e)}")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db=Depends(get_db)):
    """Get a specific order by ID"""
    try:
        order = await order_service.get_order(order_id, db)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order: {str(e)}")


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str, status_data: OrderStatusUpdate, db=Depends(get_db)
):
    """Update order status"""
    try:
        success = await order_service.update_order_status(
            order_id, status_data.status, db
        )
        if not success:
            raise HTTPException(status_code=404, detail="Order not found")

        return {"message": "Order status updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update order status: {str(e)}"
        )
