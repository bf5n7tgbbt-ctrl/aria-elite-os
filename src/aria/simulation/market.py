from __future__ import annotations

import random


class MarketSimulator:
    """Generate realistic price paths to stress-test a trading thesis."""

    def __init__(self, seed: int | None = None) -> None:
        self.generator = random.Random(seed)

    def simulate(self, base_price: float, steps: int = 20, drift: float = 0.0008, volatility: float = 0.015) -> list[float]:
        if base_price <= 0:
            raise ValueError("Base price must be positive")
        if volatility < 0:
            raise ValueError("Volatility cannot be negative")
        if steps <= 0:
            return [float(base_price)]

        path = [float(base_price)]
        current_price = float(base_price)
        for _ in range(steps):
            shock = self.generator.gauss(drift, volatility)
            current_price *= max(1e-9, 1.0 + shock)
            path.append(float(current_price))
        return path


def simulate_price_path(base_price: float, steps: int = 20, drift: float = 0.0008, volatility: float = 0.015) -> list[float]:
    return MarketSimulator().simulate(base_price, steps=steps, drift=drift, volatility=volatility)
