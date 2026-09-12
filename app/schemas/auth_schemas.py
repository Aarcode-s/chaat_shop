

from pydantic import BaseModel

# -------------------------
# Authentication schemas
# -------------------------


class AdminLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"