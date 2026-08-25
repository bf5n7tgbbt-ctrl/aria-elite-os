import pytest

from aria.agent.trader import AdaptiveTrader, MarketSnapshot, TradeSignal
from aria.execution.executor import ExecutionEngine
from aria.learning.memory import ExperienceMemory, ExperienceRecord
from aria.learning.strategy import AdaptiveLearningStrategy
from aria.portfolio.models import Portfolio


def test_experience_memory_tracks_symbol_outcomes() -> None:
    memory = ExperienceMemory()
    memory.add(ExperienceRecord("AAPL", "buy", 0.02, 0.08, 0.75, {"source": "history"}))
    memory.add(ExperienceRecord("AAPL", "buy", 0.01, 0.03, 0.65, {"source": "history"}))

    assert memory.average_return_for("AAPL", "buy") > 0.0
    assert memory.confidence_bias("AAPL") > 0.0


def test_learning_strategy_adjusts_signal_after_positive_feedback() -> None:
    memory = ExperienceMemory()
    memory.add(ExperienceRecord("NVDA", "buy", 0.04, 0.12, 0.9, {"source": "feedback"}))

    strategy = AdaptiveLearningStrategy(memory)
    raw_signal = TradeSignal(
        symbol="NVDA",
        action="buy",
        confidence=0.4,
        expected_return=0.02,
        risk_score=0.3,
        reason="Momentum is consistent",
    )
    snapshot = MarketSnapshot("NVDA", 120.0, 100.0, 1_000_000, 0.02, 1.0, 0.7)

    refined = strategy.refine(snapshot, raw_signal)

    assert refined.action == "buy"
    assert refined.confidence > raw_signal.confidence


def test_execution_engine_records_simulated_trade() -> None:
    portfolio = Portfolio(cash=100_000.0)
    engine = ExecutionEngine()
    signal = TradeSignal(
        symbol="MSFT",
        action="buy",
        confidence=0.9,
        expected_return=0.07,
        risk_score=0.2,
        reason="Strong breakout",
    )

    order = engine.execute(signal, portfolio, 250.0)

    assert order is not None
    assert order.action == "buy"
    assert len(engine.journal.orders) == 1
    assert portfolio.cash < 100_000.0


def test_execution_engine_rejects_non_positive_prices() -> None:
    portfolio = Portfolio(cash=100_000.0)
    engine = ExecutionEngine()
    signal = TradeSignal("MSFT", "buy", 0.9, 0.07, 0.2, "Strong breakout")

    with pytest.raises(ValueError, match="price"):
        engine.execute(signal, portfolio, 0.0)
