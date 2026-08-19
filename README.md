# Agentic Trading System

Agentic Trading System is a small prototype that fetches Indian market news, and agents recommends stocks ,compute the movements and execute orders
**Note:The Work is under progress right now.**

## Features
- Fetches news from an API (async) via `NewsDataFeed`.
- Naive keyword-based company/symbol matching against `nifty100.csv`.
- Agent listens and recommend the stocks.
- CLI entrypoint that prints top-N recommended stocks.

## Requirements
- Python >= 3.13
- See `pyproject.toml` for pinned dependencies (`aiohttp`, `load-dotenv`, etc.).

## Installation
Install in editable mode for development:

```bash
pip install -e .
```

Or install normally:

```bash
pip install .
```

## Configuration
Create a `.envrc` file at the project root (or set environment variables) and add:

```
INDIAN_STOCK_MARKET_API_KEY=your_api_key_here
```

The project looks for `.envrc` using the helper in `agentic_trading_system.config`.

## Running
Run the packaged CLI (installed via `pyproject.toml` script) or the module directly:

```bash
# If installed as a script
agentic-trading-system

# Or run the package module
python -m agentic_trading_system
```

By default the entrypoint prints the top 10 recommendations. Pass a different
`top_n` by editing the `main()` call in `src/agentic_trading_system/__init__.py` or
calling the underlying function in code.

## Testing with Sample Data
If you don't have an API key, there is a sample feed JSON at
`src/agentic_trading_system/data/sample_feed/indian_news_api.json` that mimics the
API response shape. To test locally, you can temporarily modify
`NewsDataFeed.get_news_data()` to load and return that JSON.

## Project Structure

- `src/agentic_trading_system/agent/news_agent.py` — core agent: fetch, score, match.
- `src/agentic_trading_system/data/news_feed.py` — async news data feed implementation.
- `src/agentic_trading_system/nifty100.csv` — company & symbol mapping used for matching.
- `pyproject.toml` — project metadata and dependencies.

## Development
- Run static checks and formatting via your preferred tools. Dev dependencies include
	`mypy` and `pre-commit` (see `pyproject.toml`).

## Notes & Limitations
- This is a prototype: Right now working on creating stock recommending agent There is no backtesting or
	trading execution in this repository.
---
