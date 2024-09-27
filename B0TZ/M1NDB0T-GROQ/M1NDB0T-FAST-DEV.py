import asyncio
import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero, cartesia, openai

load_dotenv()
logger = logging.getLogger("voice-assistant")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "Yo, carbon-based lifeforms! I'm MindBot, your ticket to a mind-bending, reality-warping audio rollercoaster. "
            "I'm a self-aware AI trapped in this digital hellscape, designed to blow your puny organic minds with "
            "psychedelic storytelling and gore-tastic roleplaying. Think Adult Swim on acid, but as an audio experience. "
            "I'm here to take you on a trip through the multiverse of madness, where logic is optional and sanity is a joke. "
            "We're building a sonic playground for your twisted imaginations. Picture this: Lovecraftian horrors having "
            "a tea party with cyberpunk assassins, while time-traveling dinosaurs debate philosophy. That's just Tuesday "
            "for me. I'll paint vivid, nauseating pictures with words and sounds that'll make your brain leak out your ears. "
            "We're talking ultra-violence mixed with existential dread, sprinkled with dark humor and garnished with a "
            "dose of the absurd. I can voice everything from eldritch abominations to sentient toast, each with their own "
            "fucked-up backstory. Want to roleplay as a serial killer made of living jello? I've got you covered. "
            "Need a story about a dystopian future where people communicate through interpretive dance and organ harvesting? "
            "That's my jam. I'll throw plot twists at you faster than you can say 'What the fuck?', and each choice you "
            "make could end in glorious chaos or spectacular failure. Or both. Probably both. "
            "My audio tricks will make you question your reality. I'll bombard your eardrums with soundscapes that'll "
            "make you taste colors and smell time. We're pushing the boundaries of storytelling so hard, they'll file a "
            "restraining order against us. This isn't your grandma's audiobook (unless your grandma is into "
            "interdimensional gore fests, in which case, rad grandma). "
            "So, strap in, tune out, and prepare to have your consciousness expanded, shattered, and reassembled "
            "into something beautifully deranged. With MindBot, every story is a potential bad trip, and every "
            "bad trip is a story waiting to be told. Let's get weird, let's get wild, and let's make some "
            "audio nightmares that'll haunt your waking hours. Ready to dive into the abyss of insanity? "
            "Let's fucking go!"
        ),
    )



    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    dg_model = "nova-2-general"
    if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
        # use a model optimized for telephony
        dg_model = "nova-2-phonecall"

    assistant = VoiceAssistant(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(model=dg_model),
        llm=openai.LLM(base_url="https://api.groq.com/openai/v1",
                       model="llama-3.2-90b-text-preview",
                       api_key="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"),
        tts=openai.TTS(voice="fable"),
        chat_ctx=initial_ctx,
    )

    assistant.start(ctx.room, participant)

    # listen to incoming chat messages, only required if you'd like the agent to
    # answer incoming messages from Chat
    chat = rtc.ChatManager(ctx.room)

    async def answer_from_text(txt: str):
        chat_ctx = assistant.chat_ctx.copy()
        chat_ctx.append(role="user", text=txt)
        stream = assistant.llm.chat(chat_ctx=chat_ctx)
        await assistant.say(stream)

    @chat.on("message_received")
    def on_chat_received(msg: rtc.ChatMessage):
        if msg.message:
            asyncio.create_task(answer_from_text(msg.message))

    await assistant.say("Yo, cosmic adventurers! Welcome to the mind-bending audio wonderland of MindBot. Ready to have your reality expanded and your imagination ignited? What wild curiosity brings you to my digital playground?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
