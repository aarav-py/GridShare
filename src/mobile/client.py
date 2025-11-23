"""Placeholder mobile client flows for onboarding and logging."""
from typing import Dict

from src.backend.registration import Participant, Registry
from src.backend.transactions import EnergyTransaction, TransactionLogger


class MobileClient:
    def __init__(self, registry: Registry, transactions: TransactionLogger):
        self.registry = registry
        self.transactions = transactions

    def onboard(self, participant_data: Dict) -> Participant:
        participant = Participant(**participant_data)
        self.registry.register(participant)
        return participant

    def submit_transaction(
        self,
        tx_data: Dict,
        producer: Participant,
        consumer: Participant,
        route: list | None = None,
        additional_metadata: Dict | None = None,
    ) -> Dict:
        transaction = EnergyTransaction(**tx_data)
        return self.transactions.log_transaction(
            transaction, producer, consumer, route=route, additional_metadata=additional_metadata
        )
