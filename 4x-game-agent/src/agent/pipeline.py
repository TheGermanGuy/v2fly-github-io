"""Orchestrierung des End-to-End-Ablaufs.

ADB-Screenshot → Bildanalyse (Gemini oder Cloud Vision) → lokale Speicherung →
Strategie → Telegram.
"""
from __future__ import annotations

from typing import Optional

from .adb_controller import AdbController
from .config import load_profile
from .gemini_analyzer import GeminiAnalyzer, build_analysis_result
from .messenger import TelegramMessenger
from .storage import StatsStore
from .strategy import compute_defense_strategy
from .models import DefenseStrategy


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
        # Default: REST-Pfad (reine Standardbibliothek, kein gRPC/SDK nötig).
        from .gemini_analyzer import GeminiRestAnalyzer

        return GeminiRestAnalyzer(troop_types=self.troop_types)

    def navigate_to(self, screen: str) -> None:
        steps = self.menu_paths.get(screen)
        if steps:
            self.adb.navigate(steps)

    def run_once(self, screen: Optional[str] = None, send: bool = True) -> DefenseStrategy:
        if screen:
            self.navigate_to(screen)
        png = self.adb.screencap_png()
        raw = self._analyzer.analyze(png)
        result = build_analysis_result(raw)

        self.store.save(result.stats)

        strategy = compute_defense_strategy(
            player=result.stats,
            profile=self.profile,
            buffs=result.buffs,
            enemy=result.enemy,
        )
        if send:
            self.messenger.send_strategy(strategy, player_id=result.stats.player_id)
        return strategy
