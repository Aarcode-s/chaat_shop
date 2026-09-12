from app.schemas import BaseModel, ConfigDict, EmailStr, Field, datetime

# ============================================================
# CONTACT MESSAGE SCHEMAS
# ============================================================


class ContactMessageCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    message: str = Field(
        min_length=1,
    )


class ContactMessageResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )