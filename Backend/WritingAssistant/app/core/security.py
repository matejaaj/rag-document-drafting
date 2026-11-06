from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.core.exceptions import AuthError


class CurrentUser(BaseModel):

    id: int
    email: Optional[str] = None
    role: Optional[str] = None


async def get_current_user_id(request: Request) -> int:
    user_id = request.headers.get("X-USER-ID")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nisi prijavljen",
        )
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Neispravan identitet korisnika",
        )


async def get_current_user(request: Request) -> CurrentUser:
    return CurrentUser(
        id=await get_current_user_id(request),
        email=request.headers.get("X-EMAIL"),
        role=request.headers.get("X-USER-ROLE"),
    )


async def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "ADMIN":
        raise AuthError(detail="Samo admin ima pristup")
    return user
