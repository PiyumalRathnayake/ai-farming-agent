from mcp import Client
from mcp.types import TextContent
from pydantic import ValidationError

from schemas.weather import WeatherResponse
from tools.weather_server import mcp as weather_mcp


class WeatherAgentError(RuntimeError):
    pass


class WeatherAgent:
    async def get_current_weather(
        self,
        city: str,
    ) -> WeatherResponse:
        async with Client(weather_mcp) as client:
            available_tools = await client.list_tools()
            tool_names = {tool.name for tool in available_tools.tools}

            if "get_weather" not in tool_names:
                raise WeatherAgentError(
                    "The MCP get_weather tool is unavailable"
                )

            result = await client.call_tool(
                "get_weather",
                {"city": city},
            )

            if result.is_error:
                message = next(
                    (
                        block.text
                        for block in result.content
                        if isinstance(block, TextContent)
                    ),
                    "Weather tool failed",
                )
                raise WeatherAgentError(message)

            if result.structured_content is None:
                raise WeatherAgentError(
                    "Weather tool returned no structured data"
                )

            try:
                return WeatherResponse.model_validate(
                    result.structured_content
                )
            except ValidationError as error:
                raise WeatherAgentError(
                    "Weather tool returned invalid data"
                ) from error


weather_agent = WeatherAgent()