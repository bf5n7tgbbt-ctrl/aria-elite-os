# aria-elite-os
Entité Cognitive Financière Autonome

## Vue d'ensemble

Ce projet sert de socle pour orchestrer des flux de données, des modèles d'analyse et des outils d'automatisation autour d'une entité cognitive financière autonome.

## Structure du projet

- `src/aria/` : code applicatif principal
- `src/aria/data/` : intégration, normalisation et persistance des données
- `data/` : fichiers d'exemple et sources de données brutes
- `tests/` : tests de validation

## Intégration des données

Le paquet `aria.data` permet désormais de traiter plusieurs formats de sources, notamment CSV, JSON et API HTTP, puis de les enregistrer dans une base SQLite locale.

```python
from aria.data.integration import DataIntegrator, DataPipeline, SQLiteDataStore

integrator = DataIntegrator("data")
integrator.add_source("customers", "customers.csv")
integrator.add_source("orders", "orders.json")
records = integrator.integrate()
print(records[0])

store = SQLiteDataStore("data/warehouse.sqlite")
pipeline = DataPipeline(store=store, root_dir="data")
pipeline.add_source("customers", "customers.json")
normalized = pipeline.run(table_name="raw_customers")
print(normalized[0])
```

## Démarrage

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```
