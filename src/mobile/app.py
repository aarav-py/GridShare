"""High-level orchestration for the P2PConnect mobile experience.

The app connects registration, routing, and ledger logging to demonstrate
how the Virtual Clean Power Network (VCPN) moves clean energy to EV
charging stations.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from src.backend.config import InterconnectConfig, OHIO_INTERCONNECT
from src.backend.registration import Participant, Registry
from src.backend.routing import Router
from src.backend.transactions import EnergyTransaction, TransactionLogger
from src.ledger.adapter import LedgerAdapter


@dataclass
class EVChargeRequest:
    """A request to deliver clean energy to an EV charging station."""

    station_id: str
    kilowatt_hours: float
    price_usd: float
    desired_start: datetime
    priority: str = "standard"


class P2PConnectApp:
    """Coordinates the Virtual Clean Power Network for mobile clients."""

    def __init__(self, interconnect: InterconnectConfig | None = None):
        self.interconnect = interconnect or OHIO_INTERCONNECT
        self.ledger = LedgerAdapter()
        self.registry = Registry(self.interconnect)
        self.transactions = TransactionLogger(self.interconnect, self.ledger)
        self.router = Router(self.interconnect)

    def register_user(
        self,
        participant_id: str,
        role: str,
        capacity_kw: float,
        node: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Participant:
        """Register a producer, consumer, or hybrid participant with node metadata."""

        metadata = metadata or {}
        metadata.setdefault("node", node)
        participant = Participant(participant_id=participant_id, role=role, capacity_kw=capacity_kw, metadata=metadata)
        self.registry.register(participant)
        return participant

    def connect_route(self, producer_id: str, consumer_id: str) -> List[str]:
        """Compute the SDNC path across the interconnect graph."""

        producer = self.registry.get(producer_id)
        consumer = self.registry.get(consumer_id)
        return self.router.compute_route(producer, consumer)

    def request_ev_energy(
        self,
        tx_id: str,
        request: EVChargeRequest,
        producer_id: str,
        consumer_id: str,
        energy_source: str = "solar",
    ) -> Dict:
        """Create a blockchain-backed EV charging transaction."""

        producer = self.registry.get(producer_id)
        consumer = self.registry.get(consumer_id)
        route = self.connect_route(producer_id, consumer_id)
        transaction = EnergyTransaction(
            tx_id=tx_id,
            producer_id=producer.participant_id,
            consumer_id=consumer.participant_id,
            kilowatt_hours=request.kilowatt_hours,
            price_usd=request.price_usd,
            timestamp=request.desired_start,
            energy_source=energy_source,
            ev_session_id=request.station_id,
        )
        metadata = {
            "ev_station_id": request.station_id,
            "sdnc": "optimal-routing",
            "priority": request.priority,
        }
        return self.transactions.log_transaction(
            transaction, producer, consumer, route=route, additional_metadata=metadata
        )

    def ledger_snapshot(self) -> List[Dict]:
        """Provide the current blockchain-backed transaction list."""

        return self.ledger.entries
