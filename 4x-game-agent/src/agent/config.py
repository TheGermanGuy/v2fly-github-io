"""Laden des Spielprofils (Truppen-Basiswerte, Konter-Matrix, Menüpfade,
Truppentypen, OCR-Labels).

Liest eine einfache JSON-Profildatei. JSON hält das Projekt abhängigkeitsfrei.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .models import TroopStats
from .strategy import GameProfile


@dataclass
class ProfileBundle:
    profile: GameProfile
    menu_paths: Dict[str, List[Tuple[int, int]]]
    troop_types: List[str]
    ocr_labels: Dict[str, List[str]] = field(default_factory=dict)
    capture_screens: List[str] = field(default_factory=list)
    game: str = ""


def load_profile(path: str) -> ProfileBundle:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    troops = {
        name: TroopStats(
            name=name,
            attack=float(t["attack"]),
            defense=float(t["defense"]),
            health=float(t["health"]),
        )
        for name, t in data["troops"].items()
    }
    counter = {
        d: {a: float(v) for a, v in row.items()}
        for d, row in data.get("counter", {}).items()
    }
    menu_paths = {
        name: [tuple(p) for p in steps]
        for name, steps in data.get("menu_paths", {}).items()
        if isinstance(steps, list)
    }
    troop_types = data.get("troop_types") or list(troops.keys())
    ocr_labels = data.get("ocr_labels", {})
    capture_screens = data.get("capture_screens") or []
    return ProfileBundle(
        profile=GameProfile(troops=troops, counter=counter),
        menu_paths=menu_paths,
        troop_types=troop_types,
        ocr_labels=ocr_labels,
        capture_screens=capture_screens,
        game=data.get("game", ""),
    )


def load_game_profile(path: str) -> Tuple[GameProfile, Dict[str, List[Tuple[int, int]]]]:
    """Rückwärtskompatibel: (GameProfile, menu_paths)."""
    b = load_profile(path)
    return b.profile, b.menu_paths
