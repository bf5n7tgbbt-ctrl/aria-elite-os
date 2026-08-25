from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from aria.agent.trader import TradeSignal
from aria.portfolio.models import Portfolio


@dataclass(frozen=True)
class TradeOrder:
    symbol: str
    action: str
    quantity: float
    price: float
    executed_at: str
    rationale: str


@dataclass
class ExecutionJournal:
    orders: list[TradeOrder] = field(default_factory=list)

    def record(self, order: TradeOrder) -> None:
        self.orders.append(order)

    def recent(self, limit: int = 5) -> list[TradeOrder]:
        return self.orders[-limit:]


class ExecutionEngine:
    """Executes simulated trades and records their outcome in a journal."""

    def __init__(self, journal: ExecutionJournal | None = None) -> None:
        self.journal = journal or ExecutionJournal()

    def execute(self, signal: TradeSignal, portfolio: Portfolio, price: float) -> TradeOrder | None:
        if signal.action == "hold":
            return None

        if signal.action == "buy":
            notional = min(portfolio.cash, portfolio.cash * 0.25)
            quantity = notional / max(price, 1e-9)
            portfolio.cash -= notional
            portfolio.add_position(signal.symbol, quantity, price)
        elif signal.action == "sell":
            position = portfolio.positions.get(signal.symbol)
            if position is None:
                return None
            quantity = position.quantity
            proceeds = quantity * price
            portfolio.cash += proceeds
            portfolio.remove_position(signal.symbol, quantity)
        else:
            return None

        order = TradeOrder(
            symbol=signal.symbol,
            action=signal.action,
            quantity=quantity,
            price=price,
            executed_at=datetime.now(UTC).isoformat(),
            rationale=signal.reason,
        )
        self.journal.record(order)
        return order
