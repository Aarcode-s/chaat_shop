from app.schemas import BaseModel, ConfigDict, Decimal, Field

# ============================================================
# ORDER ITEM SCHEMAS
# ============================================================


class OrderItemCreate(BaseModel):
    menu_item_id: int = Field(
        gt=0,
    )

    quantity: int = Field(
        gt=0,
    )


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    item_name: str
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )


