"""Tests für die mehrstufige Stats-Erfassung: Merge + Vollständigkeitsprüfung."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.aggregate import merge_raw_stats, assess_completeness  # noqa: E402

TROOPS = ["ground", "mounted", "ranged", "siege"]


def test_merge_combines_multiple_screens():
    # Screen 1: Monarch-Profil (Power), Screen 2: Truppen, Screen 3: Buffs.
    profile_scr = {"player_id": "Lord", "power": 15_200_000}
    troops_scr = {
        "available_troops": {"ground": 1_200_000, "mounted": 800_000, "ranged": 950_000, "siege": 120_000},
        "reinforcement_capacity": 1_000_000,
    }
    buffs_scr = {"buffs": {"global_defense": 0.45, "defense_by_type": {"ground": 0.2}}}
    merged = merge_raw_stats([profile_scr, troops_scr, buffs_scr])
    assert merged["player_id"] == "Lord"
    assert merged["power"] == 15_200_000
    assert merged["reinforcement_capacity"] == 1_000_000
    assert merged["available_troops"]["mounted"] == 800_000
    assert merged["buffs"]["global_defense"] == 0.45
    assert merged["buffs"]["defense_by_type"]["ground"] == 0.2


def test_merge_does_not_overwrite_real_value_with_zero():
    s1 = {"power": 999}
    s2 = {"power": 0}
    assert merge_raw_stats([s1, s2])["power"] == 999


def test_completeness_detects_missing_fields():
    incomplete = {"power": 0, "available_troops": {"ground": 100}}
    complete, missing = assess_completeness(incomplete, TROOPS)
    assert not complete
    assert "power" in missing
    assert "reinforcement_capacity" in missing
    assert "available_troops.mounted" in missing


def test_completeness_passes_when_all_present():
    full = {
        "power": 1,
        "reinforcement_capacity": 1,
        "available_troops": {t: 1 for t in TROOPS},
    }
    complete, missing = assess_completeness(full, TROOPS)
    assert complete
    assert missing == []


def test_completeness_require_buffs():
    full_no_buffs = {
        "power": 1,
        "reinforcement_capacity": 1,
        "available_troops": {t: 1 for t in TROOPS},
        "buffs": {"global_defense": 0.0, "defense_by_type": {}},
    }
    complete, missing = assess_completeness(full_no_buffs, TROOPS, require_buffs=True)
    assert not complete
    assert "buffs" in missing
