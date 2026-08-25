# aria-elite-os
Entité Cognitive Financière Autonome

## Vue d'ensemble

Ce projet sert de socle pour orchestrer des flux de données, des modèles d'analyse et des outils d'automatisation autour d'une entité cognitive financière autonome.

## Structure du projet

- `src/aria/` : code applicatif principal
- `src/aria/data/` : intégration et normalisation des données
- `data/` : fichiers d'exemple et sources de données brutes
- `tests/` : tests de validation

## Intégration des données

Le paquet `aria.data` propose une base minimale pour charger plusieurs fichiers CSV et les fusionner dans un format d'intégration exploitable.

```python
from aria.data.integration import DataIntegrator

integrator = DataIntegrator("data")
integrator.add_source("customers", "data/customers.csv")
integrator.add_source("orders", "data/orders.csv")

records = integrator.integrate()
print(records[0])
```

## Démarrage

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```
