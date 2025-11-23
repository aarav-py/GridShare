"""Configuration for grid interconnects and compliance."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class InterconnectConfig:
    name: str
    transmission_operator: str
    compliance_rules: List[str]
    utility_partners: List[str]
    ev_charging_partners: List[str]
    grid_nodes: Dict[str, List[str]]
    regional_constraints: Dict[str, str] = field(default_factory=dict)


OHIO_INTERCONNECT = InterconnectConfig(
    name="Ohio Utility Intertie",
    transmission_operator="PJM Interconnection",
    compliance_rules=[
        "PUCO net-metering provisions",
        "SB 310 renewable portfolio standards",
        "IEEE 1547 DER interconnection",
        "Utility-specific demand response limits",
    ],
    utility_partners=[
        "AEP Ohio",
        "Duke Energy Ohio",
        "FirstEnergy",
    ],
    ev_charging_partners=[
        "ChargePoint Midwest Hub",
        "Electrify America Columbus",
        "Municipal Fleet Depots",
    ],
    grid_nodes={
        "AEP-Columbus": ["Duke-Cincinnati", "AEP-Prospect"],
        "AEP-Prospect": ["FirstEnergy-Akron"],
        "Duke-Cincinnati": ["EVHub-Cleveland", "FirstEnergy-Akron", "EVHub-Dayton"],
        "FirstEnergy-Akron": ["EVHub-Cleveland"],
        "EVHub-Dayton": ["EVHub-Cleveland"],
        "EVHub-Cleveland": [],
    },
    regional_constraints={
        "peak_demand_mw": "Follow PUCO emergency curtailment notices",
        "utility_routing_preference": "Prioritize AEP-owned assets when available",
    },
)

DEFAULT_CONFIGS = {"ohio": OHIO_INTERCONNECT}
