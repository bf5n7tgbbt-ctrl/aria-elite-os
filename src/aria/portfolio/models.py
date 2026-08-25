from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Position:
    symbol: str
    quantity: float = 0.0
    avg_price: float = 0.0

    def market_value(self, price: float) -> float:
        return self.quantity * price

    def pnl(self, price: float) -> float:
        return (price - self.avg_price) * self.quantity

    def to_dict(self) -> dict[str, Any]:
        return {"symbol": self.symbol, "quantity": self.quantity, "avg_price": self.avg_price}


@dataclass
class Portfolio:
    cash: float = 100_000.0
    positions: dict[str, Position] = field(default_factory=dict)
    risk_budget: float = 0.02

    def add_position(self, symbol: str, quantity: float, price: float) -> Position:
        if symbol in self.positions:
            existing = self.positions[symbol]
            total_quantity = existing.quantity + quantity
            weighted_price = (existing.avg_price * existing.quantity + price * quantity) / max(total_quantity, 1e-9)
            existing.quantity = total_quantity
            existing.avg_price = weighted_price
            self.positions[symbol] = existing
            return existing

        position = Position(symbol=symbol, quantity=quantity, avg_price=price)
        self.positions[symbol] = position
        return position

    def remove_position(self, symbol: str, quantity: float) -> float:
        if symbol not in self.positions:
            return 0.0
        position = self.positions[symbol]
        sold = min(quantity, position.quantity)
        position.quantity -= sold
        if position.quantity <= 0:
            del self.positions[symbol]
        return sold

    def market_value(self, prices: dict[str, float]) -> float:
        return self.cash + sum(position.market_value(prices.get(position.symbol, 0.0)) for position in self.positions.values())

    def exposure(self, prices: dict[str, float]) -> float:
        return sum(abs(position.market_value(prices.get(position.symbol, 0.0))) for position in self.positions.values())

    def total_equity(self, prices: dict[str, float]) -> float:
        return self.market_value(prices)

    def position_weight(self, symbol: str, prices: dict[str, float]) -> float:
        total = self.total_equity(prices)
        if total <= 0:
            return 0.0
        position_value = self.positions.get(symbol, Position(symbol=symbol)).market_value(prices.get(symbol, 0.0))
        return abs(position_value) / total

    def snapshot(self, prices: dict[str, float]) -> dict[str, Any]:
        return {
            "cash": self.cash,
            "equity": self.total_equity(prices),
            "exposure": self.exposure(prices),
            "positions": {symbol: pos.to_dict() for symbol, pos in self.positions.items()},
        }
