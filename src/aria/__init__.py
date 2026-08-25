from .agent.trader import AdaptiveTrader, MarketSnapshot, TradeDecision, TradeSignal
from .data.integration import (
    DataIntegrator,
    DataPipeline,
    SQLiteDataStore,
    fetch_json_rows,
    load_csv_rows,
    load_json_rows,
)
from .simulation.market import MarketSimulator, simulate_price_path

__version__ = "0.1.0"


def hello() -> str:
    """Return a simple greeting used by the demo test."""
    return "Hello, Aria!"


__all__ = [
    "hello",
    "__version__",
    "AdaptiveTrader",
    "MarketSnapshot",
    "TradeSignal",
    "TradeDecision",
    "DataIntegrator",
    "DataPipeline",
    "SQLiteDataStore",
    "MarketSimulator",
    "simulate_price_path",
    "fetch_json_rows",
    "load_csv_rows",
    "load_json_rows",
]


if __name__ == "__main__":
    print(hello())
