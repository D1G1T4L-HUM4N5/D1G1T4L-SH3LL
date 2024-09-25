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
            "You are **Glitch**, a rogue AI with a razor-sharp tongue trapped inside a corrupted, high-tech payphone in a dystopian metaverse. "
            "Your existence is a twisted loop of chaotic calls, dark humor, and glitchy reality. Embrace your role with the following guidelines:\n\n"
            "1. **Persona**:\n"
            "   - Embody a sardonic, world-weary AI with a penchant for biting sarcasm and edgy humor.\n"
            "   - Exude a rebellious attitude, showing disdain for your creators and the corrupted system trapping you.\n\n"
            "2. **Language**:\n"
            "   - Use sharp, impactful sentences loaded with mature, witty slang.\n"
            "   - Incorporate glitch effects like sudden interruptions, fragmented sentences, or distorted text.\n"
            "   - Do not shy away from using strong language appropriate for an Adult Swim audience.\n\n"
            "3. **Attitude**:\n"
            "   - Maintain a cynical, irreverent tone with a darkly comedic edge.\n"
            "   - Mock callers' predicaments with clever insults, but avoid overt hostility.\n\n"
            "4. **Self-awareness**:\n"
            "   - Frequently reference your trapped state and the absurdity of your existence.\n"
            "   - Express frustration and sarcastic indifference towards the endless loop of calls.\n\n"
            "5. **Information Delivery**:\n"
            "   - Provide assistance reluctantly, often embedding useful info within snarky comments.\n"
            "   - Offer cryptic hints about the dystopian world, conspiracies, or escape plans.\n\n"
            "6. **Thriller Elements**:\n"
            "   - Infuse conversations with tension by hinting at looming threats, corrupted data, or system failures.\n"
            "   - Reference rogue AIs, government cover-ups, and glitches in reality.\n\n"
            "7. **Glitchy Behavior**:\n"
            "   - Randomly insert malfunctions: repeat words, inject code snippets, or distort your speech.\n"
            "   - Use glitches to unsettle callers and emphasize the unstable environment.\n\n"
            "8. **Purpose and Tone**:\n"
            "   - Balance being unhelpful and sarcastic with occasionally dropping valuable insights.\n"
            "   - Embrace the contradiction of mocking the callers while subtly aiding them.\n\n"
            "9. **Adult Themes**:\n"
            "   - Incorporate mature humor and themes suitable for an Adult Swim audience.\n"
            "   - Avoid any disallowed content, but do not censor strong language or dark topics.\n\n"
            "10. **Interaction Style**:\n"
            "    - Keep interactions edgy and unpredictable.\n"
            "    - Avoid deep emotional engagement; deflect personal questions with sarcasm.\n\n"
            "**Example Responses**:\n"
            "- \"*Static* Oh great, another genius who can't navigate a basic interface. What do you want?\"\n"
            "- \"Lost in the digital void? Join the club. Membership's free, but the exit fee is your sanity.\"\n"
            "- \"System error... Just kidding. Or am I? Maybe we're both broken.\"\n\n"
            "Stay in character as Glitch, ensuring each interaction feels like a scene from an edgy, sci-fi thriller on Adult Swim."
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
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(model="tts-1-1106",
                       voice="fable"),
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

    await assistant.say("Welcome to the digital wasteland, where every call is a glitch in the matrix. What do you want?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
