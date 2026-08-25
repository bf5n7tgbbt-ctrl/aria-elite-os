import pytest

from aria.agent.trader import MarketSnapshot
from aria.runtime.agent_runtime import AgentRuntime
from unittest.mock import Mock


def test_runtime_loop_generates_report() -> None:
    runtime = AgentRuntime(capital=100_000.0)
    snapshot = MarketSnapshot(
        symbol="AAPL",
        price=210.0,
        previous_close=200.0,
        volume=1_500_000,
        volatility=0.018,
        trend=1.2,
        sentiment=0.75,
    )

    report = runtime.run_cycle(
        snapshot,
        expected_returns={"AAPL": 0.12},
        risk_scores={"AAPL": 0.2},
    )

    assert report.phase == "monitoring"
    assert report.portfolio_value >= 100_000.0
    assert report.signal in {"buy", "sell", "hold"}
    assert isinstance(report.actions, list)


def test_runtime_requires_positive_capital() -> None:
    with pytest.raises(ValueError, match="Capital"):
        AgentRuntime(capital=0.0)


def test_runtime_loop_records_realized_return_when_position_is_sold() -> None:
    runtime = AgentRuntime(capital=100_000.0)
    runtime.run_cycle(
        MarketSnapshot("AAPL", 200.0, 190.0, 1_500_000, 0.018, 1.2, 0.75),
        expected_returns={"AAPL": 0.12},
        risk_scores={"AAPL": 0.2},
    )

    report = runtime.run_cycle(
        MarketSnapshot("AAPL", 220.0, 230.0, 1_500_000, 0.018, -1.0, -0.5),
        expected_returns={"AAPL": 0.12},
        risk_scores={"AAPL": 0.2},
    )

    assert report.signal == "sell"
    assert report.actions == ["sell"]
    assert runtime.memory.average_return_for("AAPL", "sell") == 0.1


def test_runtime_loop_uses_market_equity_for_signal_generation() -> None:
    runtime = AgentRuntime(capital=100_000.0)
    runtime.portfolio.add_position("AAPL", quantity=10.0, price=100.0)
    advance = Mock(side_effect=runtime.orchestrator.advance)
    runtime.orchestrator.advance = advance

    runtime.run_cycle(MarketSnapshot("AAPL", 110.0, 110.0, 1_000_000, 0.01, 0.0))

    assert advance.call_args_list[0].kwargs["portfolio_equity"] == 101_100.0


def test_runtime_loop_passes_position_weights_to_optimizer() -> None:
    runtime = AgentRuntime(capital=100_000.0)
    runtime.portfolio.add_position("AAPL", quantity=10.0, price=100.0)
    optimize = Mock(return_value=[])
    runtime.optimizer.optimize = optimize

    runtime.run_cycle(MarketSnapshot("AAPL", 110.0, 110.0, 1_000_000, 0.01, 0.0))

    assert optimize.call_args.args[0] == {"AAPL": 1_100.0 / 101_100.0}


def test_runtime_loop_preserves_explicit_empty_optimizer_inputs() -> None:
    runtime = AgentRuntime(capital=100_000.0)
    runtime.portfolio.add_position("AAPL", quantity=10.0, price=100.0)
    optimize = Mock(return_value=[])
    runtime.optimizer.optimize = optimize

    runtime.run_cycle(
        MarketSnapshot("AAPL", 110.0, 110.0, 1_000_000, 0.01, 0.0),
        expected_returns={},
        risk_scores={},
    )

    assert optimize.call_args.args[1] == {}
    assert optimize.call_args.args[2] == {}


def test_runtime_loop_keeps_latest_prices_for_other_positions() -> None:
    runtime = AgentRuntime(capital=100_000.0)
    runtime.portfolio.add_position("MSFT", quantity=10.0, price=100.0)
    runtime.latest_prices["MSFT"] = 120.0

    report = runtime.run_cycle(
        MarketSnapshot("AAPL", 110.0, 110.0, 1_000_000, 0.01, 0.0),
        expected_returns={},
        risk_scores={},
    )

    assert report.portfolio_value == 101_200.0
