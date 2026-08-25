from aria.agent.trader import MarketSnapshot
from aria.runtime.agent_runtime import AgentRuntime


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
