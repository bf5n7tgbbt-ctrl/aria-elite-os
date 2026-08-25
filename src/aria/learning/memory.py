from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExperienceRecord:
    symbol: str
    action: str
    expected_return: float
    realized_return: float
    confidence: float
    context: dict[str, Any] = field(default_factory=dict)


class ExperienceMemory:
    """Stores market outcomes and helps the agent adapt over time."""

    def __init__(self) -> None:
        self.records: list[ExperienceRecord] = []

    def add(self, record: ExperienceRecord) -> None:
        self.records.append(record)

    def average_return_for(self, symbol: str, action: str | None = None) -> float:
        matches = [
            record.realized_return
            for record in self.records
            if record.symbol == symbol and (action is None or record.action == action)
        ]
        if not matches:
            return 0.0
        return sum(matches) / len(matches)

    def confidence_bias(self, symbol: str) -> float:
        outcomes = [record.realized_return for record in self.records if record.symbol == symbol]
        if not outcomes:
            return 0.0
        return sum(outcomes) / len(outcomes)

    def last_context(self, symbol: str) -> dict[str, Any]:
        for record in reversed(self.records):
            if record.symbol == symbol:
                return record.context
        return {}
