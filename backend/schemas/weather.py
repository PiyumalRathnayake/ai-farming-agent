from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    location: str
    country: str
    latitude: float
    longitude: float
    timezone: str
    observed_at: str

    temperature_c: float = Field(description="Temperature in Celsius")
    apparent_temperature_c: float
    humidity_percent: int
    precipitation_mm: float
    weather_code: int
    condition: str
    wind_speed_kmh: float