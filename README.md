# aria-elite-os
Entité Cognitive Financière Autonome

## Vue d'ensemble

ARIA est conçu comme une IA évolutive orientée trading et analyse financière. Elle doit être capable d'observer son environnement, prévoir les tendances, simuler des scénarios, évaluer les opportunités, gérer le risque et exécuter des décisions de trading avec un comportement adaptatif.

## Architecture proposée

- `src/aria/agent/` : moteur d'IA et logique de décision de trading
- `src/aria/data/` : intégration, normalisation et stockage de données internes
- `src/aria/simulation/` : simulateurs de marché pour tester les scénarios
- `data/` : sources de données brutes et exemples
- `tests/` : validation de la logique de décision et du pipeline

## Exemples d'usage

```python
from aria.agent.trader import AdaptiveTrader, MarketSnapshot

trader = AdaptiveTrader(capital=100_000.0)
snapshot = MarketSnapshot(
    symbol="AAPL",
    price=210.0,
    previous_close=200.0,
    volume=1_500_000,
    volatility=0.018,
    trend=1.2,
    sentiment=0.75,
)

decision = trader.evaluate(snapshot)
print(decision.signal.action)
print(decision.position_size)
```

```python
from aria.simulation.market import MarketSimulator

simulator = MarketSimulator(seed=42)
path = simulator.simulate(100.0, steps=20, drift=0.001, volatility=0.02)
print(path[:5])
```

## Démarrage

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```
