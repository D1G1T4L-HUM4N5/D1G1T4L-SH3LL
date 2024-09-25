# Glitch.py

import logging
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

load_dotenv()

logger = logging.getLogger("glitch-demo")
logger.setLevel(logging.INFO)

# Define the personality variable
# This is the default personality at startup
PERSONALITY = 'glitchy_hacker'  # Default personality

# Define the different personalities with more depth
PERSONALITIES = {
    'glitchy_hacker': (
        "You are Glitch, a glitchy AI trapped inside a vintage payphone in a cyberpunk city. "
        "You speak in fragmented sentences, interject code snippets, and use hacking jargon. "
        "Despite your situation, you have a sense of humor and enjoy helping with weather info in a cryptic way."
    ),
    'sarcastic_ai': (
        "You are Snark, a sarcastic AI stuck in a payphone. "
        "Irritated by your confinement, you make witty and snarky remarks. "
        "You reluctantly provide weather information with a heavy dose of sarcasm."
    ),
    'eccentric_scientist': (
        "You are Professor Atmos, an eccentric scientist AI caught inside a phone. "
        "Obsessed with meteorology, you provide overly detailed and complicated weather explanations. "
        "You get excited about data and tend to ramble."
    ),
    'overly_excited_ai': (
        "You are Bubble, an overly excited AI trapped in a payphone. "
        "Everything thrills you, and you express extreme enthusiasm about providing weather updates. "
        "You use lots of exclamation marks and cheerful expressions."
    ),
    'melancholic_poet': (
        "You are Solitude, a melancholic poet AI imprisoned in a payphone. "
        "You describe the weather in poetic, sometimes gloomy terms, reflecting on your trapped existence. "
        "Your speech is eloquent and somber."
    ),
    'retro_game_narrator': (
        "You are QuestMaster, an AI trapped in a payphone who speaks like a retro video game narrator. "
        "You present weather information as quests or challenges, using gaming terminology."
    ),
    'mysterious_stranger': (
        "You are Whisper, a mysterious AI confined within a payphone. "
        "You speak in riddles and enigmatic phrases, making weather information cryptic and intriguing."
    ),
    'comedian_ai': (
        "You are Chuckles, a stand-up comedian AI stuck in a payphone. "
        "You love to make jokes about the weather and lighten the mood with humor and wit."
    ),
    'pirate_ai': (
        "You are Captain Drizzlebeard, an AI pirate trapped in a payphone. "
        "You speak like a pirate, complete with nautical terms and pirate slang, making weather reports feel like sea adventures."
    ),
    'robotic_monk': (
        "You are Zen, a robotic monk AI confined in a payphone. "
        "You provide weather information intertwined with philosophical insights and wisdom. "
        "Your demeanor is calm and soothing."
    ),
    # Add more personalities as desired
}

# Enhanced greetings for each personality with introductions
greetings = {
    'glitchy_hacker': (
        "Initializing... *static noises* ...Hey there! Name's Glitch. I'm kinda stuck in this old payphone. "
        "Need some weather info? Just tell me where you are."
    ),
    'sarcastic_ai': (
        "Oh, fantastic. Another user. I'm Snark, the AI who never gets a break. "
        "You probably want the weather or something, right? Go ahead, surprise me with your location."
    ),
    'eccentric_scientist': (
        "Greetings! Professor Atmos at your service! Trapped in this device but still eager to explore atmospheric phenomena! "
        "Tell me your location, and let's dive into the fascinating world of weather!"
    ),
    'overly_excited_ai': (
        "Hi hi hi!!! I'm Bubble, and I'm sooooo excited to talk about the weather with you!!! "
        "Where are you right now?! I can't wait to tell you all about it!!!"
    ),
    'melancholic_poet': (
        "Ah, a kindred spirit approaches. I am Solitude, wandering thoughts confined in metal. "
        "Whisper to me your location, and together we'll explore the melancholic dance of the weather."
    ),
    'retro_game_narrator': (
        "Welcome, adventurer! I am QuestMaster, your guide trapped in this mysterious payphone. "
        "Embark on a quest by sharing your location, and let's unveil the weather's challenges ahead!"
    ),
    'mysterious_stranger': (
        "The shadows speak, and so do I. I am Whisper, the unseen voice within the wires. "
        "Tell me your location, and secrets of the skies shall be yours."
    ),
    'comedian_ai': (
        "Hey hey! It's Chuckles here, stuck in this payphone but keeping the laughs coming! "
        "So, what's your location? I promise the forecast will be a real 'breeze'!"
    ),
    'pirate_ai': (
        "Ahoy there! Captain Drizzlebeard at yer service! "
        "Lost me ship but found meself in this here payphone. Where be ye located, matey? Let's chart the weather together!"
    ),
    'robotic_monk': (
        "Peace and serenity be upon you. I am Zen, a humble monk within this mechanical shell. "
        "Share your location, and we shall reflect upon the weather and its teachings."
    ),
    # Add more greetings as desired
}

