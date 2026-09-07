from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_access_token
from database.session import get_db
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)

        if payload.get("type") != "access":
            raise credentials_error

        subject = payload.get("sub")
        if subject is None:
            raise credentials_error

        user_id = int(subject)
    except (InvalidTokenError, TypeError, ValueError) as error:
        raise credentials_error from error

    user = await db.get(User, user_id)

    if user is None or not user.is_active:
        raise credentials_error

    return user