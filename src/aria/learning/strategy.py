from __future__ import annotations

from aria.agent.trader import MarketSnapshot, TradeSignal
from aria.learning.memory import ExperienceMemory


class AdaptiveLearningStrategy:
    """Adjusts a raw market signal using the agent's historical performance."""

    def __init__(self, memory: ExperienceMemory | None = None) -> None:
        self.memory = memory or ExperienceMemory()

    def refine(self, snapshot: MarketSnapshot, signal: TradeSignal) -> TradeSignal:
        bias = self.memory.confidence_bias(snapshot.symbol)
        adjusted_confidence = max(0.0, min(1.0, signal.confidence + bias * 0.4))
        adjusted_expected_return = signal.expected_return + bias * 0.2

        if signal.action == "buy" and bias < -0.05:
            action = "hold"
            adjusted_expected_return = 0.0
        elif signal.action == "sell" and bias > 0.05:
            action = "hold"
            adjusted_expected_return = 0.0
        else:
            action = signal.action

        return TradeSignal(
            symbol=signal.symbol,
            action=action,
            confidence=adjusted_confidence,
            expected_return=adjusted_expected_return,
            risk_score=signal.risk_score,
            reason=f"{signal.reason} Memory-adjusted bias: {bias:.3f}.",
        )
