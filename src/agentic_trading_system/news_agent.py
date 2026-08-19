"""news_agent

Simple agent to fetch current news and recommend stocks based on naive keyword matching
and a lightweight sentiment heuristic.

Usage:
    - Set INDIAN_STOCK_MARKET_API_KEY in .envrc to allow existing news feed to work
    - Run: python -m agentic_trading_system  # or use the package script

Notes:
    - This implementation uses the existing NewsDataFeed (async) in data/news_feed.py.
    - Sentiment is a small rule-based scorer (no heavy ML dependencies).
    - The agent matches company names and symbols from nifty100.csv to tag news items.

"""
from __future__ import annotations

import asyncio
import csv
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

import aiohttp

from .config import resource_path
from .data.news_feed import NewsDataFeed


@dataclass
class StockSentiment:
    symbol: str
    company: str
    count: int = 0
    sentiment_score: float = 0.0


POSITIVE_WORDS = {
    "beat",
    "beats",
    "beat expectations",
    "record",
    "gain",
    "gained",
    "growth",
    "upgrade",
    "raised",
    "appoint",
    "profit",
    "surge",
    "soar",
    "strong",
    "positive",
}

NEGATIVE_WORDS = {
    "miss",
    "missed",
    "downgrade",
    "cut",
    "loss",
    "losses",
    "fall",
    "fell",
    "drop",
    "weak",
    "decline",
    "negative",
    "lawsuit",
    "probe",
}


def load_nifty_mapping(csv_path: str) -> Dict[str, str]:
    """Load mapping from company name -> symbol and symbol -> company"""
    mapping: Dict[str, str] = {}
    if not os.path.exists(csv_path):
        return mapping
    with open(csv_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = (row.get("Company Name") or row.get("Company Name", "")).strip()
            symbol = (row.get("Symbol") or row.get("Symbol", "")).strip()
            if name:
                mapping[name.lower()] = symbol
            if symbol:
                mapping[symbol.lower()] = symbol
    return mapping


def score_text_sentiment(text: str) -> float:
    """Naive sentiment: +1 per positive word, -1 per negative word, normalized by length."""
    if not text:
        return 0.0
    t = text.lower()
    score = 0
    for w in POSITIVE_WORDS:
        if w in t:
            score += 1
    for w in NEGATIVE_WORDS:
        if w in t:
            score -= 1
    # normalize by number of words to reduce bias from long text
    words = len(t.split())
    if words == 0:
        return float(score)
    return score / min(words, 20)  # cap divisor to avoid tiny numbers


async def fetch_news() -> List[dict]:
    """Wrapper around existing NewsDataFeed.get_news_data() to return a list of news items.

    Expect the feed to return either a list or dict with keys like 'data' or 'news'.
    """
    try:
        data = await NewsDataFeed.get_news_data()
    except aiohttp.ClientError as exc:
        raise RuntimeError(f"Failed to fetch news feed: {exc}")

    # attempt to extract list of items from common shapes
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("data", "news", "articles", "payload"):
            if k in data and isinstance(data[k], list):
                return data[k]
        # If dict is a single news item, wrap it
        return [data]
    return []


def match_item_to_symbols(item: dict, mapping: Dict[str, str]) -> List[str]:
    """Return list of matched symbols for a news item by checking title/content for company names or symbols."""
    text = " ".join(str(item.get(k, "")) for k in ("title", "description", "content", "summary"))
    t = text.lower()
    matched = set()
    # Simple matching: check each company name or symbol presence
    for key, symbol in mapping.items():
        if key in t:
            matched.add(symbol)
    return list(matched)


async def analyze_and_recommend(top_n: int = 10) -> List[Tuple[str, str, int, float]]:
    """Fetch news, compute sentiment per stock, and return top recommended stocks as tuples:
    (symbol, company, mentions, avg_sentiment_score)
    """
    csv_path = resource_path("src/agentic_trading_system/nifty100.csv")
    mapping = load_nifty_mapping(csv_path)

    # reverse mapping symbol->company for nice output
    symbol_to_company: Dict[str, str] = {}
    # try to populate symbol_to_company by reading the csv again
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                symbol = row.get("Symbol", "").strip()
                company = row.get("Company Name", "").strip()
                if symbol:
                    symbol_to_company[symbol] = company

    items = await fetch_news()
    if not items:
        return []

    stats: Dict[str, StockSentiment] = {}

    for item in items:
        text = " ".join(str(item.get(k, "")) for k in ("title", "description", "content", "summary"))
        s = score_text_sentiment(text)
        matched_symbols = match_item_to_symbols(item, mapping)
        # if no symbol matched, try to look for direct mentions of known symbols (simple heuristic)
        if not matched_symbols:
            # check for any symbols as standalone tokens
            text_tokens = set(text.lower().split())
            for token in text_tokens:
                if token.upper() in symbol_to_company:
                    matched_symbols.append(token.upper())
        for symbol in matched_symbols:
            company = symbol_to_company.get(symbol, "")
            if symbol not in stats:
                stats[symbol] = StockSentiment(symbol=symbol, company=company)
            stats[symbol].count += 1
            stats[symbol].sentiment_score += s

    # compute average sentiment per symbol
    scored = []
    for sym, st in stats.items():
        avg = st.sentiment_score / st.count if st.count else 0.0
        scored.append((sym, st.company, st.count, avg))

    # sort by a combined key: mention count and avg sentiment (weighted)
    scored.sort(key=lambda x: (x[2], x[3]), reverse=True)

    return scored[:top_n]


def format_recommendations(recs: List[Tuple[str, str, int, float]]) -> str:
    if not recs:
        return "No recommendations — no news items found or failed to fetch feed."
    lines = ["Top stock recommendations based on current news:\n"]
    for symbol, company, mentions, avg in recs:
        lines.append(f"{symbol} — {company or 'Unknown Company'} | mentions: {mentions} | avg_sentiment: {avg:.3f}")
    return "\n".join(lines)


def run_sync(top_n: int = 10) -> None:
    recs = asyncio.run(analyze_and_recommend(top_n=top_n))
    print(format_recommendations(recs))


if __name__ == "__main__":
    run_sync()
