from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from agents.weather_agent import WeatherAgentError, weather_agent
from api.dependencies import get_current_user
from models.user import User
from schemas.weather import WeatherResponse


router = APIRouter(
    prefix="/weather",
    tags=["Weather Agent"],
)


@router.get("/current", response_model=WeatherResponse)
async def current_weather(
    city: Annotated[
        str,
        Query(min_length=2, max_length=100),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> WeatherResponse:
    try:
        return await weather_agent.get_current_weather(city)
    except WeatherAgentError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error