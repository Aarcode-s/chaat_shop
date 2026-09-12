from fastapi import APIRouter, HTTPException, status

from app.auth import create_access_token, verify_password
from app.config import settings
from app.schemas.auth_schemas import AdminLogin, TokenResponse

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def admin_login(
    data: AdminLogin,
):
    if data.username != settings.admin_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(
        data.password,
        settings.admin_password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data.username
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )