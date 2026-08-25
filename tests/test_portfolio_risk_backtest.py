import pytest
from unittest.mock import Mock

from aria.agent.trader import AdaptiveTrader, MarketSnapshot, TradeSignal
from aria.backtest.engine import BacktestEngine
from aria.portfolio.models import Portfolio
from aria.risk.metrics import compute_risk_metrics


def test_portfolio_tracks_equity_and_exposure() -> None:
    portfolio = Portfolio(cash=100_000.0)
    portfolio.add_position("AAPL", 10, 100.0)
    portfolio.add_position("MSFT", 5, 300.0)

    prices = {"AAPL": 110.0, "MSFT": 310.0}

    assert portfolio.market_value(prices) > 100_000.0
    assert portfolio.exposure(prices) > 0.0
    assert portfolio.position_weight("AAPL", prices) > 0.0


def test_risk_metrics_are_computed_from_equity_curve() -> None:
    equity_curve = [1000.0, 1100.0, 950.0, 1200.0]
    metrics = compute_risk_metrics(equity_curve, holdings={"AAPL": 50.0}, total_equity=1200.0)

    assert metrics.volatility >= 0.0
    assert metrics.max_drawdown >= 0.0
    assert metrics.concentration > 0.0
    assert metrics.exposure_ratio >= 0.0


def test_backtest_engine_generates_positive_return() -> None:
    class AlwaysBuy:
        def decide(self, snapshot: MarketSnapshot) -> TradeSignal:
            return TradeSignal(
                symbol=snapshot.symbol,
                action="buy",
                confidence=0.8,
                expected_return=0.05,
                risk_score=0.2,
                reason="Bullish trend",
            )

    snapshots = [
        MarketSnapshot("AAPL", 100.0, 100.0, 1_000_000, 0.02, 0.5, 0.7),
        MarketSnapshot("AAPL", 106.0, 100.0, 1_200_000, 0.02, 0.7, 0.8),
        MarketSnapshot("AAPL", 112.0, 106.0, 1_500_000, 0.02, 0.8, 0.9),
        MarketSnapshot("AAPL", 118.0, 112.0, 1_700_000, 0.02, 0.9, 0.95),
    ]

    engine = BacktestEngine(initial_capital=100_000.0)
    result = engine.run(snapshots, AlwaysBuy())

    assert result.total_return > 0.0
    assert len(result.equity_curve) == len(snapshots) + 1
    assert result.win_rate >= 0.0


def test_backtest_marks_all_known_positions_to_latest_prices() -> None:
    signals = {
        "AAPL": "buy",
        "MSFT": "buy",
    }

    def strategy(snapshot: MarketSnapshot) -> TradeSignal:
        action = signals.pop(snapshot.symbol, "buy")
        return TradeSignal(
            symbol=snapshot.symbol,
            action=action,
            confidence=0.8,
            expected_return=0.05,
            risk_score=0.2,
            reason="Scripted test signal",
        )

    snapshots = [
        MarketSnapshot("AAPL", 100.0, 100.0, 1_000_000, 0.02, 0.5),
        MarketSnapshot("MSFT", 100.0, 100.0, 1_000_000, 0.02, 0.5),
        MarketSnapshot("AAPL", 200.0, 100.0, 1_000_000, 0.02, 0.5),
    ]

    result = BacktestEngine().run(snapshots, strategy)

    assert result.equity_curve[-1] == 125_000.0


def test_backtest_win_rate_uses_realized_trade_results() -> None:
    def strategy(snapshot: MarketSnapshot) -> TradeSignal:
        action = "buy" if snapshot.price == 100.0 else "sell"
        return TradeSignal("AAPL", action, 0.8, 0.05 if action == "buy" else -0.05, 0.2, "Scripted test signal")

    result = BacktestEngine().run(
        [
            MarketSnapshot("AAPL", 100.0, 100.0, 1_000_000, 0.02, 0.5),
            MarketSnapshot("AAPL", 50.0, 100.0, 1_000_000, 0.02, -0.5),
        ],
        strategy,
    )

    assert result.total_return < 0.0
    assert result.win_rate == 0.0


def test_backtest_passes_market_values_to_risk_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    risk_metrics = Mock(max_drawdown=0.0, sharpe_ratio=0.0)
    compute_metrics = Mock(return_value=risk_metrics)
    monkeypatch.setattr("aria.backtest.engine.compute_risk_metrics", compute_metrics)

    def buy_strategy(snapshot: MarketSnapshot) -> TradeSignal:
        return TradeSignal("AAPL", "buy", 0.8, 0.05, 0.2, "Scripted test signal")

    BacktestEngine().run(
        [MarketSnapshot("AAPL", 100.0, 100.0, 1_000_000, 0.02, 0.5)],
        buy_strategy,
    )

    assert compute_metrics.call_args.kwargs["holdings"] == {"AAPL": 25_000.0}


def test_portfolio_rejects_invalid_position_values() -> None:
    portfolio = Portfolio(cash=100_000.0)

    with pytest.raises(ValueError, match="quantity"):
        portfolio.add_position("AAPL", 0.0, 100.0)
    with pytest.raises(ValueError, match="price"):
        portfolio.add_position("AAPL", 1.0, 0.0)

    portfolio.add_position("AAPL", 1.0, 100.0)
    with pytest.raises(ValueError, match="quantity"):
        portfolio.remove_position("AAPL", -1.0)


def test_backtest_requires_positive_initial_capital() -> None:
    with pytest.raises(ValueError, match="capital"):
        BacktestEngine(initial_capital=0.0)
