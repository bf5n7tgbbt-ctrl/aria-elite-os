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
        self.capital = capital
        self.portfolio = Portfolio(cash=capital)
        self.trader = AdaptiveTrader(capital=capital)
        self.optimizer = PortfolioOptimizer()
        self.memory = ExperienceMemory()
        self.learning_strategy = AdaptiveLearningStrategy(self.memory)
        self.execution = ExecutionEngine()
        self.orchestrator = OrchestrationManager()

    def run_cycle(self, market_snapshot: MarketSnapshot, *, expected_returns: dict[str, float] | None = None, risk_scores: dict[str, float] | None = None) -> RuntimeReport:
        self.orchestrator.advance("signal_generation", strategy_score=0.8, risk_level=0.25, portfolio_equity=self.portfolio.cash, last_signal="hold")

        raw_signal = self.trader.decide(market_snapshot)
        signal = self.learning_strategy.refine(market_snapshot, raw_signal)

        if signal.action != "hold":
            order = self.execution.execute(signal, self.portfolio, market_snapshot.price)
            if order is not None:
                realized_return = (market_snapshot.price - order.price) / order.price if order.action == "buy" else 0.0
                self.memory.add(
                    ExperienceRecord(
                        symbol=order.symbol,
                        action=order.action,
                        expected_return=signal.expected_return,
                        realized_return=realized_return,
                        confidence=signal.confidence,
                        context={"price": market_snapshot.price},
                    )
                )

        positions = {symbol: position.quantity for symbol, position in self.portfolio.positions.items()}
        expected_returns = expected_returns or {symbol: 0.08 for symbol in positions}
        risk_scores = risk_scores or {symbol: 0.3 for symbol in positions}
        allocations = self.optimizer.optimize(positions, expected_returns, risk_scores, self.portfolio.total_equity({market_snapshot.symbol: market_snapshot.price}))

        self.orchestrator.advance(
            "monitoring",
            strategy_score=signal.confidence,
            risk_level=signal.risk_score,
            portfolio_equity=self.portfolio.total_equity({market_snapshot.symbol: market_snapshot.price}),
            last_signal=signal.action,
            notes=[decision.reason for decision in allocations],
        )

        return RuntimeReport(
            phase="monitoring",
            portfolio_value=self.portfolio.total_equity({market_snapshot.symbol: market_snapshot.price}),
            signal=signal.action,
            actions=[order.action for order in self.execution.journal.orders[-5:]],
            notes=[decision.reason for decision in allocations],
        )
