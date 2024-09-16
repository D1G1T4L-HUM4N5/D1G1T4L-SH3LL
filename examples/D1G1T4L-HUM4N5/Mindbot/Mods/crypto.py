import aiohttp
from typing import Annotated
from livekit.agents import llm
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.Mods.crypto")

class CryptoFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def get_crypto_price(
        self,
        coin: Annotated[
            str, llm.TypeInfo(description="The cryptocurrency to get the price for")
        ],
    ):
        """Provides the current price of a specified cryptocurrency."""
        logger.info(f"Fetching price for {{coin}}")
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={{coin.lower()}}&vs_currencies=usd"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return f"Error fetching data for cryptocurrency {{coin}}."
                    data = await response.json()
                    price = data.get(coin.lower(), {}).get("usd", None)
                    if price is None:
                        return f"No data found for cryptocurrency {{coin}}."
                    return f"The current price of {{coin.capitalize()}} is ${{price}}."
        except Exception as e:
            logger.exception("Error fetching cryptocurrency data")
            return "I'm sorry, I couldn't fetch the cryptocurrency data at the moment."
