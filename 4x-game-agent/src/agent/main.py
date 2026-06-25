"""CLI-Einstiegspunkt für den 4x-game-agent."""
from __future__ import annotations

import argparse
import sys

from .pipeline import Agent
from .messenger import format_strategy_message


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="4x-game-agent")
    parser.add_argument("--profile", required=True, help="Pfad zur Spielprofil-JSON")
    parser.add_argument("--db", default="stats.db", help="Pfad zur lokalen SQLite-DB")
    parser.add_argument("--serial", default=None, help="ADB-Geräte-Serial / host:port")
    parser.add_argument("--screen", default=None, help="Vorab-Navigation zu Menü (z. B. 'keep')")
    parser.add_argument(
        "--backend",
        default="gemini",
        choices=["gemini", "gemini_sdk", "cloud_vision"],
        help="Bildanalyse-Backend: gemini (REST, Default), gemini_sdk oder cloud_vision (Composio/Google Cloud Vision)",
    )
    parser.add_argument("--no-send", action="store_true", help="Telegram-Versand überspringen")
    args = parser.parse_args(argv)

    agent = Agent(
        profile_path=args.profile,
        db_path=args.db,
        adb_serial=args.serial,
        backend=args.backend,
    )
    strategy = agent.run_once(screen=args.screen, send=not args.no_send)
    print(format_strategy_message(strategy))
    return 0


if __name__ == "__main__":
    sys.exit(main())
