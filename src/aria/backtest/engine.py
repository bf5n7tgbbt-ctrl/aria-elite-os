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
        self.initial_capital = initial_capital

    def run(self, snapshots: Sequence[MarketSnapshot], strategy: AdaptiveTrader | Callable[[MarketSnapshot], TradeSignal]) -> BacktestResult:
        portfolio = Portfolio(cash=self.initial_capital)
        equity_curve = [float(self.initial_capital)]
        trades = 0
        wins = 0

        for snapshot in snapshots:
            if callable(strategy):
                signal = strategy(snapshot)
            else:
                signal = strategy.decide(snapshot)

            if signal.action == "buy":
                position_value = portfolio.cash * 0.25
                quantity = position_value / max(snapshot.price, 1e-9)
                portfolio.cash -= position_value
                portfolio.add_position(snapshot.symbol, quantity, snapshot.price)
                trades += 1
                if signal.expected_return > 0:
                    wins += 1
            elif signal.action == "sell":
                position = portfolio.positions.get(snapshot.symbol)
                if position is not None:
                    sell_quantity = position.quantity
                    proceeds = sell_quantity * snapshot.price
                    portfolio.cash += proceeds
                    portfolio.remove_position(snapshot.symbol, sell_quantity)
                    trades += 1
                    if signal.expected_return < 0:
                        wins += 1

            current_equity = portfolio.total_equity({snapshot.symbol: snapshot.price})
            equity_curve.append(current_equity)

        final_equity = equity_curve[-1]
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        risk = compute_risk_metrics(equity_curve, holdings={k: v.quantity for k, v in portfolio.positions.items()}, total_equity=final_equity)
        win_rate = wins / trades if trades else 0.0

        return BacktestResult(
            equity_curve=equity_curve,
            total_return=total_return,
            max_drawdown=risk.max_drawdown,
            sharpe_ratio=risk.sharpe_ratio,
            win_rate=win_rate,
        )
