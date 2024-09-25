# VortexAI.py

import json
import logging
import os
from typing import Annotated

import aiohttp
from dotenv import load_dotenv
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

# Load environment variables from .env file
load_dotenv()

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("VortexAI_debug.log"),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger("VortexAI")
logger.setLevel(logging.DEBUG)  # Capture all debug logs

# Determine the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the personalities.json file
PERSONALITIES_FILE = os.path.join(script_dir, 'personalities.json')

# Load personalities from JSON file
try:
    with open(PERSONALITIES_FILE, 'r', encoding='utf-8') as f:
        personality_data = json.load(f)
    logger.debug(f"Loaded personalities from '{PERSONALITIES_FILE}'.")
except FileNotFoundError:
    logger.error(f"Personalities JSON file '{PERSONALITIES_FILE}' not found. Please ensure it exists in the script directory.")
    exit(1)
except json.JSONDecodeError as e:
    logger.error(f"Error decoding JSON from '{PERSONALITIES_FILE}': {e}")
    exit(1)

PERSONALITIES = personality_data.get('personalities', {})
PERSONALITY = 'Glitch'  # Default personality

if PERSONALITY not in PERSONALITIES:
    logger.error(f"Default personality '{PERSONALITY}' not found in '{PERSONALITIES_FILE}'.")
    exit(1)

class AssistantFnc(llm.FunctionContext):
    """
    Defines the LLM functions that the assistant can execute.
    """

    def __init__(self):
        super().__init__()
        self.assistant = None  # To be set after initialization
        self.personality = PERSONALITY

    @llm.ai_callable()
    async def get_weather(
        self,
        location: Annotated[
            str, llm.TypeInfo(description="The location to get the weather for")
        ],
    ):
        """
        Fetches weather information for the specified location.
        """
        logger.debug(f"Function 'get_weather' called with location: {location}")
        url = f"https://wttr.in/{location}?format=%C+%t"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        weather_data = await response.text()
                        logger.debug(f"Weather data fetched successfully: {weather_data}")
                        return f"The weather in {location} is {weather_data}."
                    else:
                        logger.error(f"Failed to get weather data, status code: {response.status}")
                        raise Exception(f"Failed to get weather data, status code: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return "Sorry, I couldn't retrieve the weather information right now."

    @llm.ai_callable()
    async def change_personality(
        self,
        new_personality: Annotated[
            str, llm.TypeInfo(description="The name of the new personality to switch to")
        ],
    ):
        """
        Changes the assistant's personality to the specified one.
        """
        logger.debug(f"Function 'change_personality' called with new_personality: {new_personality}")
        if new_personality in PERSONALITIES:
            self.personality = new_personality
            personality_details = PERSONALITIES[new_personality]
            personality_text = personality_details.get('description', '')
            greeting = personality_details.get('greeting', 'Hello!')

            # Update the assistant's chat context with the new personality
            self.assistant.chat_ctx = llm.ChatContext().append(
                text=personality_text,
                role="system",
            ).append(
                text=(
                    "Note: You can change your personality by saying its name. "
                    "Available personalities are: " + ', '.join(PERSONALITIES.keys())
                ),
                role="system",
            )
            logger.debug(f"Updated chat context with personality: {new_personality}")

            # Announce the personality change and provide a new greeting
            await self.assistant.say(f"*** Switching to {new_personality} personality... ***")
            logger.debug(f"Announced personality change to '{new_personality}'.")
            await self.assistant.say(greeting)
            logger.debug(f"Sent greeting for '{new_personality}': {greeting}")
            logger.info(f"Personality changed to {new_personality}")
            return f"Personality changed to {new_personality}."
        else:
            logger.warning(f"Requested personality '{new_personality}' not found.")
            await self.assistant.say(f"Sorry, I don't recognize the personality '{new_personality}'.")
            return f"Personality '{new_personality}' not found."

    @llm.ai_callable()
    async def list_personalities(
        self
    ):
        """
        Lists all available personalities.
        """
        available = ', '.join(PERSONALITIES.keys())
        logger.debug("Function 'list_personalities' called.")
        await self.assistant.say(f"Available personalities are: {available}. Just say the name to switch.")
        logger.debug(f"Listed available personalities: {available}")
        return f"Available personalities: {available}."

def prewarm_process(proc: JobProcess):
    """
    Preloads necessary resources to speed up the session start.
    """
    logger.debug("Prewarming process: Loading Silero VAD...")
    try:
        vad = silero.VAD.load()
        proc.userdata["vad"] = vad
        logger.debug("Silero VAD loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading Silero VAD: {e}")

async def entrypoint(ctx: JobContext):
    """
    The main entry point for the assistant.
    """
    logger.debug("Entrypoint: Connecting with auto_subscribe=AUDIO_ONLY.")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    personality_text = PERSONALITIES[PERSONALITY].get('description', '')
    logger.debug(f"Initial personality description: {personality_text}")

    initial_chat_ctx = llm.ChatContext().append(
        text=personality_text,
        role="system",
    ).append(
        text=(
            "Note: You can change your personality by saying its name. "
            "Available personalities are: " + ', '.join(PERSONALITIES.keys())
        ),
        role="system",
    )
    logger.debug("Initial chat context set.")

    participant = await ctx.wait_for_participant()
    logger.debug(f"Participant connected: {participant}")

    # Create function context instance
    fnc_ctx = AssistantFnc()

    # Create the assistant instance
    assistant = VoiceAssistant(
        vad=ctx.proc.userdata.get("vad"),
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),  # Using a lightweight model
        tts=openai.TTS(voice="fable"),  # Ensure 'fable' is a valid voice
        fnc_ctx=fnc_ctx,
        chat_ctx=initial_chat_ctx,
    )
    logger.debug("VoiceAssistant instance created.")

    # Assign the assistant to the function context
    fnc_ctx.assistant = assistant
    logger.debug("Assistant assigned to function context.")

    # Start the assistant
    assistant.start(ctx.room, participant)
    logger.debug("Assistant started.")

    # Announce the activation of the personality with excitement
    await assistant.say("*** Booting up... ***")
    logger.debug("Announced booting up.")

    await assistant.say(f"*** {PERSONALITY} personality activated! ***")
    logger.debug(f"Announced personality activation: {PERSONALITY}")

    # Initial greeting based on personality
    greeting = PERSONALITIES[PERSONALITY].get('greeting', "Hello! How can I assist you today?")
    await assistant.say(greeting)
    logger.debug(f"Sent initial greeting: {greeting}")

if __name__ == "__main__":
    logger.info(f"Assistant Personality: {PERSONALITY}")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm_process,
        ),
    )
