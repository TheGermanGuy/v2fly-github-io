"""Orchestrierung des End-to-End-Ablaufs.

ADB-Mehrschirm-Erfassung (alle relevanten Stats) → Bildanalyse (Gemini oder
Cloud Vision) → Merge + Vollständigkeitsprüfung → lokale Speicherung →
Strategie → Telegram.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .adb_controller import AdbController
from .aggregate import assess_completeness, merge_raw_stats
from .config import load_profile
from .gemini_analyzer import GeminiAnalyzer, build_analysis_result
from .messenger import TelegramMessenger
from .storage import StatsStore
from .strategy import compute_defense_strategy
from .models import DefenseStrategy


class IncompleteStatsError(RuntimeError):
    def __init__(self, missing: List[str]):
        self.missing = missing
        super().__init__("Unvollständige Stats erfasst, fehlt: " + ", ".join(missing))


class Agent:
    def __init__(
        self,
        profile_path: str,
        db_path: str = "stats.db",
        adb_serial: Optional[str] = None,
        backend: str = "gemini",
    ):
        bundle = load_profile(profile_path)
        self.profile = bundle.profile
        self.menu_paths = bundle.menu_paths
        self.troop_types = bundle.troop_types
        self.ocr_labels = bundle.ocr_labels
        # Welche Screens für die vollständige Erfassung nacheinander angefahren
        # werden. Reihenfolge aus dem Profil (capture_screens) oder Default.
        self.capture_screens: List[str] = bundle.capture_screens or list(
            self.menu_paths.keys()
        )
        self.store = StatsStore(db_path)
        self.adb = AdbController(serial=adb_serial)
        self.messenger = TelegramMessenger()
        self.backend = backend
        self._analyzer = self._build_analyzer(backend)

    def _build_analyzer(self, backend: str):
        if backend == "cloud_vision":
            from .vision_cloud import CloudVisionOCR

            return CloudVisionOCR(labels=self.ocr_labels or None)
        if backend == "gemini_sdk":
            return GeminiAnalyzer(troop_types=self.troop_types)
        from .gemini_analyzer import GeminiRestAnalyzer

        return GeminiRestAnalyzer(troop_types=self.troop_types)

    def navigate_to(self, screen: str) -> None:
        steps = self.menu_paths.get(screen)
        if steps:
            self.adb.navigate(steps)

    # --- Schritt 1: ALLE relevanten Stats per ADB erfassen --------------------
    def capture_all_stats(
        self, screens: Optional[List[str]] = None, save_dir: Optional[str] = None
    ) -> Tuple[Dict, Dict[str, Dict]]:
        """Fährt nacheinander die relevanten Screens an, macht je einen ADB-
        Screenshot, analysiert ihn und merged alles zu einem vollständigen
        Roh-Dict.

        Rückgabe: (merged_raw, per_screen_raw).
        """
        screens = screens or self.capture_screens
        per_screen: Dict[str, Dict] = {}
        raws: List[Dict] = []
        for screen in screens:
            self.navigate_to(screen)
            png = self.adb.screencap_png()
            if save_dir:
                import os

                os.makedirs(save_dir, exist_ok=True)
                with open(os.path.join(save_dir, f"{screen}.png"), "wb") as f:
                    f.write(png)
            raw = self._analyzer.analyze(png)
            per_screen[screen] = raw
            raws.append(raw)
        merged = merge_raw_stats(raws)
        return merged, per_screen

    # --- Voller Lauf ----------------------------------------------------------
    def run_once(
        self,
        send: bool = True,
        save_dir: Optional[str] = None,
        require_complete: bool = True,
    ) -> DefenseStrategy:
        # 1. Erfassung ALLER relevanten realen Stats per ADB (mehrere Screens).
        merged, _ = self.capture_all_stats(save_dir=save_dir)

        # 2. Vollständigkeit sicherstellen, BEVOR gerechnet wird.
        complete, missing = assess_completeness(merged, self.troop_types)
        if require_complete and not complete:
            raise IncompleteStatsError(missing)

        result = build_analysis_result(merged)

        # 3. Lokal speichern.
        self.store.save(result.stats)

        # 4. Strategie + Ausgabe.
        strategy = compute_defense_strategy(
            player=result.stats,
            profile=self.profile,
            buffs=result.buffs,
            enemy=result.enemy,
        )
        if send:
            self.messenger.send_strategy(strategy, player_id=result.stats.player_id)
        return strategy
