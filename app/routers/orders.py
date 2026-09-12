from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import DBSession
from app.models import MenuItem, Order, OrderItem
from app.schemas import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
)

router = APIRouter(
    prefix="/api/orders",
    tags=["Orders"],
)


# ============================================================
# CREATE ORDER
# ============================================================

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: OrderCreate,
    db:DBSession,
):
    total_amount = Decimal("0.00")
    order_items = []

    for item in data.items:

        statement = select(MenuItem).where(
            MenuItem.id == item.menu_item_id
        )

        result = db.execute(statement)

        menu_item = result.scalar_one_or_none()

        if menu_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item {item.menu_item_id} not found",
            )

        if not menu_item.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{menu_item.name} is currently unavailable",
            )

        subtotal = menu_item.price * item.quantity

        total_amount += subtotal

        order_items.append(
            OrderItem(
                menu_item_id=menu_item.id,
                item_name=menu_item.name,
                quantity=item.quantity,
                unit_price=menu_item.price,
            )
        )

    order = Order(
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        total_amount=total_amount,
        status="pending",
        items=order_items,
    )

    db.add(order)

    db.commit()

    db.refresh(order)

    return order


# ============================================================
# GET ONE ORDER
# ============================================================

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    db:DBSession,
):
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )

    result = db.execute(statement)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    return order


# ============================================================
# GET ALL ORDERS
# ============================================================

@router.get(
    "",
    response_model=list[OrderResponse],
)
def get_orders(
    db:DBSession,
):
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )

    result = db.execute(statement)

    orders = result.scalars().all()

    return orders


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db:DBSession,
):
    statement = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
    )

    result = db.execute(statement)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    allowed_statuses = {
        "pending",
        "confirmed",
        "preparing",
        "ready",
        "completed",
        "cancelled",
    }

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order status",
        )

    order.status = data.status

    db.commit()

    db.refresh(order)

    return order