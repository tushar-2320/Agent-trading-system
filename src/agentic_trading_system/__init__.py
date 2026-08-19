"""Package entrypoint for agentic_trading_system.

Provides a simple CLI entrypoint `main()` that runs the news->stock recommendation agent.
"""
from .news_agent import run_sync, analyze_and_recommend  # noqa: F401


def main() -> None:
    """Console entrypoint used by the package script defined in pyproject.toml.

    Running `agentic-trading-system` will execute this function.
    """
    # Default: top 10 recommendations
    run_sync(top_n=10)
