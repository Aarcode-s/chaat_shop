from app.schemas import BaseModel, ConfigDict, Decimal, Field, datetime
from app.schemas.order_item_schemas import OrderItemCreate, OrderItemResponse

# ============================================================
# ORDER SCHEMAS
# ============================================================


class OrderCreate(BaseModel):
    customer_name: str = Field(
        min_length=1,
        max_length=100,
    )

    customer_phone: str = Field(
        min_length=10,
        max_length=20,
    )

    items: list[OrderItemCreate] = Field(
        min_length=1,
    )


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    total_amount: Decimal
    status: str
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderStatusUpdate(BaseModel):
    status: str = Field(
        min_length=1,
        max_length=20,
    )




