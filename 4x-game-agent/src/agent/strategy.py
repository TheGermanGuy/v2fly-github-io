"""Deterministischer, mathematisch exakter Verteidigungsstrategie-Rechner.

Modell
------
Für jeden eigenen Truppentyp t berechnen wir die *effektive Verteidigung pro
Einheit* gegen die beobachtete Angreifer-Zusammensetzung:

    eff_def(t) = base_def(t) * buff_def(t)
                 * Σ_a  enemy_fraction(a) * counter(t, a)

wobei
  - base_def(t)        : Basis-Verteidigung des Typs t,
  - buff_def(t)        : Buff-Multiplikator (1 + Prozentsumme) für t,
  - enemy_fraction(a)  : normierter Anteil des Angreifertyps a,
  - counter(t, a)      : Konter-Multiplikator (wie gut t gegen a verteidigt).

Optimierung
-----------
Gesucht ist die Zuteilung x_t ≥ 0 (Anzahl Einheiten je Typ), die die gesamte
effektive Verteidigung maximiert, unter den Nebenbedingungen

    0 ≤ x_t ≤ available(t)        (Box-Schranke je Typ)
    Σ_t x_t ≤ capacity            (Gesamt-Verstärkungskapazität)

Da die Zielfunktion  Σ_t x_t * eff_def(t)  linear ist und nur Box- plus eine
Summenschranke vorliegen, ist dies ein kontinuierliches Rucksackproblem. Die
**greedy-Zuteilung in absteigender Reihenfolge von eff_def(t)** ist dafür
*beweisbar optimal* (Austauschargument). Das Ergebnis ist exakt, nicht
heuristisch.
"""
from __future__ import annotations

from typing import Dict

from .models import (
    Allocation,
    Buffs,
    DefenseStrategy,
    EnemyComposition,
    PlayerStats,
    TroopStats,
)


class GameProfile:
    """Spielspezifische Parameter: Truppen-Basiswerte + Konter-Matrix.

    counter[t][a] = Multiplikator, wenn Typ t gegen Angreifertyp a verteidigt.
    Werte > 1 bedeuten Vorteil, < 1 Nachteil.
    """

    def __init__(self, troops: Dict[str, TroopStats], counter: Dict[str, Dict[str, float]]):
        self.troops = troops
        self.counter = counter

    def counter_value(self, defender: str, attacker: str) -> float:
        return self.counter.get(defender, {}).get(attacker, 1.0)


def effective_defense_per_unit(
    troop_type: str,
    profile: GameProfile,
    buffs: Buffs,
    enemy: EnemyComposition,
) -> float:
    """Effektive Verteidigung einer einzelnen Einheit von `troop_type`."""
    stats = profile.troops[troop_type]
    base = stats.defense * buffs.defense_multiplier(troop_type) * buffs.health_multiplier()
    enemy_norm = enemy.normalized()
    if not enemy_norm:
        # Kein Angreiferprofil bekannt -> nur Buffs/Basiswerte, Konter neutral.
        weighted_counter = 1.0
    else:
        weighted_counter = sum(
            frac * profile.counter_value(troop_type, atk)
            for atk, frac in enemy_norm.items()
        )
    return base * weighted_counter


def compute_defense_strategy(
    player: PlayerStats,
    profile: GameProfile,
    buffs: Buffs,
    enemy: EnemyComposition,
) -> DefenseStrategy:
    """Berechnet die optimale Verteidigungszuteilung (exakter Greedy)."""
    # 1. Effektive Verteidigung pro Einheit je Typ.
    eff: Dict[str, float] = {
        t: effective_defense_per_unit(t, profile, buffs, enemy)
        for t in profile.troops
        if t in player.available_troops
    }

    capacity = player.reinforcement_capacity
    if capacity <= 0:
        # Keine explizite Kapazität -> gesamte verfügbare Armee einsetzbar.
        capacity = sum(player.available_troops.get(t, 0) for t in eff)

    # 2. Greedy: Typen mit höchster eff_def zuerst auffüllen.
    order = sorted(eff, key=lambda t: eff[t], reverse=True)

    allocations = []
    remaining = capacity
    notes = []
    for t in order:
        if remaining <= 0:
            break
        avail = int(player.available_troops.get(t, 0))
        take = min(avail, remaining)
        if take <= 0:
            continue
        allocations.append(
            Allocation(
                troop_type=t,
                count=take,
                effective_defense_per_unit=round(eff[t], 4),
            )
        )
        remaining -= take

    total = sum(a.total_effective_defense for a in allocations)

    if not allocations:
        notes.append("Keine verfügbaren Truppen für die Verteidigung gefunden.")
    else:
        best = allocations[0]
        notes.append(
            f"Priorität: {best.troop_type} (höchste effektive Verteidigung "
            f"≈ {best.effective_defense_per_unit:.2f}/Einheit gegen das "
            f"beobachtete Angreiferprofil)."
        )
    if remaining > 0 and capacity > 0:
        notes.append(
            f"{remaining} Verstärkungsplätze ungenutzt (zu wenige Truppen verfügbar)."
        )

    return DefenseStrategy(
        allocations=allocations,
        total_effective_defense=round(total, 2),
        notes=notes,
    )
