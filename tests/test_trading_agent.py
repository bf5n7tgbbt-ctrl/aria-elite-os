import pytest

from aria.agent.trader import AdaptiveTrader, MarketSnapshot
from aria.simulation.market import MarketSimulator


def test_adaptive_trader_identifies_bullish_opportunity() -> None:
    snapshot = MarketSnapshot(
        symbol="AAPL",
        price=210.0,
        previous_close=200.0,
        volume=1_500_000,
        volatility=0.018,
        trend=1.2,
        sentiment=0.75,
    )

    trader = AdaptiveTrader(capital=100_000.0)
    decision = trader.evaluate(snapshot)

    assert decision.signal.action == "buy"
    assert decision.signal.confidence > 0.0
    assert decision.position_size > 0.0


def test_adaptive_trader_requires_positive_capital() -> None:
    with pytest.raises(ValueError, match="Capital"):
        AdaptiveTrader(capital=0.0)


def test_market_simulator_generates_price_path() -> None:
    simulator = MarketSimulator(seed=42)
    path = simulator.simulate(100.0, steps=10, drift=0.001, volatility=0.02)

    assert len(path) == 11
    assert path[0] == 100.0
    assert all(value > 0 for value in path)


def test_market_simulator_keeps_prices_positive_after_extreme_shock() -> None:
    class FixedShock:
        def gauss(self, drift: float, volatility: float) -> float:
            return -1.1

    simulator = MarketSimulator()
    simulator.generator = FixedShock()

    path = simulator.simulate(100.0, steps=1, volatility=0.1)

    assert all(price > 0 for price in path)


def test_adaptive_trader_avoids_trade_when_conditions_are_weak() -> None:
    snapshot = MarketSnapshot(
        symbol="MSFT",
        price=101.0,
        previous_close=100.0,
        volume=650_000,
        volatility=0.09,
        trend=0.15,
        sentiment=0.1,
    )

    trader = AdaptiveTrader()
    decision = trader.evaluate(snapshot)

    assert decision.signal.action == "hold"
    assert decision.signal.expected_return == 0.0


def test_market_simulator_rejects_invalid_market_parameters() -> None:
    simulator = MarketSimulator(seed=42)

    with pytest.raises(ValueError, match="price"):
        simulator.simulate(0.0)
    with pytest.raises(ValueError, match="Volatility"):
        simulator.simulate(100.0, volatility=-0.01)
