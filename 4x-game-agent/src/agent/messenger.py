"""Messenger-Ausgabe der Verteidigungsstrategie über die Telegram-Bot-API.

Nutzt nur die HTTP-API (stdlib urllib), daher keine externen Abhängigkeiten.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Optional

from .models import DefenseStrategy


class TelegramMessenger:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    def _api_url(self) -> str:
        if not self.bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN ist nicht gesetzt.")
        return f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_text(self, text: str) -> dict:
        if not self.chat_id:
            raise RuntimeError("TELEGRAM_CHAT_ID ist nicht gesetzt.")
        payload = json.dumps(
            {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}
        ).encode("utf-8")
        req = urllib.request.Request(
            self._api_url(), data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Telegram-API-Fehler {e.code}: {e.read().decode()}") from e

    def send_strategy(self, strategy: DefenseStrategy, player_id: str = "") -> dict:
        return self.send_text(format_strategy_message(strategy, player_id))


def format_strategy_message(strategy: DefenseStrategy, player_id: str = "") -> str:
    """Reine Formatierungsfunktion (unit-testbar)."""
    lines = ["*🛡 Verteidigungsstrategie*"]
    if player_id:
        lines.append(f"_Spieler:_ `{player_id}`")
    lines.append("")
    if strategy.allocations:
        lines.append("*Empfohlene Aufstellung:*")
        for a in strategy.allocations:
            lines.append(
                f"• {a.troop_type}: *{a.count}* "
                f"(eff. Def ≈ {a.effective_defense_per_unit:.2f}/Einheit)"
            )
        lines.append("")
        lines.append(f"*Gesamte effektive Verteidigung:* {strategy.total_effective_defense:.2f}")
    else:
        lines.append("_Keine Aufstellung berechenbar._")
    if strategy.notes:
        lines.append("")
        for n in strategy.notes:
            lines.append(f"› {n}")
    return "\n".join(lines)
