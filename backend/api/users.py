from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import hash_password

from database.session import get_db
from models.user import User
from schemas.user import UserCreate, UserRead, UserUpdate
from services.crud import (
    create_record,
    delete_record,
    get_record_or_404,
    list_records,
    update_record,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    values = payload.model_dump(exclude={"password"})
    values["email"] = str(payload.email).lower()
    values["hashed_password"] = hash_password(payload.password)

    existing = await db.scalar(select(User).where(User.email == values["email"]))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    try:
        return await create_record(db, User, values)
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        ) from error


@router.get("", response_model=list[UserRead])
async def read_users(db: AsyncSession = Depends(get_db)) -> list[User]:
    return await list_records(db, User)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await get_record_or_404(db, User, user_id)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await get_record_or_404(db, User, user_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    password = changes.pop("password", None)
    if password:
        changes["hashed_password"] = hash_password(password)
    if "email" in changes:
        changes["email"] = str(changes["email"]).lower()
        duplicate = await db.scalar(
            select(User).where(
                User.email == changes["email"],
                User.id != user_id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

    return await update_record(db, user, changes)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    user = await get_record_or_404(db, User, user_id)
    await delete_record(db, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
