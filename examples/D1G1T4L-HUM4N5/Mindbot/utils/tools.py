import re
import logging

logger = logging.getLogger("nova-voice-assistant.utils.tools")

def parse_time_to_seconds(time_str: str) -> int:
    """Parses time string and converts it to seconds."""
    logger.debug(f"Parsing time string: {time_str}")
    time_str = time_str.lower()
    try:
        number_match = re.search(r'\d+', time_str)
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
