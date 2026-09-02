from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


async def create_record(
    db: AsyncSession,
    model: type[ModelType],
    values: dict[str, Any],
) -> ModelType:
    record = model(**values)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def list_records(
    db: AsyncSession,
    model: type[ModelType],
) -> list[ModelType]:
    statement = select(model).order_by(getattr(model, "id"))
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_record_or_404(
    db: AsyncSession,
    model: type[ModelType],
    record_id: int,
) -> ModelType:
    record = await db.get(model, record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} not found",
        )
    return record


async def update_record(
    db: AsyncSession,
    record: ModelType,
    changes: dict[str, Any],
) -> ModelType:
    for field, value in changes.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)
    return record


async def delete_record(db: AsyncSession, record: ModelType) -> None:
    await db.delete(record)
    await db.commit()
