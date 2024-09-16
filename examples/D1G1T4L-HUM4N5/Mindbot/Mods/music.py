from typing import Annotated
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
        """Simulates playing the specified song."""
        logger.info(f"Playing music: {{song_name}}")
        # Placeholder implementation
        # Integrate with a music service API like Spotify or YouTube if needed
        return f"Now playing '{{song_name}}'. (This is a simulation.)"
