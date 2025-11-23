from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.mobile.app import EVChargeRequest, P2PConnectApp


def test_vcpn_ev_charge_flow_records_route_and_metadata():
    app = P2PConnectApp()
    producer = app.register_user(
        participant_id="solar-001",
        role="producer",
        capacity_kw=750,
        node="AEP-Columbus",
        metadata={"resource": "solar farm"},
    )
    consumer = app.register_user(
        participant_id="ev-station-9",
        role="consumer",
        capacity_kw=200,
        node="EVHub-Cleveland",
        metadata={"station_name": "North Coast EV Hub"},
    )

    ev_request = EVChargeRequest(
        station_id="EVHub-Cleveland",
        kilowatt_hours=320.0,
        price_usd=48.25,
        desired_start=datetime(2025, 5, 10, 15, 30, 0),
        priority="fast-track",
    )

    payload = app.request_ev_energy(
        tx_id="tx-ev-0001",
        request=ev_request,
        producer_id=producer.participant_id,
        consumer_id=consumer.participant_id,
        energy_source="solar",
    )

    assert payload["route"] == ["AEP-Columbus", "Duke-Cincinnati", "EVHub-Cleveland"]
    assert payload["ev_station_id"] == "EVHub-Cleveland"
    assert payload["network"] == "Virtual Clean Power Network"


def test_hybrid_registration_is_supported():
    app = P2PConnectApp()
    participant = app.register_user(
        participant_id="prosumer-77",
        role="hybrid",
        capacity_kw=150,
        node="AEP-Prospect",
        metadata={"storage": "battery"},
    )

    assert participant.participant_id == "prosumer-77"
    assert participant.role == "hybrid"
    assert app.registry.get("prosumer-77").metadata["node"] == "AEP-Prospect"
