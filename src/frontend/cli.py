"""Command-line interface for demonstrating GridShare flows.

The CLI wraps the existing mobile-facing orchestration so non-developers
can register participants, request EV charging energy, and inspect the
ledger without writing Python code.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from src.mobile.app import EVChargeRequest, P2PConnectApp


class GridShareCLI:
    """High-level helper for orchestrating demo interactions."""

    def __init__(self, app: Optional[P2PConnectApp] = None):
        self.app = app or P2PConnectApp()

    def bootstrap_demo_participants(
        self,
        producer_id: str = "solar-utility-demo",
        consumer_id: str = "ev-station-demo",
        producer_node: str = "AEP-Columbus",
        consumer_node: str = "EVHub-Cleveland",
    ) -> Dict[str, str]:
        """Register a default producer and consumer if they are absent."""

        participants = self.app.registry.participants
        if producer_id not in participants:
            self.app.register_user(
                participant_id=producer_id,
                role="producer",
                capacity_kw=750,
                node=producer_node,
                metadata={"resource": "solar farm"},
            )
        if consumer_id not in participants:
            self.app.register_user(
                participant_id=consumer_id,
                role="consumer",
                capacity_kw=250,
                node=consumer_node,
                metadata={"station_name": "Demo EV Hub"},
            )
        return {"producer_id": producer_id, "consumer_id": consumer_id}

    def create_request(
        self,
        station_id: str,
        kilowatt_hours: float,
        price_usd: float,
        desired_start: str,
        priority: str = "standard",
    ) -> EVChargeRequest:
        """Validate inputs and return an EVChargeRequest instance."""

        start_dt = datetime.fromisoformat(desired_start)
        return EVChargeRequest(
            station_id=station_id,
            kilowatt_hours=kilowatt_hours,
            price_usd=price_usd,
            desired_start=start_dt,
            priority=priority,
        )

    def submit_charge_request(
        self,
        tx_id: str,
        request: EVChargeRequest,
        producer_id: str,
        consumer_id: str,
        energy_source: str = "solar",
    ) -> Dict:
        """Route and log an EV charging energy transfer."""

        return self.app.request_ev_energy(
            tx_id=tx_id,
            request=request,
            producer_id=producer_id,
            consumer_id=consumer_id,
            energy_source=energy_source,
        )

    def render_ledger(self, entries: Optional[Iterable[Dict]] = None) -> str:
        """Render ledger entries in a human-readable format."""

        entries = list(entries) if entries is not None else self.app.ledger_snapshot()
        if not entries:
            return "No ledger entries yet. Submit an EV charge request to get started."

        lines: List[str] = ["GridShare Ledger"]
        for entry in entries:
            tx_id = entry.get("tx_id", "<unknown>")
            route = " -> ".join(entry.get("route", []))
            lines.extend(
                [
                    f"- Transaction {tx_id}: {entry.get('kilowatt_hours')} kWh @ ${entry.get('price_usd')}",
                    f"  Producer: {entry.get('producer_id')} | Consumer: {entry.get('consumer_id')} | Source: {entry.get('energy_source')}",
                    f"  Route: {route}",
                ]
            )
        return "\n".join(lines)


# CLI runner ---------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GridShare demo CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap", help="Register demo producer and consumer")
    bootstrap.add_argument("--producer-id", default="solar-utility-demo")
    bootstrap.add_argument("--consumer-id", default="ev-station-demo")
    bootstrap.add_argument("--producer-node", default="AEP-Columbus")
    bootstrap.add_argument("--consumer-node", default="EVHub-Cleveland")

    request = subparsers.add_parser("request", help="Submit an EV charging request")
    request.add_argument("--tx-id", required=True, help="Unique transaction identifier")
    request.add_argument("--station-id", default="EVHub-Cleveland")
    request.add_argument("--kilowatt-hours", type=float, required=True)
    request.add_argument("--price-usd", type=float, required=True)
    request.add_argument("--desired-start", required=True, help="ISO timestamp, e.g., 2025-05-10T15:30:00")
    request.add_argument("--priority", default="standard", choices=["standard", "fast-track"])
    request.add_argument("--producer-id", default="solar-utility-demo")
    request.add_argument("--consumer-id", default="ev-station-demo")
    request.add_argument("--energy-source", default="solar")

    ledger = subparsers.add_parser("ledger", help="Show ledger entries")
    ledger.add_argument("--as-json", action="store_true", help="Dump raw ledger entries")

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    cli = GridShareCLI()

    if args.command == "bootstrap":
        participants = cli.bootstrap_demo_participants(
            producer_id=args.producer_id,
            consumer_id=args.consumer_id,
            producer_node=args.producer_node,
            consumer_node=args.consumer_node,
        )
        print("Demo participants ready:")
        print(f"- Producer: {participants['producer_id']} @ {args.producer_node}")
        print(f"- Consumer: {participants['consumer_id']} @ {args.consumer_node}")
        return

    if args.command == "request":
        cli.bootstrap_demo_participants(producer_id=args.producer_id, consumer_id=args.consumer_id)
        request = cli.create_request(
            station_id=args.station_id,
            kilowatt_hours=args.kilowatt_hours,
            price_usd=args.price_usd,
            desired_start=args.desired_start,
            priority=args.priority,
        )
        payload = cli.submit_charge_request(
            tx_id=args.tx_id,
            request=request,
            producer_id=args.producer_id,
            consumer_id=args.consumer_id,
            energy_source=args.energy_source,
        )
        print("Charge request logged:")
        print(cli.render_ledger([payload]))
        return

    if args.command == "ledger":
        entries = cli.app.ledger_snapshot()
        if args.as_json:
            print(entries)
        else:
            print(cli.render_ledger(entries))


if __name__ == "__main__":
    main()
