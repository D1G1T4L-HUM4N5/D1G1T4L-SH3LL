import aiohttp
from typing import Annotated
from livekit.agents import llm
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.Mods.translation")

class TranslationFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def translate_text(
        self,
        text: Annotated[str, llm.TypeInfo(description="The text to translate")],
        target_language: Annotated[
            str, llm.TypeInfo(description="The language to translate the text into")
        ],
    ):
        """Translates text into the specified language."""
        logger.info(f"Translating text to {{target_language}}")
        url = "https://libretranslate.de/translate"
        try:
            payload = {
                'q': text,
                'source': 'auto',
                'target': target_language.lower(),
                'format': 'text'
            }
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload, headers=headers) as response:
                    if response.status != 200:
                        return "Error translating text."
                    data = await response.json()
                    translated_text = data.get("translatedText", "")
                    return f"Translated text: {{translated_text}}"
        except Exception as e:
            logger.exception("Error translating text")
            return "I'm sorry, I couldn't translate the text at the moment."
