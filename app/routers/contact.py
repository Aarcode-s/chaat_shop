from fastapi import APIRouter, status
from sqlalchemy import select

from app.database import DBSession
from app.models import ContactMessage
from app.schemas import (
    ContactMessageCreate,
    ContactMessageResponse,
)

router = APIRouter(
    prefix="/api/contact",
    tags=["Contact"],
)


# ============================================================
# CREATE CONTACT MESSAGE
# ============================================================

@router.post(
    "",
    response_model=ContactMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact_message(
    data: ContactMessageCreate,
    db: DBSession,
):
    contact_message = ContactMessage(
        name=data.name,
        email=data.email,
        message=data.message,
    )

    db.add(contact_message)

    db.commit()

    db.refresh(contact_message)

    return contact_message


# ============================================================
# GET ALL CONTACT MESSAGES
# ============================================================

@router.get(
    "",
    response_model=list[ContactMessageResponse],
)
def get_contact_messages(
    db: DBSession,
):
    statement = (
        select(ContactMessage)
        .order_by(ContactMessage.created_at.desc())
    )

    result = db.execute(statement)

    messages = result.scalars().all()

    return messages