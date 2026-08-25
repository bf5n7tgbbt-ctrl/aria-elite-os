from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aria.agent.trader import AdaptiveTrader, MarketSnapshot, TradeSignal
from aria.execution.executor import ExecutionEngine
from aria.learning.memory import ExperienceMemory, ExperienceRecord
from aria.learning.strategy import AdaptiveLearningStrategy
from aria.optimizer.allocation import PortfolioOptimizer
from aria.orchestration.manager import OrchestrationManager
from aria.portfolio.models import Portfolio


@dataclass(frozen=True)
class RuntimeReport:
    phase: str
    portfolio_value: float
    signal: str
    actions: list[str]
    notes: list[str]


class AgentRuntime:
    """Complete autonomous lifecycle for ARIA: simulate a market cycle end to end."""

    def __init__(self, capital: float = 100_000.0) -> None:
        if capital <= 0:
            raise ValueError("Capital must be positive")
        self.capital = capital
        self.portfolio = Portfolio(cash=capital)
        self.trader = AdaptiveTrader(capital=capital)
        self.optimizer = PortfolioOptimizer()
        self.memory = ExperienceMemory()
        self.learning_strategy = AdaptiveLearningStrategy(self.memory)
        self.execution = ExecutionEngine()
        self.orchestrator = OrchestrationManager()
        self.latest_prices: dict[str, float] = {}

    def run_cycle(self, market_snapshot: MarketSnapshot, *, expected_returns: dict[str, float] | None = None, risk_scores: dict[str, float] | None = None) -> RuntimeReport:
        cycle_order_start = len(self.execution.journal.orders)
        self.latest_prices[market_snapshot.symbol] = market_snapshot.price
        current_prices = self.latest_prices
        self.orchestrator.advance(
            "signal_generation",
            strategy_score=0.8,
            risk_level=0.25,
            portfolio_equity=self.portfolio.total_equity(current_prices),
            last_signal="hold",
        )

        raw_signal = self.trader.decide(market_snapshot)
        signal = self.learning_strategy.refine(market_snapshot, raw_signal)

        if signal.action != "hold":
            entry_price = None
            if signal.action == "sell":
                position = self.portfolio.positions.get(signal.symbol)
                if position is not None:
                    entry_price = position.avg_price
            order = self.execution.execute(signal, self.portfolio, market_snapshot.price)
            if order is not None:
                if order.action == "sell" and entry_price is not None:
                    realized_return = (order.price - entry_price) / entry_price
                    self.memory.add(
                        ExperienceRecord(
                            symbol=order.symbol,
                            action=order.action,
                            expected_return=signal.expected_return,
                            realized_return=realized_return,
                            confidence=signal.confidence,
                            context={
                                "entry_price": entry_price,
                                "exit_price": order.price,
                            },
                        )
                    )

        positions = {
            symbol: self.portfolio.position_weight(symbol, current_prices)
            for symbol in self.portfolio.positions
        }
        if expected_returns is None:
            expected_returns = {symbol: 0.08 for symbol in positions}
        if risk_scores is None:
            risk_scores = {symbol: 0.3 for symbol in positions}
        allocations = self.optimizer.optimize(
            positions,
            expected_returns,
            risk_scores,
            self.portfolio.total_equity(current_prices),
        )

        self.orchestrator.advance(
            "monitoring",
            strategy_score=signal.confidence,
            risk_level=signal.risk_score,
            portfolio_equity=self.portfolio.total_equity(current_prices),
            last_signal=signal.action,
            notes=[decision.reason for decision in allocations],
        )
        cycle_actions = [
            order.action for order in self.execution.journal.orders[cycle_order_start:]
        ]

        return RuntimeReport(
            phase="monitoring",
            portfolio_value=self.portfolio.total_equity(current_prices),
            signal=signal.action,
            actions=cycle_actions,
            notes=[decision.reason for decision in allocations],
        )
