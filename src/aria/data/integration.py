from __future__ import annotations

import csv
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import request


def load_csv_rows(path: str | Path) -> list[dict[str, str]]:
    """Load a CSV file and return a list of rows as dictionaries."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def load_json_rows(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON array or object containing a `records` list."""
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON not found: {json_path}")

    with json_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        rows = payload["records"]
    else:
        raise ValueError("JSON source must be a list or an object containing a 'records' list")

    normalized: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            normalized.append(row)
    return normalized


def fetch_json_rows(url: str, *, timeout: int = 10, headers: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Fetch JSON from an HTTP API and return a list of dictionaries."""
    req = request.Request(url, headers=headers or {})
    with request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
        rows = payload["records"]
    else:
        raise ValueError("API response must be a list or an object containing a 'records' list")

    return [row for row in rows if isinstance(row, dict)]


@dataclass(frozen=True)
class DataSource:
    name: str
    path: str | Path | None = None
    url: str | None = None
    source_type: str | None = None

    @property
    def kind(self) -> str:
        if self.source_type:
            return self.source_type
        if self.url:
            return "json"
        if self.path is not None:
            suffix = str(self.path).lower()
            if suffix.endswith(".csv"):
                return "csv"
            if suffix.endswith(".json"):
                return "json"
        return "unknown"


class SQLiteDataStore:
    """Small SQLite-backed storage to persist normalized records."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_records(self, records: list[dict[str, Any]], table_name: str = "records") -> int:
        if not records:
            return 0

        columns = list(dict.fromkeys(key for record in records for key in record.keys()))
        column_sql = ", ".join(f'"{column}" TEXT' for column in columns)

        with self.connect() as conn:
            conn.execute(f'DROP TABLE IF EXISTS "{table_name}";')
            conn.execute(f'CREATE TABLE "{table_name}" ({column_sql});')
            for record in records:
                values = [record.get(column) for column in columns]
                placeholders = ", ".join("?" for _ in columns)
                insert_sql = f'INSERT INTO "{table_name}" VALUES ({placeholders});'
                conn.execute(insert_sql, values)
            conn.commit()
        return len(records)

    def fetch_all(self, table_name: str = "records") -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(f'SELECT * FROM "{table_name}";').fetchall()
        return [dict(row) for row in rows]


class DataIntegrator:
    """Combine CSV, JSON and API-backed sources into one data stream."""

    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir is not None else Path.cwd()
        self.sources: list[DataSource] = []

    def add_source(self, name: str, path: str | Path | None = None, *, url: str | None = None, source_type: str | None = None) -> "DataIntegrator":
        if path is None and url is None:
            raise ValueError("A data source requires either a file path or a URL")

        if path is not None:
            resolved_path = Path(path)
            if not resolved_path.is_absolute():
                resolved_path = (self.root_dir / resolved_path).resolve()
            path = resolved_path

        self.sources.append(DataSource(name=name, path=path, url=url, source_type=source_type))
        return self

    def _load_rows(self, source: DataSource) -> list[dict[str, Any]]:
        if source.url:
            return fetch_json_rows(source.url)

        if source.path is None:
            raise ValueError(f"Source '{source.name}' is missing a path")

        kind = source.kind
        if kind == "csv":
            return load_csv_rows(source.path)
        if kind == "json":
            return load_json_rows(source.path)
        raise ValueError(f"Unsupported source type '{kind}' for '{source.name}'")

    def integrate(self) -> list[dict[str, Any]]:
        integrated: list[dict[str, Any]] = []
        for source in self.sources:
            rows = self._load_rows(source)
            for row in rows:
                integrated.append({"source": source.name, **row})
        return integrated


class DataPipeline:
    """Small orchestration pipeline for ingestion, normalization and storage."""

    def __init__(self, store: SQLiteDataStore | None = None, root_dir: str | Path | None = None) -> None:
        self.integrator = DataIntegrator(root_dir=root_dir)
        self.store = store

    def add_source(self, name: str, path: str | Path | None = None, *, url: str | None = None, source_type: str | None = None) -> "DataPipeline":
        self.integrator.add_source(name, path, url=url, source_type=source_type)
        return self

    def normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        normalized = {}
        for key, value in record.items():
            normalized[str(key).strip()] = value
        return normalized

    def run(self, *, table_name: str = "records") -> list[dict[str, Any]]:
        records = [self.normalize_record(record) for record in self.integrator.integrate()]
        if self.store is not None:
            self.store.save_records(records, table_name=table_name)
        return records
