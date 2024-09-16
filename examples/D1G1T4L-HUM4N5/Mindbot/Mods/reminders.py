from typing import Annotated
from livekit.agents import llm
from utils.tools import parse_time_to_seconds
from utils.logger import setup_logger
import asyncio

logger = setup_logger("nova-voice-assistant.Mods.reminders")

class RemindersFunctions(llm.FunctionContext):
    """Manages setting reminders."""
    
    @llm.ai_callable()
    async def set_reminder(
        self,
        reminder_message: Annotated[
            str, llm.TypeInfo(description="The reminder message")
        ],
        reminder_time: Annotated[
            str,
            llm.TypeInfo(
                description="The time to set the reminder for (e.g., 'in 10 minutes')"
            ),
        ],
    ):
        """Sets a reminder with the specified message and time."""
        logger.info(f"Setting reminder: '{{reminder_message}}' at '{{reminder_time}}'")
        try:
            delay = parse_time_to_seconds(reminder_time)
            if delay > 0:
                # Schedule the reminder asynchronously
                asyncio.create_task(self._reminder_task(reminder_message, delay))
                return f"Reminder set for {{reminder_time}}: {{reminder_message}}."
            else:
                return "I'm sorry, I couldn't understand the time specified for the reminder."
        except Exception as e:
            logger.exception("Error setting reminder")
            return "I'm sorry, I couldn't set the reminder."

    async def _reminder_task(self, message: str, delay: int):
        """Waits for the specified delay and then notifies the user."""
        await asyncio.sleep(delay)
        # Assuming you have access to the assistant's say method
        # This may need to be integrated differently based on your assistant's architecture
        # For example:
        # await self.assistant.say(f"Reminder: {message}")
        logger.info(f"Reminder triggered: {{message}}")
