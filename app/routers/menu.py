
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database import DBSession
from app.models import MenuItem
from app.routers import AdminVerify
from app.schemas.menu_schemas import (
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
)

router = APIRouter(
    prefix="/api/menu",
    tags=["Menu"],
)


@router.get("", response_model=list[MenuItemResponse])
def get_menu_items(db: DBSession):
    statement = select(MenuItem).order_by(MenuItem.id)
    results = db.execute(statement).scalars().all()
    return results


@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(db: DBSession, item_id: int):
    statement = select(MenuItem).where(MenuItem.id == item_id)
    menu_item = db.execute(statement).scalar_one_or_none()

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    return menu_item


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=MenuItemResponse,
)
def create_menu_item(
    detail: MenuItemCreate,
    db: DBSession,
    admin: AdminVerify,
):
    new_menu_item = MenuItem(
        name=detail.name,
        category=detail.category,
        description=detail.description,
        price=detail.price,
        is_available=detail.is_available,
    )

    try:
        db.add(new_menu_item)
        db.commit()
        db.refresh(new_menu_item)
    except SQLAlchemyError:
        db.rollback()
        raise

    return new_menu_item


@router.patch(
    "/{item_id}",
    response_model=MenuItemResponse,
)
def update_menu_item(
    item_id: int,
    data: MenuItemUpdate,
    db: DBSession,
    admin: AdminVerify,
):
    statement = select(MenuItem).where(MenuItem.id == item_id)
    menu_item = db.execute(statement).scalar_one_or_none()

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu_item, field, value)

    db.commit()
    db.refresh(menu_item)
    return menu_item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_menu_item(
    item_id: int,
    db: DBSession,
    admin: AdminVerify,
):
    statement = select(MenuItem).where(MenuItem.id == item_id)
    menu_item = db.execute(statement).scalar_one_or_none()

    if menu_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    db.delete(menu_item)
    db.commit()

    