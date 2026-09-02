from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ForecastHistoryCreate(BaseModel):
    user_id: int
    location: str = Field(min_length=1, max_length=150)
    forecast: str = Field(min_length=1)


class ForecastHistoryUpdate(BaseModel):
    user_id: int | None = None
    location: str | None = Field(default=None, min_length=1, max_length=150)
    forecast: str | None = Field(default=None, min_length=1)


class ForecastHistoryRead(BaseModel):
    id: int
    user_id: int
    location: str
    forecast: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
