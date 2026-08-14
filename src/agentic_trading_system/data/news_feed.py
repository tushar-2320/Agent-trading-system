import aiohttp

from agentic_trading_system.config import INDIAN_STOCK_MARKET_API_KEY


class NewsDataFeed:
    # Need to Add more relevant api
    @staticmethod
    async def get_news_data():
        api_key = INDIAN_STOCK_MARKET_API_KEY

        headers = {
            "x-api-key": api_key,
        }

        async with aiohttp.ClientSession() as session:
            response = await session.get("https://stock.indianapi.in/news",
                                         headers=headers)
            response.raise_for_status()
            return await response.json()
