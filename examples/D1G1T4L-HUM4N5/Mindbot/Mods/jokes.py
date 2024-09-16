import aiohttp
from livekit.agents import llm
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.Mods.jokes")

class JokesFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def get_joke(self):
        """Fetches a random Chuck Norris joke."""
        logger.info("Fetching a joke")
        url = "https://api.chucknorris.io/jokes/random"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return "Error fetching joke."
                    data = await response.json()
                    joke = data.get("value", "")
                    return f"Here's a joke: {{joke}}"
        except Exception as e:
            logger.exception("Error fetching joke")
            return "I'm sorry, I couldn't fetch a joke at the moment."
