from __future__ import annotations

import argparse
import json

from aria.agent.trader import MarketSnapshot
from aria.runtime.agent_runtime import AgentRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ARIA autonomous trading runtime")
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--price", type=float, default=210.0)
    parser.add_argument("--previous-close", type=float, default=200.0)
    parser.add_argument("--volume", type=float, default=1_500_000.0)
    parser.add_argument("--volatility", type=float, default=0.018)
    parser.add_argument("--trend", type=float, default=1.2)
    parser.add_argument("--sentiment", type=float, default=0.75)
    parser.add_argument("--capital", type=float, default=100_000.0)
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    snapshot = MarketSnapshot(
        symbol=args.symbol,
        price=args.price,
        previous_close=args.previous_close,
        volume=args.volume,
        volatility=args.volatility,
        trend=args.trend,
        sentiment=args.sentiment,
    )
    runtime = AgentRuntime(capital=args.capital)
    report = runtime.run_cycle(
        snapshot,
        expected_returns={args.symbol: 0.12},
        risk_scores={args.symbol: 0.2},
    )

    if args.json:
        print(json.dumps({
            "phase": report.phase,
            "portfolio_value": report.portfolio_value,
            "signal": report.signal,
            "actions": report.actions,
            "notes": report.notes,
        }, indent=2))
        return

    print(f"ARIA runtime report for {args.symbol}")
    print(f"Phase: {report.phase}")
    print(f"Signal: {report.signal}")
    print(f"Portfolio value: {report.portfolio_value:.2f}")
    print(f"Actions: {', '.join(report.actions) if report.actions else 'none'}")
    for note in report.notes:
        print(f"- {note}")


if __name__ == "__main__":
    main()
