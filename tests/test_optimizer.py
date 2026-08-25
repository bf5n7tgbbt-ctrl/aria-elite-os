from aria.optimizer.allocation import PortfolioOptimizer


def test_portfolio_optimizer_generates_weight_adjustments() -> None:
    optimizer = PortfolioOptimizer(risk_budget=0.02, max_weight=0.30)
    positions = {"AAPL": 0.10, "MSFT": 0.15, "NVDA": 0.05}
    expected_returns = {"AAPL": 0.12, "MSFT": 0.08, "NVDA": 0.15}
    risk_scores = {"AAPL": 0.35, "MSFT": 0.28, "NVDA": 0.22}

    decisions = optimizer.optimize(positions, expected_returns, risk_scores, total_equity=100_000.0)

    assert len(decisions) == 3
    assert decisions[0].symbol == "AAPL"
    assert decisions[0].target_weight >= 0.0
    assert decisions[0].adjustment != 0.0 or decisions[2].adjustment != 0.0
