import aiohttp
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
        """Fetches the latest news articles on a specified topic."""
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
                    news_summary = f"Here are the latest news updates on {{topic}}:\n"
                    for article in articles:
                        news_summary += f"- {{article['title']}} ({{article['source']['name']}})\n"
                    return news_summary.strip()
        except Exception as e:
            logger.exception("Error fetching news data")
            return "I'm sorry, I couldn't fetch the news at the moment."
