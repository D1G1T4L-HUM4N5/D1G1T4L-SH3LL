import os
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
