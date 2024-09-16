import aiohttp
from typing import Annotated
from livekit.agents import llm
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.Mods.weather")

class WeatherFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def get_weather(
        self,
        location: Annotated[
            str, llm.TypeInfo(description="The location to get the weather for")
        ],
    ):
        """Fetches the current weather for a specified location."""
        logger.info(f"Fetching weather for {location}")
        api_key = Config.OPENWEATHERMAP_API_KEY
        if not api_key:
            return "Weather service is not configured properly. Please set the OPENWEATHERMAP_API_KEY environment variable."
        url = f"http://api.openweathermap.org/data/2.5/weather?q={{location}}&appid={{api_key}}&units=metric"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        data = await response.json()
                        message = data.get('message', 'Unknown error.')
                        return f"Error fetching weather data: {{message}}"
                    data = await response.json()
                    weather = data["weather"][0]["description"]
                    temp = data["main"]["temp"]
                    report = f"The current weather in {{location}} is {{weather}} with a temperature of {{temp}} degrees Celsius."
                    return report
        except Exception as e:
            logger.exception("Error fetching weather data")
            return "I'm sorry, I couldn't fetch the weather data at the moment."
