from .agent.trader import AdaptiveTrader, MarketSnapshot, TradeDecision, TradeSignal
from .backtest.engine import BacktestEngine, BacktestResult
from .data.integration import (
    DataIntegrator,
    DataPipeline,
    SQLiteDataStore,
    fetch_json_rows,
    load_csv_rows,
    load_json_rows,
)
from .execution.executor import ExecutionEngine, ExecutionJournal, TradeOrder
from .learning.memory import ExperienceMemory, ExperienceRecord
from .learning.strategy import AdaptiveLearningStrategy
from .portfolio.models import Portfolio, Position
from .risk.metrics import RiskMetrics, compute_risk_metrics
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
    "Portfolio",
    "Position",
    "RiskMetrics",
    "compute_risk_metrics",
    "BacktestEngine",
    "BacktestResult",
    "ExecutionEngine",
    "ExecutionJournal",
    "TradeOrder",
    "ExperienceMemory",
    "ExperienceRecord",
    "AdaptiveLearningStrategy",
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
