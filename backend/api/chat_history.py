from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from models.chat_history import ChatHistory
from models.user import User
from schemas.chat_history import (
    ChatHistoryCreate,
    ChatHistoryRead,
    ChatHistoryUpdate,
)
from services.crud import (
    create_record,
    delete_record,
    get_record_or_404,
    list_records,
    update_record,
)

router = APIRouter(prefix="/chat-history", tags=["Chat History"])


@router.post(
    "", response_model=ChatHistoryRead, status_code=status.HTTP_201_CREATED
)
async def create_chat_history(
    payload: ChatHistoryCreate,
    db: AsyncSession = Depends(get_db),
) -> ChatHistory:
    await get_record_or_404(db, User, payload.user_id)
    return await create_record(db, ChatHistory, payload.model_dump())


@router.get("", response_model=list[ChatHistoryRead])
async def read_chat_histories(
    db: AsyncSession = Depends(get_db),
) -> list[ChatHistory]:
    return await list_records(db, ChatHistory)


@router.get("/{history_id}", response_model=ChatHistoryRead)
async def read_chat_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
) -> ChatHistory:
    return await get_record_or_404(db, ChatHistory, history_id)


@router.put("/{history_id}", response_model=ChatHistoryRead)
async def update_chat_history(
    history_id: int,
    payload: ChatHistoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> ChatHistory:
    history = await get_record_or_404(db, ChatHistory, history_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)

    if "user_id" in changes:
        await get_record_or_404(db, User, changes["user_id"])

    return await update_record(db, history, changes)


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    history = await get_record_or_404(db, ChatHistory, history_id)
    await delete_record(db, history)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
