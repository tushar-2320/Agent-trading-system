import os
import sys

from dotenv import load_dotenv


def resource_path(relative_path: str) -> str:  # TODO: CHECK FOR PATH
    base_path: str = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


load_dotenv(
    dotenv_path=resource_path(".envrc"),
    verbose=True,
)


INDIAN_STOCK_MARKET_API_KEY = os.getenv("INDIAN_STOCK_MARKET_API_KEY")
