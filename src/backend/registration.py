"""Producer and consumer registration logic."""
from dataclasses import dataclass, field
from typing import Dict

from .config import InterconnectConfig


@dataclass
class Participant:
    participant_id: str
    role: str
    capacity_kw: float
    metadata: Dict[str, str] = field(default_factory=dict)


class Registry:
    """Simple in-memory registry for producers and consumers."""

    def __init__(self, interconnect: InterconnectConfig):
        self.interconnect = interconnect
        self.entries: Dict[str, Participant] = {}

    def register(self, participant: Participant) -> None:
        if participant.participant_id in self.entries:
            raise ValueError(f"Participant {participant.participant_id} already registered")
        if participant.role not in {"producer", "consumer", "hybrid"}:
            raise ValueError("role must be 'producer', 'consumer', or 'hybrid'")
        self.entries[participant.participant_id] = participant

    def get(self, participant_id: str) -> Participant:
        try:
            return self.entries[participant_id]
        except KeyError as exc:
            raise KeyError(f"Participant {participant_id} is not registered") from exc

    @property
    def participants(self) -> Dict[str, Participant]:
        """Return a copy of registered participants keyed by ID."""

        return dict(self.entries)
