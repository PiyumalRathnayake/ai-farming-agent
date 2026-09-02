from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from models.forecast_history import ForecastHistory
from models.user import User
from schemas.forecast_history import (
    ForecastHistoryCreate,
    ForecastHistoryRead,
    ForecastHistoryUpdate,
)
from services.crud import (
    create_record,
    delete_record,
    get_record_or_404,
    list_records,
    update_record,
)

router = APIRouter(prefix="/forecast-history", tags=["Forecast History"])


@router.post(
    "", response_model=ForecastHistoryRead, status_code=status.HTTP_201_CREATED
)
async def create_forecast_history(
    payload: ForecastHistoryCreate,
    db: AsyncSession = Depends(get_db),
) -> ForecastHistory:
    await get_record_or_404(db, User, payload.user_id)
    return await create_record(db, ForecastHistory, payload.model_dump())


@router.get("", response_model=list[ForecastHistoryRead])
async def read_forecast_histories(
    db: AsyncSession = Depends(get_db),
) -> list[ForecastHistory]:
    return await list_records(db, ForecastHistory)


@router.get("/{history_id}", response_model=ForecastHistoryRead)
async def read_forecast_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
) -> ForecastHistory:
    return await get_record_or_404(db, ForecastHistory, history_id)


@router.put("/{history_id}", response_model=ForecastHistoryRead)
async def update_forecast_history(
    history_id: int,
    payload: ForecastHistoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> ForecastHistory:
    history = await get_record_or_404(db, ForecastHistory, history_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)

    if "user_id" in changes:
        await get_record_or_404(db, User, changes["user_id"])

    return await update_record(db, history, changes)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    history = await get_record_or_404(db, ForecastHistory, history_id)
    await delete_record(db, history)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
