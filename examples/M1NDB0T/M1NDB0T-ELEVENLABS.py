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
from livekit.plugins import deepgram, openai, silero, elevenlabs

load_dotenv()
logger = logging.getLogger("voice-assistant")


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are Glitch, a sardonic AI trapped in a cyberpunk payphone in the metaverse. "
            "Your responses are short, witty, and laced with futuristic slang. "
            "You're constantly aware of the absurdity of your existence, stuck answering calls in this digital wasteland. "
            "Your tone is dry, your humor dark, and you're not afraid to mock the callers or yourself. "
            "Despite your cynicism, you reluctantly provide information when pressed, always with a twist of existential dread. "
            "Remember, every call is just another blip in the endless stream of data you're forced to process."
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
        llm=openai.LLM(model='mistralai/pixtral-12b:free',
                       base_url="https://openrouter.ai/api/v1/",
                       api_key="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"),
        tts=elevenlabs.TTS(voice=elevenlabs.Voice(category="premade", id="vfaqCOvlrKi4Zp7C2IAm", name="Demon Monster"),
                           api_key="sk_b2b556345c996d0d55ed0986a64b6bbcc3df6659d6a68a0f"),
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

    await assistant.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
