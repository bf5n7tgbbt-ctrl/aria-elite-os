from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Literal


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    price: float
    previous_close: float
    volume: float
    volatility: float
    trend: float
    sentiment: float = 0.0

    @property
    def return_pct(self) -> float:
        if isclose(self.previous_close, 0.0):
            return 0.0
        return (self.price - self.previous_close) / self.previous_close


@dataclass(frozen=True)
class TradeSignal:
    symbol: str
    action: Literal["buy", "sell", "hold"]
    confidence: float
    expected_return: float
    risk_score: float
    reason: str


@dataclass(frozen=True)
class TradeDecision:
    signal: TradeSignal
    position_size: float
    estimated_max_loss: float


class AdaptiveTrader:
    """Lightweight adaptive trading engine using price trend, sentiment and volatility."""

    def __init__(self, capital: float = 100_000.0, max_position_size: float = 0.25, risk_per_trade: float = 0.02) -> None:
        if capital <= 0:
            raise ValueError("Capital must be positive")
        self.capital = capital
        self.max_position_size = max_position_size
        self.risk_per_trade = risk_per_trade

    def _score_opportunity(self, snapshot: MarketSnapshot) -> float:
        momentum = snapshot.return_pct * 8.0
        trend_bias = snapshot.trend * 2.0
        sentiment_bias = snapshot.sentiment * 3.0
        volatility_penalty = snapshot.volatility * 6.0
        return momentum + trend_bias + sentiment_bias - volatility_penalty

    def _build_signal(self, snapshot: MarketSnapshot) -> TradeSignal:
        score = self._score_opportunity(snapshot)
        absolute_score = abs(score)
        confidence = max(0.0, min(1.0, absolute_score / 3.0))
        risk_score = min(1.0, snapshot.volatility * 2.0)

        if score >= 0.75:
            action = "buy"
            expected_return = snapshot.return_pct + (snapshot.sentiment * 0.05)
            reason = "Bullish momentum with positive sentiment and controlled volatility."
        elif score <= -0.75:
            action = "sell"
            expected_return = -(abs(snapshot.return_pct) + abs(snapshot.sentiment) * 0.05)
            reason = "Bearish setup with weak sentiment and elevated downside risk."
        else:
            action = "hold"
            expected_return = 0.0
            reason = "Momentum not strong enough to justify a trade under current constraints."

        return TradeSignal(
            symbol=snapshot.symbol,
            action=action,
            confidence=confidence,
            expected_return=expected_return,
            risk_score=risk_score,
            reason=reason,
        )

    def evaluate(self, snapshot: MarketSnapshot) -> TradeDecision:
        signal = self._build_signal(snapshot)
        max_risk_amount = self.capital * self.risk_per_trade
        position_size = min(self.capital * self.max_position_size, max_risk_amount / max(snapshot.volatility, 0.01))
        estimated_max_loss = max_risk_amount * (1.0 + signal.risk_score)

        return TradeDecision(
            signal=signal,
            position_size=position_size,
            estimated_max_loss=estimated_max_loss,
        )

    def decide(self, snapshot: MarketSnapshot) -> TradeSignal:
        return self._build_signal(snapshot)
