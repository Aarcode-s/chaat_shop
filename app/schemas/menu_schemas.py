
from typing import Literal

from app.schemas import BaseModel, ConfigDict, Decimal, Field

MenuCategory = Literal["chaat", "snacks", "drinks"]

# ============================================================
# MENU ITEM SCHEMAS
# ============================================================


class MenuItemCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    category: MenuCategory

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    price: Decimal = Field(
        gt=0,
        decimal_places=2,
        max_digits=10,
    )

    is_available: bool = True


class MenuItemUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    category: MenuCategory | None = None

    description: str | None = Field(
        default=None,
        max_length=255,
    )

    price: Decimal | None = Field(
        default=None,
        gt=0,
        decimal_places=2,
        max_digits=10,
    )

    is_available: bool | None = None


class MenuItemResponse(BaseModel):
    id: int
    name: str
    category: MenuCategory
    description: str | None
    price: Decimal
    is_available: bool

    model_config = ConfigDict(
        from_attributes=True,
    )