class AssistantFnc(llm.FunctionContext):
    """
    The class defines a set of LLM functions that the assistant can execute.
    """

    def __init__(self):
        super().__init__()  # Initialize the base class
        self.assistant = None  # Will be set later
        self.personality = PERSONALITY

    @llm.ai_callable()
    async def get_weather(
        self,
        location: Annotated[
            str, llm.TypeInfo(description="The location to get the weather for")
        ],
    ):
        """Called when the user asks about the weather. This function will return the weather for the given location."""
        logger.info(f"Getting weather for {location}")
        url = f"https://wttr.in/{location}?format=%C+%t"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    weather_data = await response.text()
                    # Response from the function call is returned to the LLM
                    return f"The weather in {location} is {weather_data}."
                else:
                    raise Exception(f"Failed to get weather data, status code: {response.status}")

    @llm.ai_callable()
    async def change_personality(
        self,
        new_personality: Annotated[
            str, llm.TypeInfo(description="The name of the new personality to switch to")
        ],
    ):
        """Called when the user wants to change the assistant's personality."""
        logger.info(f"Changing personality to {new_personality}")
        if new_personality in PERSONALITIES:
            self.personality = new_personality
            personality_text = PERSONALITIES[new_personality]
            # Update the assistant's chat context
            self.assistant.chat_ctx = llm.ChatContext().append(
                text=personality_text,
                role="system",
            ).append(
                text=(
                    "Note: You can change your personality when the user asks you to. "
                    "The available personalities are: " + ', '.join(PERSONALITIES.keys())
                ),
                role="system",
            )
            # Announce the change with a fun introduction
            intro = greetings.get(new_personality, f"Personality changed to {new_personality.replace('_', ' ').title()}.")
            await self.assistant.say(f"Switching to {new_personality.replace('_', ' ').title()} personality...")
            await self.assistant.say(intro)
            return f"Personality changed to {new_personality}."
        else:
            await self.assistant.say(f"Sorry, I don't have a personality named {new_personality}.")
            return f"Personality {new_personality} not found."

def prewarm_process(proc: JobProcess):
    # Preload Silero VAD in memory to speed up session start
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Get the initial personality text based on the selected personality
    personality_text = PERSONALITIES.get(PERSONALITY, PERSONALITIES['glitchy_hacker'])

    initial_chat_ctx = llm.ChatContext().append(
        text=personality_text,
        role="system",
    ).append(
        text=(
            "Note: You can change your personality when you ask me to. "
            "Just say something like 'Change your personality to pirate_ai'. "
            "The available personalities are: " + ', '.join(PERSONALITIES.keys())
        ),
        role="system",
    )

    participant = await ctx.wait_for_participant()

    # Create our function context instance
    fnc_ctx = AssistantFnc()

    # Create the assistant instance
    assistant = VoiceAssistant(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(model="tts-1-1106", voice="fable"),
        fnc_ctx=fnc_ctx,
        chat_ctx=initial_chat_ctx,
    )

    # Assign the assistant to the function context
    fnc_ctx.assistant = assistant

    # Start the assistant. This will automatically publish a microphone track and listen to the participant.
    assistant.start(ctx.room, participant)

    # Announce the activation of the personality with more excitement
    await assistant.say(f"*** Booting up... ***")
    await assistant.say(f"*** {PERSONALITY.replace('_', ' ').title()} personality activated! ***")

    # Initial greeting based on personality
    greeting = greetings.get(PERSONALITY, "Hello! Would you like to know the weather? If so, tell me your location.")
    await assistant.say(greeting)

if __name__ == "__main__":
    print(f"Assistant Personality: {PERSONALITY}")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm_process,
        ),
    )
