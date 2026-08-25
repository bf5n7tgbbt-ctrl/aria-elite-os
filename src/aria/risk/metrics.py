from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class RiskMetrics:
    volatility: float
    max_drawdown: float
    concentration: float
    exposure_ratio: float
    sharpe_ratio: float


def compute_risk_metrics(equity_curve: list[float], holdings: dict[str, float] | None = None, total_equity: float | None = None) -> RiskMetrics:
    if len(equity_curve) < 2:
        return RiskMetrics(0.0, 0.0, 0.0, 0.0, 0.0)

    returns = []
    for previous, current in zip(equity_curve, equity_curve[1:]):
        if previous == 0:
            returns.append(0.0)
        else:
            returns.append((current - previous) / previous)

    if not returns:
        return RiskMetrics(0.0, 0.0, 0.0, 0.0, 0.0)

    mean_return = sum(returns) / len(returns)
    variance = sum((value - mean_return) ** 2 for value in returns) / len(returns)
    volatility = sqrt(variance) if variance > 0 else 0.0
    peak = equity_curve[0]
    max_drawdown = 0.0
    for value in equity_curve:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak if peak else 0.0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    holding_total = sum(abs(amount) for amount in (holdings or {}).values()) if holdings else 0.0
    equity_base = total_equity if total_equity is not None and total_equity > 0 else max(sum(equity_curve), 1.0)
    concentration = max((abs(value) / holding_total) for value in (holdings or {}).values()) if holdings and holding_total else 0.0
    exposure_ratio = (holding_total / equity_base) if holding_total and equity_base else 0.0
    sharpe_ratio = (mean_return / volatility) if volatility > 0 else 0.0

    return RiskMetrics(
        volatility=volatility,
        max_drawdown=max_drawdown,
        concentration=concentration,
        exposure_ratio=exposure_ratio,
        sharpe_ratio=sharpe_ratio,
    )
