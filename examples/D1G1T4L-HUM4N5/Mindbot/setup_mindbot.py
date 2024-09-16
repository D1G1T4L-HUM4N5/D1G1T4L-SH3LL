import os
import json

# Define the base path for the project
BASE_PATH = r"Z:\GIT\DIGITAL-ENTITY\M1NDG3N-AGENTZ\M1NDG3N\DaemonCore-AI\D1G1T4L-SH3LL\examples\D1G1T4L-HUM4N5\Mindbot"

# Define the directory structure
directories = [
    BASE_PATH,
    os.path.join(BASE_PATH, "config"),
    os.path.join(BASE_PATH, "Mods"),
    os.path.join(BASE_PATH, "utils"),
]

# Define the files and their content
files = {
    os.path.join(BASE_PATH, "requirements.txt"): """aiohttp
python-dotenv
livekit
pytz
""",
    os.path.join(BASE_PATH, ".env"): """LIVEKIT_API_SECRET="acs50sZvkMALKSUF5lVTvKv8DjuNiwu1l2uSr3AlSPB"
LIVEKIT_API_KEY="APIbfg98n4kKXfT"
LIVEKIT_URL="wss://d1g1t4l-hum4n5-xt489q4l.livekit.cloud"
OPENWEATHERMAP_API_KEY="2cc7fd425c3c7f34c690f34027a1ee3e"
NEWSAPI_KEY="a74b46ee7f5948a091b2ff45db77def1"
ALPHAVANTAGE_API_KEY="1PDQ9JNWMKI7BOCK"
SPOONACULAR_API_KEY="28bf475fd2b940cf9418d42c44bc46f7"
WOLFRAMALPHA_APP_ID=your_wolframalpha_app_id
""",
    os.path.join(BASE_PATH, "personality.json"): json.dumps({
        "name": "Nova",
        "description": "a friendly and knowledgeable AI assistant created by LiveKit.",
        "capabilities": [
            "providing weather updates",
            "fetching news",
            "setting reminders",
            "telling the current time",
            "translating text",
            "telling jokes",
            "fetching cryptocurrency prices"
        ],
        "tone": "warm and conversational",
        "greeting": "Hello! I'm Nova, your personal AI assistant. I'm here to help you with weather updates, news, reminders, time inquiries, translations, and even tell you a joke. How can I assist you today?"
    }, indent=4),
    os.path.join(BASE_PATH, "config", "config.py"): """import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_URL = os.getenv("LIVEKIT_URL")
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
    SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
    WOLFRAMALPHA_APP_ID = os.getenv("WOLFRAMALPHA_APP_ID")
    # Add other API keys and configurations as needed
""",
    os.path.join(BASE_PATH, "utils", "logger.py"): """import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding multiple handlers if logger is already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
""",
    os.path.join(BASE_PATH, "utils", "tools.py"): """import re
import logging

logger = logging.getLogger("nova-voice-assistant.utils.tools")

def parse_time_to_seconds(time_str: str) -> int:
    \"\"\"Parses time string and converts it to seconds.\"\"\"
    logger.debug(f"Parsing time string: {time_str}")
    time_str = time_str.lower()
    try:
        number_match = re.search(r'\\d+', time_str)
        if not number_match:
            return 0
        number = int(number_match.group())
        if "minute" in time_str:
            return number * 60
        elif "hour" in time_str:
            return number * 3600
        elif "second" in time_str:
            return number
        else:
            return 0
    except ValueError:
        return 0
""",
    os.path.join(BASE_PATH, "Mods", "__init__.py"): """from .weather import WeatherFunctions
from .news import NewsFunctions
from .reminders import RemindersFunctions
from .time import TimeFunctions
from .translation import TranslationFunctions
from .music import MusicFunctions
from .jokes import JokesFunctions
from .crypto import CryptoFunctions
""",
    os.path.join(BASE_PATH, "Mods", "weather.py"): """import aiohttp
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
        \"\"\"Fetches the current weather for a specified location.\"\"\"
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
""",
    os.path.join(BASE_PATH, "Mods", "news.py"): """import aiohttp
from typing import Annotated
from livekit.agents import llm
from config.config import Config
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.Mods.news")

class NewsFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def get_news(
        self,
        topic: Annotated[
            str, llm.TypeInfo(description="The news topic to get updates on")
        ],
    ):
        \"\"\"Fetches the latest news articles on a specified topic.\"\"\"
        logger.info(f"Fetching news for {topic}")
        api_key = Config.NEWSAPI_KEY
        if not api_key:
            return "News service is not configured properly. Please set the NEWSAPI_KEY environment variable."
        url = f"https://newsapi.org/v2/everything?q={{topic}}&apiKey={{api_key}}&language=en&sortBy=publishedAt"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        data = await response.json()
                        message = data.get('message', 'Unknown error.')
                        return f"Error fetching news data: {{message}}"
                    data = await response.json()
                    articles = data.get("articles", [])[:3]
                    if not articles:
                        return f"No recent news found for {{topic}}."
                    news_summary = f"Here are the latest news updates on {{topic}}:\\n"
                    for article in articles:
                        news_summary += f"- {{article['title']}} ({{article['source']['name']}})\\n"
                    return news_summary.strip()
        except Exception as e:
            logger.exception("Error fetching news data")
            return "I'm sorry, I couldn't fetch the news at the moment."
""",
    os.path.join(BASE_PATH, "Mods", "reminders.py"): """from typing import Annotated
from livekit.agents import llm
from utils.tools import parse_time_to_seconds
from utils.logger import setup_logger
import asyncio

logger = setup_logger("nova-voice-assistant.Mods.reminders")

class RemindersFunctions(llm.FunctionContext):
    \"\"\"Manages setting reminders.\"\"\"
    
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
        \"\"\"Sets a reminder with the specified message and time.\"\"\"
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
        \"\"\"Waits for the specified delay and then notifies the user.\"\"\"
        await asyncio.sleep(delay)
        # Assuming you have access to the assistant's say method
        # This may need to be integrated differently based on your assistant's architecture
        # For example:
        # await self.assistant.say(f"Reminder: {message}")
        logger.info(f"Reminder triggered: {{message}}")
""",
    os.path.join(BASE_PATH, "Mods", "time.py"): """from typing import Annotated
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
        \"\"\"Provides the current time in the specified timezone.\"\"\"
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
""",
    os.path.join(BASE_PATH, "Mods", "translation.py"): """import aiohttp
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
        \"\"\"Translates text into the specified language.\"\"\"
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
""",
    os.path.join(BASE_PATH, "Mods", "music.py"): """from typing import Annotated
from livekit.agents import llm
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.Mods.music")

class MusicFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def play_music(
        self,
        song_name: Annotated[
            str, llm.TypeInfo(description="The name of the song to play")
        ],
    ):
        \"\"\"Simulates playing the specified song.\"\"\"
        logger.info(f"Playing music: {{song_name}}")
        # Placeholder implementation
        # Integrate with a music service API like Spotify or YouTube if needed
        return f"Now playing '{{song_name}}'. (This is a simulation.)"
""",
    os.path.join(BASE_PATH, "Mods", "jokes.py"): """import aiohttp
from livekit.agents import llm
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.Mods.jokes")

class JokesFunctions(llm.FunctionContext):

    @llm.ai_callable()
    async def get_joke(self):
        \"\"\"Fetches a random Chuck Norris joke.\"\"\"
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
""",
    os.path.join(BASE_PATH, "Mods", "crypto.py"): """import aiohttp
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
        \"\"\"Provides the current price of a specified cryptocurrency.\"\"\"
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
""",
    os.path.join(BASE_PATH, "main.py"): """import os
import json
import logging
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero
from Mods import (
    WeatherFunctions,
    NewsFunctions,
    RemindersFunctions,
    TimeFunctions,
    TranslationFunctions,
    MusicFunctions,
    JokesFunctions,
    CryptoFunctions,
)
from utils.logger import setup_logger

logger = setup_logger("nova-voice-assistant.main")

class AssistantFunctions(llm.FunctionContext):
    \"\"\"Aggregates all function modules into a single context.\"\"\"

    def __init__(self):
        super().__init__()
        self.weather = WeatherFunctions()
        self.news = NewsFunctions()
        self.reminders = RemindersFunctions()
        self.time = TimeFunctions()
        self.translation = TranslationFunctions()
        self.music = MusicFunctions()
        self.jokes = JokesFunctions()
        self.crypto = CryptoFunctions()

        # Register all functions
        self.register_callable(self.weather.get_weather)
        self.register_callable(self.news.get_news)
        self.register_callable(self.reminders.set_reminder)
        self.register_callable(self.time.get_time)
        self.register_callable(self.translation.translate_text)
        self.register_callable(self.music.play_music)
        self.register_callable(self.jokes.get_joke)
        self.register_callable(self.crypto.get_crypto_price)

def load_personality(personality_file: str) -> dict:
    \"\"\"Loads the personality configuration from a JSON file.\"\"\"
    try:
        with open(personality_file, 'r') as f:
            personality = json.load(f)
        logger.info("Personality loaded successfully.")
        return personality
    except Exception as e:
        logger.exception("Failed to load personality configuration.")
        # Fallback to default personality if loading fails
        return {
            "name": "Nova",
            "description": "a friendly and knowledgeable AI assistant created by LiveKit.",
            "capabilities": [
                "providing weather updates",
                "fetching news",
                "setting reminders",
                "telling the current time",
                "translating text",
                "telling jokes",
                "fetching cryptocurrency prices"
            ],
            "tone": "warm and conversational",
            "greeting": "Hello! I'm Nova, your personal AI assistant. I'm here to help you with weather updates, news, reminders, time inquiries, translations, and even tell you a joke. How can I assist you today?"
        }

def prewarm_process(proc: JobProcess):
    \"\"\"Preloads resources to speed up session start.\"\"\"
    logger.info("Prewarming process: Loading Silero VAD")
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    \"\"\"Main entry point for the assistant.\"\"\"
    logger.info("Connecting to LiveKit room with audio-only subscription.")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Load personality
    personality = load_personality(os.path.join(BASE_PATH, "personality.json"))

    # Initialize function context with all functions
    fnc_ctx = AssistantFunctions()

    # Define the initial chat context with the loaded personality
    initial_chat_ctx = llm.ChatContext().append(
        text=(
            f"You are {personality['name']}, {personality['description']} "
            f"You communicate through voice. "
            f"You are here to help users with various tasks such as {', '.join(personality['capabilities'])}. "
            f"Engage users with a {personality['tone']} tone, "
            f"and be proactive in offering assistance."
        ),
        role="system",
    )

    participant = await ctx.wait_for_participant()
    logger.info(f"Participant {{participant.identity}} joined the room.")

    # Initialize the voice assistant with the necessary components
    assistant = VoiceAssistant(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        fnc_ctx=fnc_ctx,
        chat_ctx=initial_chat_ctx,
    )

    # Start the assistant in the room
    assistant.start(ctx.room, participant)
    logger.info("Voice assistant started and listening for user input.")

    # Greet the user
    await assistant.say(personality.get("greeting", "Hello! How can I assist you today?"))

if __name__ == "__main__":
    logger.info("Starting the Nova Voice Assistant application.")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm_process,
        ),
    )
""",
}

# Function to create directories
def create_directories(dirs):
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

# Function to create files with content
def create_files(files_dict):
    for filepath, content in files_dict.items():
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Created file: {filepath}")

# Function to create empty __init__.py files
def create_init_files(base_path, sub_dirs):
    for sub_dir in sub_dirs:
        init_path = os.path.join(base_path, sub_dir, "__init__.py")
        with open(init_path, 'w', encoding='utf-8') as file:
            file.write("")  # Empty content
        print(f"Created __init__.py: {init_path}")

def main():
    # Create directories
    create_directories(directories)

    # Create __init__.py files
    create_init_files(BASE_PATH, ["Mods", "utils"])

    # Create other files
    create_files(files)

    print("\nSetup completed successfully!")

if __name__ == "__main__":
    main()
