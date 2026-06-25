"""Lokale Speicherung der extrahierten Spielerstatistiken (SQLite, stdlib)."""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import List, Optional

from .models import PlayerStats


class StatsStore:
    def __init__(self, db_path: str = "stats.db"):
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True) if Path(
            self.db_path
        ).parent != Path("") else None
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS player_stats (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id     TEXT NOT NULL,
                    power         INTEGER,
                    captured_at   REAL NOT NULL,
                    payload       TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_player ON player_stats(player_id, captured_at)"
            )

    def save(self, stats: PlayerStats, captured_at: Optional[float] = None) -> int:
        captured_at = captured_at if captured_at is not None else time.time()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO player_stats (player_id, power, captured_at, payload) "
                "VALUES (?, ?, ?, ?)",
                (
                    stats.player_id,
                    int(stats.power),
                    captured_at,
                    json.dumps(stats.to_dict(), ensure_ascii=False),
                ),
            )
            return int(cur.lastrowid)

    def latest(self, player_id: str) -> Optional[PlayerStats]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload FROM player_stats WHERE player_id = ? "
                "ORDER BY captured_at DESC LIMIT 1",
                (player_id,),
            ).fetchone()
        if row is None:
            return None
        return _stats_from_payload(row["payload"])

    def history(self, player_id: str, limit: int = 50) -> List[PlayerStats]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload FROM player_stats WHERE player_id = ? "
                "ORDER BY captured_at DESC LIMIT ?",
                (player_id, limit),
            ).fetchall()
        return [_stats_from_payload(r["payload"]) for r in rows]


def _stats_from_payload(payload: str) -> PlayerStats:
    d = json.loads(payload)
    return PlayerStats(
        player_id=d["player_id"],
        power=d.get("power", 0),
        available_troops=d.get("available_troops", {}),
        reinforcement_capacity=d.get("reinforcement_capacity", 0),
        raw=d.get("raw", {}),
    )
