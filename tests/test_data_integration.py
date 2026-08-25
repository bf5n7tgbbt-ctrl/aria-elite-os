import json
from pathlib import Path

from aria.data.integration import DataIntegrator, DataPipeline, SQLiteDataStore


def test_data_integrator_combines_csv_and_json_sources(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    customers = data_dir / "customers.csv"
    customers.write_text(
        "id,name,segment\n1,Alice,retail\n2,Bob,enterprise\n",
        encoding="utf-8",
    )

    orders = data_dir / "orders.json"
    orders.write_text(
        json.dumps(
            {
                "records": [
                    {"order_id": 100, "customer_id": 1, "total": 99.99},
                    {"order_id": 101, "customer_id": 2, "total": 149.5},
                ]
            }
        ),
        encoding="utf-8",
    )

    integrator = DataIntegrator(data_dir)
    integrator.add_source("customers", customers)
    integrator.add_source("orders", orders)

    records = integrator.integrate()

    assert len(records) == 4
    assert records[0]["source"] == "customers"
    assert records[0]["name"] == "Alice"
    assert records[2]["source"] == "orders"
    assert records[2]["order_id"] == 100


def test_sqlite_store_persists_pipeline_records(tmp_path: Path) -> None:
    db_path = tmp_path / "records.sqlite"
    store = SQLiteDataStore(db_path)
    records = [
        {"id": 1, "name": "Alice", "value": 12.5},
        {"id": 2, "name": "Bob", "value": 8.25},
    ]

    saved = store.save_records(records, table_name="customers")
    persisted = store.fetch_all("customers")

    assert saved == 2
    assert persisted[0]["name"] == "Alice"
    assert persisted[1]["value"] == "8.25"


def test_data_pipeline_runs_and_stores(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    source_file = data_dir / "customers.json"
    source_file.write_text(
        json.dumps(
            {
                "records": [
                    {"id": 1, "name": "Alice", "segment": "retail"},
                    {"id": 2, "name": "Bob", "segment": "enterprise"},
                ]
            }
        ),
        encoding="utf-8",
    )

    store = SQLiteDataStore(tmp_path / "pipeline.sqlite")
    pipeline = DataPipeline(store=store, root_dir=data_dir)
    pipeline.add_source("customers", "customers.json")

    records = pipeline.run(table_name="raw_customers")
    assert len(records) == 2
    assert records[0]["source"] == "customers"
    assert store.fetch_all("raw_customers")[0]["name"] == "Alice"
