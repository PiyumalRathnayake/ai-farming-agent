from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatHistoryCreate(BaseModel):
    user_id: int
    message: str = Field(min_length=1)
    response: str = Field(min_length=1)


class ChatHistoryUpdate(BaseModel):
    user_id: int | None = None
    message: str | None = Field(default=None, min_length=1)
    response: str | None = Field(default=None, min_length=1)


class ChatHistoryRead(BaseModel):
    id: int
    user_id: int
    message: str
    response: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
