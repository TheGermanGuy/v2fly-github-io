"""Zusammenführung & Vollständigkeitsprüfung der per ADB erfassten Stats.

In Evony liegen die relevanten Werte auf mehreren Screens (Monarch-Profil,
Truppen-Panel, Buff-Panel). Diese Modul-Funktionen mergen die Einzel-Analysen zu
einem vollständigen Datensatz und prüfen *vor* der Strategieberechnung, ob alle
relevanten Informationen wirklich erfasst wurden.

Reine Funktionen (keine I/O) — vollständig unit-testbar.
"""
from __future__ import annotations

from typing import Dict, List, Tuple


def merge_raw_stats(raws: List[Dict]) -> Dict:
    """Mehrere Roh-Dicts (je Screen) zu einem vollständigen Roh-Dict mergen.

    Regel: ein nicht-leerer/echter Wert von einem späteren Screen füllt eine
    Lücke; vorhandene echte Werte werden nicht durch 0/leer überschrieben.
    """
    merged: Dict = {
        "player_id": "unknown",
        "power": 0,
        "available_troops": {},
        "reinforcement_capacity": 0,
        "buffs": {"global_defense": 0.0, "global_health": 0.0, "defense_by_type": {}},
        "enemy_composition": {},
    }
    for raw in raws:
        if not raw:
            continue
        pid = raw.get("player_id")
        if pid and pid != "unknown" and merged["player_id"] == "unknown":
            merged["player_id"] = pid
        merged["power"] = merged["power"] or int(raw.get("power", 0) or 0)
        merged["reinforcement_capacity"] = merged["reinforcement_capacity"] or int(
            raw.get("reinforcement_capacity", 0) or 0
        )
        for t, v in (raw.get("available_troops") or {}).items():
            v = int(v or 0)
            if v and not merged["available_troops"].get(t):
                merged["available_troops"][t] = v
        b = raw.get("buffs") or {}
        merged["buffs"]["global_defense"] = merged["buffs"]["global_defense"] or float(
            b.get("global_defense", 0.0) or 0.0
        )
        merged["buffs"]["global_health"] = merged["buffs"]["global_health"] or float(
            b.get("global_health", 0.0) or 0.0
        )
        for t, v in (b.get("defense_by_type") or {}).items():
            v = float(v or 0.0)
            if v and not merged["buffs"]["defense_by_type"].get(t):
                merged["buffs"]["defense_by_type"][t] = v
        for a, v in (raw.get("enemy_composition") or {}).items():
            v = float(v or 0.0)
            if v and not merged["enemy_composition"].get(a):
                merged["enemy_composition"][a] = v
    return merged


def assess_completeness(
    raw: Dict, troop_types: List[str], require_buffs: bool = False
) -> Tuple[bool, List[str]]:
    """Prüft, ob alle relevanten Stats erfasst sind.

    Pflicht: power > 0, Verstärkungskapazität > 0 und für jeden Truppentyp eine
    (auch 0 erlaubte, aber *vorhandene*) Angabe. Optional: mindestens ein Buff.
    Gibt (vollständig?, Liste fehlender Felder) zurück.
    """
    missing: List[str] = []
    if int(raw.get("power", 0) or 0) <= 0:
        missing.append("power")
    if int(raw.get("reinforcement_capacity", 0) or 0) <= 0:
        missing.append("reinforcement_capacity")
    troops = raw.get("available_troops") or {}
    for t in troop_types:
        if t not in troops:
            missing.append(f"available_troops.{t}")
    if require_buffs:
        b = raw.get("buffs") or {}
        has_buff = (
            float(b.get("global_defense", 0) or 0) > 0
            or float(b.get("global_health", 0) or 0) > 0
            or any(float(v or 0) > 0 for v in (b.get("defense_by_type") or {}).values())
        )
        if not has_buff:
            missing.append("buffs")
    return (len(missing) == 0, missing)
