from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentCycleState:
    phase: str = "idle"
    strategy_score: float = 0.0
    portfolio_equity: float = 0.0
    risk_level: float = 0.0
    last_signal: str = "hold"
    notes: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "strategy_score": self.strategy_score,
            "portfolio_equity": self.portfolio_equity,
            "risk_level": self.risk_level,
            "last_signal": self.last_signal,
            "notes": list(self.notes),
        }


class MonitoringDashboard:
    """Provides a lightweight overview of the AI lifecycle."""

    def __init__(self) -> None:
        self.state = AgentCycleState()

    def update(self, **kwargs: Any) -> AgentCycleState:
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        return self.state

    def health(self) -> str:
        if self.state.risk_level > 0.7:
            return "at_risk"
        if self.state.strategy_score > 0.8:
            return "favorable"
        if self.state.strategy_score > 0.5:
            return "monitoring"
        return "neutral"


class OrchestrationManager:
    """Coordinates ingestion, strategy, portfolio, execution and learning loops."""

    def __init__(self) -> None:
        self.dashboard = MonitoringDashboard()
        self.events: list[str] = []

    def log(self, event: str) -> None:
        self.events.append(event)

    def advance(self, phase: str, **context: Any) -> AgentCycleState:
        self.log(f"phase:{phase}")
        self.dashboard.update(**context)
        self.dashboard.state.phase = phase
        return self.dashboard.state

    def summary(self) -> dict[str, Any]:
        return {
            "health": self.dashboard.health(),
            "state": self.dashboard.state.snapshot(),
            "events": list(self.events),
        }
