from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from aria.agent.trader import AdaptiveTrader, MarketSnapshot
    from aria.simulation.market import MarketSimulator
except Exception:  # pragma: no cover - bootstrap should still be useful without package install
    AdaptiveTrader = None
    MarketSnapshot = None
    MarketSimulator = None


@dataclass
class EnvironmentProfile:
    name: str = "aria-default"
    capital: float = 100_000.0
    risk_per_trade: float = 0.02
    max_position_ratio: float = 0.25
    learning_rate: float = 0.05
    market_modes: list[str] = field(
        default_factory=lambda: ["equities", "crypto", "forex", "macro"]
    )
    data_sources: list[str] = field(
        default_factory=lambda: ["csv", "json", "api", "sqlite"]
    )
    simulation_steps: int = 30


@dataclass
class AriaSetup:
    root_dir: Path = field(default_factory=lambda: ROOT)
    profile: EnvironmentProfile = field(default_factory=EnvironmentProfile)

    def ensure_directories(self) -> list[Path]:
        directories = [
            self.root_dir / "src" / "aria" / "agent",
            self.root_dir / "src" / "aria" / "data",
            self.root_dir / "src" / "aria" / "simulation",
            self.root_dir / "data",
            self.root_dir / "tests",
            self.root_dir / "logs",
            self.root_dir / "reports",
            self.root_dir / "models",
        ]
        for path in directories:
            path.mkdir(parents=True, exist_ok=True)
        return directories

    def write_default_config(self) -> Path:
        config_path = self.root_dir / ".aria-config.json"
        config_path.write_text(
            json.dumps(asdict(self.profile), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return config_path

    def write_env_template(self) -> Path:
        env_path = self.root_dir / ".env.example"
        env_path.write_text(
            "\n".join(
                [
                    "ARIA_ENV=development",
                    "ARIA_CAPITAL=100000",
                    "ARIA_RISK_PER_TRADE=0.02",
                    "ARIA_MAX_POSITION_RATIO=0.25",
                    "ARIA_LEARNING_RATE=0.05",
                    "ARIA_MARKETS=equities,crypto,forex,macro",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return env_path

    def seed_sample_data(self) -> dict[str, Path]:
        data_dir = self.root_dir / "data"
        price_path = data_dir / "market_snapshot.json"
        price_path.write_text(
            json.dumps(
                {
                    "symbol": "AAPL",
                    "price": 210.0,
                    "previous_close": 200.0,
                    "volume": 1500000,
                    "volatility": 0.018,
                    "trend": 1.2,
                    "sentiment": 0.75,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return {"market_snapshot": price_path}

    def bootstrap(self) -> dict[str, Any]:
        directories = self.ensure_directories()
        config_file = self.write_default_config()
        env_file = self.write_env_template()
        sample_data = self.seed_sample_data()

        runtime: dict[str, Any] = {
            "root_dir": str(self.root_dir),
            "directories": [str(path) for path in directories],
            "config": str(config_file),
            "env_template": str(env_file),
            "sample_data": {name: str(path) for name, path in sample_data.items()},
        }

        if AdaptiveTrader is not None and MarketSimulator is not None:
            trader = AdaptiveTrader(
                capital=self.profile.capital,
                max_position_size=self.profile.max_position_ratio,
                risk_per_trade=self.profile.risk_per_trade,
            )
            simulator = MarketSimulator(seed=42)
            runtime["trader_ready"] = True
            runtime["default_trader"] = trader
            runtime["default_simulator"] = simulator
        else:
            runtime["trader_ready"] = False

        return runtime


def bootstrap(root_dir: str | Path | None = None) -> dict[str, Any]:
    path = Path(root_dir) if root_dir is not None else ROOT
    setup = AriaSetup(root_dir=path)
    return setup.bootstrap()


if __name__ == "__main__":
    state = bootstrap()
    print("ARIA bootstrap complete.")
    print(f"Project root: {state['root_dir']}")
    print(f"AI runtime ready: {state['trader_ready']}")
    print("Folders created:")
    for directory in state["directories"]:
        print(f" - {directory}")
    print(f"Config file: {state['config']}")
    print(f"Env template: {state['env_template']}")
