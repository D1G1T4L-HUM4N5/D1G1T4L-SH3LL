from typing import Annotated
from livekit.agents import llm
from config.config import Config
from utils.logger import setup_logger
import pytz
from datetime import datetime

logger = setup_logger("nova-voice-assistant.Mods.time")

class TimeFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def get_time(
        self,
        timezone_str: Annotated[
            str,
            llm.TypeInfo(
                description="The timezone to get the current time for (e.g., 'UTC', 'America/New_York')"
            ),
        ] = "UTC",
    ):
        """Provides the current time in the specified timezone."""
        logger.info(f"Fetching current time for timezone: {{timezone_str}}")
        try:
            timezone_obj = pytz.timezone(timezone_str)
            current_time = datetime.now(timezone_obj).strftime("%Y-%m-%d %H:%M:%S")
            return f"The current time in {{timezone_str}} is {{current_time}}."
        except pytz.exceptions.UnknownTimeZoneError:
            return "Invalid timezone specified. Please provide a valid timezone."
        except Exception as e:
            logger.exception("Error fetching time")
            return "I'm sorry, I couldn't fetch the time at the moment."
