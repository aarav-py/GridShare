"""Transaction logging across the grid ledger."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List

from .config import InterconnectConfig
from .registration import Participant
from src.ledger.adapter import LedgerAdapter


@dataclass
class EnergyTransaction:
    tx_id: str
    producer_id: str
    consumer_id: str
    kilowatt_hours: float
    price_usd: float
    timestamp: datetime
    energy_source: str = "solar"
    ev_session_id: str | None = None


class TransactionLogger:
    """Collects transactions and writes them to the ledger adapter."""

    def __init__(self, interconnect: InterconnectConfig, ledger: LedgerAdapter):
        self.interconnect = interconnect
        self.ledger = ledger
        self._transactions: List[EnergyTransaction] = []

    @property
    def transactions(self) -> List[EnergyTransaction]:
        return list(self._transactions)

    def log_transaction(
        self,
        transaction: EnergyTransaction,
        producer: Participant,
        consumer: Participant,
        route: List[str] | None = None,
        additional_metadata: Dict | None = None,
    ) -> Dict:
        if producer.participant_id != transaction.producer_id or consumer.participant_id != transaction.consumer_id:
            raise ValueError("Producer or consumer mismatch")
        payload = asdict(transaction)
        payload["timestamp"] = transaction.timestamp.isoformat()
        payload["interconnect"] = self.interconnect.name
        payload["network"] = "Virtual Clean Power Network"
        payload["route"] = route or []
        if additional_metadata:
            payload.update(additional_metadata)
        self._transactions.append(transaction)
        self.ledger.append_entry(payload)
        return payload
