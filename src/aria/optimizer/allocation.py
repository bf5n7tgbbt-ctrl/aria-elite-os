from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AllocationDecision:
    symbol: str
    target_weight: float
    current_weight: float
    adjustment: float
    reason: str


class PortfolioOptimizer:
    """Rebalances allocations using expected return, risk budget and signal quality."""

    def __init__(self, risk_budget: float = 0.02, max_weight: float = 0.30) -> None:
        self.risk_budget = risk_budget
        self.max_weight = max_weight

    def optimize(self, positions: dict[str, float], expected_returns: dict[str, float], risk_scores: dict[str, float], total_equity: float) -> list[AllocationDecision]:
        if total_equity <= 0:
            return []

        decisions: list[AllocationDecision] = []
        for symbol, current_weight in positions.items():
            expected_return = expected_returns.get(symbol, 0.0)
            risk_score = risk_scores.get(symbol, 0.5)
            target_weight = max(0.0, min(self.max_weight, (expected_return + 0.05) / max(risk_score + 0.5, 0.1)))
            if current_weight > target_weight:
                reason = "Reduce allocation due to lower expected return or higher risk."
            else:
                reason = "Increase allocation to capture stronger expected signal."
            adjustment = target_weight - current_weight
            decisions.append(
                AllocationDecision(
                    symbol=symbol,
                    target_weight=target_weight,
                    current_weight=current_weight,
                    adjustment=adjustment,
                    reason=reason,
                )
            )
        return decisions
