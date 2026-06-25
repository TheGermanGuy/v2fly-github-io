"""Tests für das Cloud-Vision-OCR-Parsing und das Evony-Profil
(ohne externe SDKs/Netzwerk)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.vision_cloud import ocr_text_to_raw, _to_int  # noqa: E402
from agent.config import load_profile  # noqa: E402
from agent.gemini_analyzer import build_analysis_result, build_schema_hint  # noqa: E402
from agent.strategy import compute_defense_strategy  # noqa: E402

EVONY_PROFILE = os.path.join(
    os.path.dirname(__file__), "..", "config", "game_profile.evony.json"
)


def test_to_int_suffixes():
    assert _to_int("12,345") == 12345
    assert _to_int("1.2M") == 1_200_000
    assert _to_int("3K") == 3000
    assert _to_int("2B") == 2_000_000_000


def test_ocr_text_to_raw_evony_labels():
    bundle = load_profile(EVONY_PROFILE)
    text = "\n".join(
        [
            "Power 15.2M",
            "Ground Troops 1,200,000",
            "Mounted Troops 800,000",
            "Ranged Troops 950,000",
            "Siege Machines 120,000",
            "March capacity 1,000,000",
        ]
    )
    raw = ocr_text_to_raw(text, labels=bundle.ocr_labels)
    assert raw["power"] == 15_200_000
    assert raw["available_troops"]["ground"] == 1_200_000
    assert raw["available_troops"]["mounted"] == 800_000
    assert raw["available_troops"]["siege"] == 120_000
    assert raw["reinforcement_capacity"] == 1_000_000


def test_evony_profile_loads_four_types():
    bundle = load_profile(EVONY_PROFILE)
    assert bundle.troop_types == ["ground", "mounted", "ranged", "siege"]
    assert bundle.game.startswith("Evony")
    assert "ground" in bundle.profile.troops


def test_evony_schema_hint_has_four_types():
    hint = build_schema_hint(["ground", "mounted", "ranged", "siege"])
    assert set(hint["available_troops"].keys()) == {"ground", "mounted", "ranged", "siege"}


def test_evony_end_to_end_strategy():
    bundle = load_profile(EVONY_PROFILE)
    raw = {
        "player_id": "lord",
        "power": 15_200_000,
        "available_troops": {
            "ground": 1_200_000,
            "mounted": 800_000,
            "ranged": 950_000,
            "siege": 120_000,
        },
        "reinforcement_capacity": 1_000_000,
        "buffs": {"global_defense": 0.4, "defense_by_type": {"ground": 0.2}},
        # Angreifer fährt mounted-lastige Rallye -> ground ist der beste Konter.
        "enemy_composition": {"mounted": 0.7, "ranged": 0.3},
    }
    res = build_analysis_result(raw)
    s = compute_defense_strategy(res.stats, bundle.profile, res.buffs, res.enemy)
    assert s.allocations[0].troop_type == "ground"
    assert sum(a.count for a in s.allocations) == 1_000_000
