from pathlib import Path

from aria.data.integration import DataIntegrator


def test_data_integrator_combines_csv_sources(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    customers = data_dir / "customers.csv"
    customers.write_text(
        "id,name,segment\n1,Alice,retail\n2,Bob,enterprise\n",
        encoding="utf-8",
    )

    orders = data_dir / "orders.csv"
    orders.write_text(
        "order_id,customer_id,total\n100,1,99.99\n101,2,149.5\n",
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
    assert records[2]["order_id"] == "100"
