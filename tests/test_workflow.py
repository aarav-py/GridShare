from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.backend.config import OHIO_INTERCONNECT
from src.backend.registration import Participant, Registry
from src.backend.routing import Router
from src.backend.transactions import EnergyTransaction, TransactionLogger
from src.ledger.adapter import LedgerAdapter


def test_registration_and_transaction_logging():
    registry = Registry(OHIO_INTERCONNECT)
    ledger = LedgerAdapter()
    logger = TransactionLogger(OHIO_INTERCONNECT, ledger)

    producer = Participant(participant_id="p1", role="producer", capacity_kw=500, metadata={"node": "AEP-Columbus"})
    consumer = Participant(participant_id="c1", role="consumer", capacity_kw=250, metadata={"node": "EVHub-Cleveland"})

    registry.register(producer)
    registry.register(consumer)

    tx = EnergyTransaction(
        tx_id="tx-001",
        producer_id="p1",
        consumer_id="c1",
        kilowatt_hours=120.5,
        price_usd=18.75,
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
    )

    payload = logger.log_transaction(tx, producer, consumer)
    assert payload["interconnect"] == OHIO_INTERCONNECT.name
    assert ledger.entries[0]["kilowatt_hours"] == 120.5


def test_routing_path_finds_shortest_route():
    registry = Registry(OHIO_INTERCONNECT)
    router = Router(OHIO_INTERCONNECT)
    producer = Participant(participant_id="p1", role="producer", capacity_kw=500, metadata={"node": "AEP-Columbus"})
    consumer = Participant(participant_id="c1", role="consumer", capacity_kw=250, metadata={"node": "EVHub-Cleveland"})

    registry.register(producer)
    registry.register(consumer)

    path = router.compute_route(producer, consumer)
    assert path == ["AEP-Columbus", "Duke-Cincinnati", "EVHub-Cleveland"]
