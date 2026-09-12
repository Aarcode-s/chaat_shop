from typing import Annotated

from fastapi import Depends

from app.auth import get_current_admin

AdminVerify = Annotated[str, Depends(get_current_admin)]