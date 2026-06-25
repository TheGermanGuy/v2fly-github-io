"""Tests für lokale Speicherung, Gemini-Parsing und Messenger-Formatierung
(alles ohne externe Abhängigkeiten/Netzwerk)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.models import PlayerStats  # noqa: E402
from agent.storage import StatsStore  # noqa: E402
from agent.gemini_analyzer import build_analysis_result, parse_gemini_json  # noqa: E402
from agent.messenger import format_strategy_message  # noqa: E402
from agent.strategy import GameProfile, compute_defense_strategy  # noqa: E402
from agent.models import Buffs, EnemyComposition, TroopStats  # noqa: E402


def test_store_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        store = StatsStore(os.path.join(d, "stats.db"))
        stats = PlayerStats(
            player_id="hero",
            power=123456,
            available_troops={"infantry": 500, "cavalry": 300},
            reinforcement_capacity=400,
        )
        store.save(stats)
        latest = store.latest("hero")
        assert latest is not None
        assert latest.power == 123456
        assert latest.available_troops["infantry"] == 500
        assert len(store.history("hero")) == 1


def test_parse_gemini_json_strips_codefence():
    raw = '```json\n{"player_id": "x", "power": 10}\n```'
    d = parse_gemini_json(raw)
    assert d["player_id"] == "x"
    assert d["power"] == 10


def test_build_analysis_result():
    raw = {
        "player_id": "hero",
        "power": 999,
        "available_troops": {"infantry": "100", "cavalry": 50},
        "reinforcement_capacity": "120",
        "buffs": {"global_defense": 0.25, "defense_by_type": {"infantry": 0.1}},
        "enemy_composition": {"cavalry": 0.7, "archer": 0.3},
    }
    res = build_analysis_result(raw)
    assert res.stats.power == 999
    assert res.stats.available_troops["infantry"] == 100
    assert res.stats.reinforcement_capacity == 120
    assert abs(res.buffs.defense_multiplier("infantry") - 1.35) < 1e-9
    assert abs(sum(res.enemy.normalized().values()) - 1.0) < 1e-9


def test_format_strategy_message():
    profile = GameProfile(
        {
            "infantry": TroopStats("infantry", 100, 140, 160),
            "cavalry": TroopStats("cavalry", 150, 100, 120),
        },
        {"infantry": {"cavalry": 1.3}, "cavalry": {"cavalry": 1.0}},
    )
    player = PlayerStats(
        player_id="hero",
        available_troops={"infantry": 100, "cavalry": 100},
        reinforcement_capacity=100,
    )
    s = compute_defense_strategy(player, profile, Buffs(), EnemyComposition({"cavalry": 1.0}))
    msg = format_strategy_message(s, "hero")
    assert "Verteidigungsstrategie" in msg
    assert "infantry" in msg
    assert "hero" in msg
