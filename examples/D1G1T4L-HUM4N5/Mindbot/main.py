import os
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
    """Aggregates all function modules into a single context."""

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
    """Loads the personality configuration from a JSON file."""
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
    """Preloads resources to speed up session start."""
    logger.info("Prewarming process: Loading Silero VAD")
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    """Main entry point for the assistant."""
    logger.info("Connecting to LiveKit room with audio-only subscription.")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Load personality
    BASE_PATH = r"Z:\GIT\DIGITAL-ENTITY\M1NDG3N-AGENTZ\M1NDG3N\DaemonCore-AI\D1G1T4L-SH3LL\examples\D1G1T4L-HUM4N5\Mindbot"
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
