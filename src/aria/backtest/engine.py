from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from aria.agent.trader import AdaptiveTrader, MarketSnapshot, TradeSignal
from aria.portfolio.models import Portfolio
from aria.risk.metrics import compute_risk_metrics


@dataclass(frozen=True)
class BacktestResult:
    equity_curve: list[float]
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float


class BacktestEngine:
    def __init__(self, initial_capital: float = 100_000.0) -> None:
        if initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        self.initial_capital = initial_capital

    def run(self, snapshots: Sequence[MarketSnapshot], strategy: AdaptiveTrader | Callable[[MarketSnapshot], TradeSignal]) -> BacktestResult:
        portfolio = Portfolio(cash=self.initial_capital)
        equity_curve = [float(self.initial_capital)]
        closed_trades = 0
        wins = 0
        latest_prices: dict[str, float] = {}

        for snapshot in snapshots:
            latest_prices[snapshot.symbol] = snapshot.price
            if callable(strategy):
                signal = strategy(snapshot)
            else:
                signal = strategy.decide(snapshot)

            if signal.action == "buy":
                position_value = portfolio.cash * 0.25
                quantity = position_value / max(snapshot.price, 1e-9)
                portfolio.cash -= position_value
                portfolio.add_position(snapshot.symbol, quantity, snapshot.price)
            elif signal.action == "sell":
                position = portfolio.positions.get(snapshot.symbol)
                if position is not None:
                    entry_price = position.avg_price
                    sell_quantity = position.quantity
                    proceeds = sell_quantity * snapshot.price
                    portfolio.cash += proceeds
                    portfolio.remove_position(snapshot.symbol, sell_quantity)
                    closed_trades += 1
                    if snapshot.price > entry_price:
                        wins += 1

            current_equity = portfolio.total_equity(latest_prices)
            equity_curve.append(current_equity)

        final_equity = equity_curve[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        holdings = {
            symbol: position.market_value(latest_prices[symbol])
            for symbol, position in portfolio.positions.items()
            if symbol in latest_prices
        }
        risk = compute_risk_metrics(
            equity_curve,
            holdings=holdings,
            total_equity=final_equity,
        )
        win_rate = wins / closed_trades if closed_trades else 0.0

        return BacktestResult(
            equity_curve=equity_curve,
            total_return=total_return,
            max_drawdown=risk.max_drawdown,
            sharpe_ratio=risk.sharpe_ratio,
            win_rate=win_rate,
        )
