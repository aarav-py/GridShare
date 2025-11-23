from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.frontend.cli import GridShareCLI


def test_cli_bootstrap_and_request_flow():
    cli = GridShareCLI()
    participants = cli.bootstrap_demo_participants()

    assert participants["producer_id"] in cli.app.registry.participants
    assert participants["consumer_id"] in cli.app.registry.participants

    request = cli.create_request(
        station_id="EVHub-Cleveland",
        kilowatt_hours=150.5,
        price_usd=42.0,
        desired_start="2025-06-01T10:00:00",
        priority="fast-track",
    )

    payload = cli.submit_charge_request(
        tx_id="cli-001",
        request=request,
        producer_id=participants["producer_id"],
        consumer_id=participants["consumer_id"],
        energy_source="solar",
    )

    rendered = cli.render_ledger(cli.app.ledger_snapshot())

    assert payload["route"] == ["AEP-Columbus", "Duke-Cincinnati", "EVHub-Cleveland"]
    assert "cli-001" in rendered
    assert "150.5" in rendered
