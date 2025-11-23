"""Minimal ledger adapter abstraction for blockchain integration."""
from typing import Dict, List


class LedgerAdapter:
    def __init__(self) -> None:
        self._entries: List[Dict] = []

    @property
    def entries(self) -> List[Dict]:
        return list(self._entries)

    def append_entry(self, entry: Dict) -> None:
        """Simulate writing a transaction to a blockchain ledger."""
        self._entries.append(entry)
