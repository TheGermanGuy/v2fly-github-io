"""Datenmodelle für den 4x-game-agent.

Reine stdlib-Dataclasses, damit dieser Modul-Teil ohne externe Abhängigkeiten
importier- und testbar ist.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List


@dataclass(frozen=True)
class TroopStats:
    """Basiswerte eines Truppentyps (vor Buffs)."""
    name: str
    attack: float
    defense: float
    health: float


@dataclass
class Buffs:
    """Aktuell erkannte Buffs des Spielers.

    Werte sind additive Prozentsätze als Dezimalzahl (0.25 == +25 %).
    `defense_by_type` überschreibt/ergänzt den globalen Defense-Buff pro Typ.
    """
    global_defense: float = 0.0
    global_health: float = 0.0
    defense_by_type: Dict[str, float] = field(default_factory=dict)

    def defense_multiplier(self, troop_type: str) -> float:
        return 1.0 + self.global_defense + self.defense_by_type.get(troop_type, 0.0)

    def health_multiplier(self) -> float:
        return 1.0 + self.global_health


@dataclass
class PlayerStats:
    """Aus einem Screenshot extrahierter Spielerzustand."""
    player_id: str
    power: int = 0
    # Verfügbare Truppenanzahl je Typ (Obergrenze für die Verteidigung).
    available_troops: Dict[str, int] = field(default_factory=dict)
    # Verstärkungskapazität (max. Truppen, die in die Verteidigung passen).
    reinforcement_capacity: int = 0
    raw: Dict = field(default_factory=dict)  # vollständige Gemini-Rohausgabe

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EnemyComposition:
    """Beobachtete/erwartete Angreifer-Zusammensetzung (Anteile, Summe ~1.0)."""
    fractions: Dict[str, float] = field(default_factory=dict)

    def normalized(self) -> Dict[str, float]:
        total = sum(self.fractions.values())
        if total <= 0:
            return {}
        return {k: v / total for k, v in self.fractions.items()}


@dataclass
class Allocation:
    troop_type: str
    count: int
    effective_defense_per_unit: float

    @property
    def total_effective_defense(self) -> float:
        return self.count * self.effective_defense_per_unit


@dataclass
class DefenseStrategy:
    allocations: List[Allocation]
    total_effective_defense: float
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "allocations": [asdict(a) for a in self.allocations],
            "total_effective_defense": self.total_effective_defense,
            "notes": self.notes,
        }
