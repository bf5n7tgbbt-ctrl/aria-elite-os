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
