from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    """Load a CSV file and return a list of rows as dictionaries."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


@dataclass(frozen=True)
class DataSource:
    name: str
    path: Path


class DataIntegrator:
    """Simple integration layer for combining multiple CSV sources."""

    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir is not None else Path.cwd()
        self.sources: list[DataSource] = []

    def add_source(self, name: str, path: str | Path) -> "DataIntegrator":
        resolved_path = Path(path)
        if not resolved_path.is_absolute():
            resolved_path = (self.root_dir / resolved_path).resolve()

        self.sources.append(DataSource(name=name, path=resolved_path))
        return self

    def integrate(self) -> list[dict[str, Any]]:
        integrated: list[dict[str, Any]] = []
        for source in self.sources:
            rows = load_csv_rows(source.path)
            for row in rows:
                integrated.append({"source": source.name, **row})
        return integrated
