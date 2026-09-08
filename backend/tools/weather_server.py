import httpx
from mcp.server.mcpserver import MCPServer

from schemas.weather import WeatherResponse


mcp = MCPServer("AI Farming Weather")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail",
}


@mcp.tool()
async def get_weather(city: str) -> WeatherResponse:
    """Get current weather conditions for a city."""

    city = city.strip()

    if len(city) < 2:
        raise ValueError("City must contain at least two characters")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            geocoding_response = await client.get(
                GEOCODING_URL,
                params={
                    "name": city,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
            )
            geocoding_response.raise_for_status()

            locations = geocoding_response.json().get("results", [])

            if not locations:
                raise ValueError(f"No location found for '{city}'")

            location = locations[0]

            weather_response = await client.get(
                FORECAST_URL,
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "apparent_temperature,"
                        "precipitation,"
                        "weather_code,"
                        "wind_speed_10m"
                    ),
                    "timezone": "auto",
                },
            )
            weather_response.raise_for_status()

    except httpx.HTTPError as error:
        raise RuntimeError(
            "The weather provider is currently unavailable"
        ) from error

    weather_data = weather_response.json()
    current = weather_data.get("current")

    if current is None:
        raise RuntimeError("Weather provider returned no current conditions")

    weather_code = int(current["weather_code"])

    return WeatherResponse(
        location=location["name"],
        country=location.get("country", "Unknown"),
        latitude=float(location["latitude"]),
        longitude=float(location["longitude"]),
        timezone=weather_data.get("timezone", "Unknown"),
        observed_at=current["time"],
        temperature_c=float(current["temperature_2m"]),
        apparent_temperature_c=float(
            current["apparent_temperature"]
        ),
        humidity_percent=int(current["relative_humidity_2m"]),
        precipitation_mm=float(current["precipitation"]),
        weather_code=weather_code,
        condition=WEATHER_CODES.get(
            weather_code,
            "Unknown weather condition",
        ),
        wind_speed_kmh=float(current["wind_speed_10m"]),
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")