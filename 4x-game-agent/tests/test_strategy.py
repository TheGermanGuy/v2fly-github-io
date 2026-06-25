"""Tests für den deterministischen Strategie-Rechner.

Verifiziert insbesondere die *Optimalität* der Greedy-Zuteilung (das kontinuier-
liche Rucksackproblem) gegen eine erschöpfende Referenz-Suche.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.models import Buffs, EnemyComposition, PlayerStats, TroopStats  # noqa: E402
from agent.strategy import (  # noqa: E402
    GameProfile,
    compute_defense_strategy,
    effective_defense_per_unit,
)


def make_profile():
    troops = {
        "infantry": TroopStats("infantry", 100, 140, 160),
        "cavalry": TroopStats("cavalry", 150, 100, 120),
        "archer": TroopStats("archer", 160, 90, 100),
    }
    counter = {
        "infantry": {"infantry": 1.0, "cavalry": 1.3, "archer": 0.8},
        "cavalry": {"infantry": 0.8, "cavalry": 1.0, "archer": 1.3},
        "archer": {"infantry": 1.3, "cavalry": 0.8, "archer": 1.0},
    }
    return GameProfile(troops, counter)


def test_effective_defense_with_buffs_and_counter():
    profile = make_profile()
    buffs = Buffs(global_defense=0.5, defense_by_type={"infantry": 0.1})
    enemy = EnemyComposition({"cavalry": 1.0})  # reiner Kavallerie-Angriff
    # infantry kontert cavalry mit 1.3; mult = 1 + 0.5 + 0.1 = 1.6
    expected = 140 * 1.6 * 1.3
    got = effective_defense_per_unit("infantry", profile, buffs, enemy)
    assert abs(got - expected) < 1e-9


def test_greedy_prioritizes_best_counter():
    profile = make_profile()
    buffs = Buffs()
    enemy = EnemyComposition({"cavalry": 1.0})
    player = PlayerStats(
        player_id="p1",
        available_troops={"infantry": 1000, "cavalry": 1000, "archer": 1000},
        reinforcement_capacity=1000,
    )
    s = compute_defense_strategy(player, profile, buffs, enemy)
    # infantry hat den besten Konter gegen cavalry -> sollte zuerst/voll kommen.
    assert s.allocations[0].troop_type == "infantry"
    assert s.allocations[0].count == 1000
    assert sum(a.count for a in s.allocations) == 1000


def _brute_force_best(player, profile, buffs, enemy, step):
    """Erschöpfende Referenz über ein Raster, um Optimalität zu prüfen."""
    eff = {
        t: effective_defense_per_unit(t, profile, buffs, enemy)
        for t in profile.troops
    }
    types = list(player.available_troops)
    cap = player.reinforcement_capacity
    best = -1.0
    for combo in itertools.product(*[range(0, player.available_troops[t] + 1, step) for t in types]):
        if sum(combo) > cap:
            continue
        val = sum(c * eff[t] for c, t in zip(combo, types))
        best = max(best, val)
    return best


def test_greedy_matches_bruteforce_optimum():
    profile = make_profile()
    buffs = Buffs(global_defense=0.2, defense_by_type={"archer": 0.4})
    enemy = EnemyComposition({"infantry": 0.5, "cavalry": 0.3, "archer": 0.2})
    player = PlayerStats(
        player_id="p1",
        available_troops={"infantry": 20, "cavalry": 20, "archer": 20},
        reinforcement_capacity=30,
    )
    s = compute_defense_strategy(player, profile, buffs, enemy)
    brute = _brute_force_best(player, profile, buffs, enemy, step=1)
    assert abs(s.total_effective_defense - round(brute, 2)) < 1e-6


def test_capacity_limits_allocation():
    profile = make_profile()
    player = PlayerStats(
        player_id="p1",
        available_troops={"infantry": 100, "cavalry": 100, "archer": 100},
        reinforcement_capacity=150,
    )
    s = compute_defense_strategy(player, profile, Buffs(), EnemyComposition({"cavalry": 1.0}))
    assert sum(a.count for a in s.allocations) == 150


def test_no_troops_returns_note():
    profile = make_profile()
    player = PlayerStats(player_id="p1", available_troops={}, reinforcement_capacity=0)
    s = compute_defense_strategy(player, profile, Buffs(), EnemyComposition({}))
    assert s.allocations == []
    assert any("Keine" in n for n in s.notes)


def test_unused_capacity_noted():
    profile = make_profile()
    player = PlayerStats(
        player_id="p1",
        available_troops={"infantry": 10},
        reinforcement_capacity=100,
    )
    s = compute_defense_strategy(player, profile, Buffs(), EnemyComposition({"cavalry": 1.0}))
    assert sum(a.count for a in s.allocations) == 10
    assert any("ungenutzt" in n for n in s.notes)
