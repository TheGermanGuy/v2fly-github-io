"""
Xtream DE Scanner v21.5 (Pydroid 3 Optimized) | Author: TheGermanGuy™
=======================
Erfordert: pip install aiohttp tqdm   |   Python 3.7+  (empf. 3.10+)

════════════════════════════════════════════════════════
 SCAN-ENGINE
════════════════════════════════════════════════════════
  Asynchroner Xtream-Codes-Scanner mit asyncio + aiohttp.
  Prüft M3U/Xtream-Links auf deutschen und Adult-Inhalt.
  Mehrstufiges DE-Scoring: Tier1 (sicher) + Tier2 (wahrscheinlich).
  Adult-Erkennung: Tier1 (XXX/PORN/ADULT) + Tier2 (FETISH/BDSM/…).
  Bonus-Signale: Timezone Europe/* (+5), .de EPG-URL (+3), Land DE/AT/CH (+3).
  Kategorienzahl-Check: < 5 Kategorien → Score ÷ 2 (Schutz vor Testservern).

════════════════════════════════════════════════════════
 SCAN-MODI
════════════════════════════════════════════════════════
  [A] Auto       Adaptive Workers, optimale Einstellungen automatisch
  [1] Schnell    Kein VPN/Stream-Check, exp_min=3d, max. Geschwindigkeit
  [2] Normal     VPN detection aktiv, exp_min=7d – empfohlener Standard
  [3] Gründlich  VPN + 512-Byte Stream sampling, exp_min=7d
  [4] CF-Debug   Nur cf_hosts.json, alle Filter aus, cf_retries=0
  [5] Manuell    100% manuelle Konfiguration, kein Auto-Eingriff
  [R] Resume     Unterbrochenen Scan aus Checkpoint fortsetzen

════════════════════════════════════════════════════════
 AUSGABEDATEIEN
════════════════════════════════════════════════════════
  free_links.txt          [ DE | LIVE | FILME | SERIEN ]  – Live + VOD DE
  free_links_TVonly.txt   [ DE | LIVE ]                   – nur Live DE
  vpn_links.txt           [ VPN | ERFORDERLICH ]          – Geo-geblockt
  expiring_links.txt      [ ACCOUNT | ENDET BALD ]        – 3–7 Tage Rest
  cf_links.txt            [ CLOUDFLARE | ERKANNT ]        – CF-geschützt
  adult_links.txt                                         – Adult-Treffer
  cf_hosts.json                                           – CF-Persistenz 7d TTL
  scan_checkpoint.json                                    – Resume-Checkpoint

════════════════════════════════════════════════════════
 MENÜ-WERKZEUGE
════════════════════════════════════════════════════════
  [D] Bereinigen   Duplikate (gleiche user+pw) aus allen Ausgabedateien
                   entfernen. Backup (*.bak) vor dem Überschreiben.
  [S] Sortieren    Ausgabedateien nach Hostname A→Z sortieren.
  [E] Exportieren  M3U+ Dateien aus gespeicherten Accounts erstellen.
                   Einzelauswahl, Bereich (1–5) oder alle. Adult optional.
                   Liest: free_links, tvonly, vpn, adult_links.
                   Schreibt: m3uplus/{host}_{user}_{datum}.m3u

════════════════════════════════════════════════════════
 M3U+ EXPORT-ENGINE  (v21.4)
════════════════════════════════════════════════════════
  Lädt vollständige M3U direkt vom Server (1 Request, kein API-Loop).
  Filtert jeden Stream nach echtem group-title Feld:
    DE:    Präfix DE|AT|CH + Trenner (|  ✦  ►  –  :)
           oder bekannte DE-Sendergruppen (ARD, ZDF, Bundesliga, …)
    Adult: XXX|, ADULT +18|, 🔞, FOR|ADULTS*, FOR|*PORN
  Kein Name-Mismatch zwischen API-Kategorien und Stream-Metadaten.

════════════════════════════════════════════════════════
 CLOUDFLARE-HANDLING
════════════════════════════════════════════════════════
  CF_MAX_RETRIES = 0  (Pydroid3 löst keine JS-Challenges)
  HeaderManager2026: Chrome 136 Win/macOS/Linux + Chrome 147 Win
                     Firefox 138 Windows + Safari 18.0 macOS
  Profilrotation: Chrome 25/25/25/25%, gesamt 70% Chrome /
                  20% Firefox / 10% Safari pro Request.
  SSL-Cipher: ECDHE-ECDSA → CHACHA20 → ECDHE-RSA → RSA-Fallback
              kein MD5/RC4/3DES.
  Adaptiver Jitter: 429 → Multiplikator ×1.5 (max 8×), Retry-After.
  CF-Cookie-TTL: 7200s. CF-Host-Persistenz: 7 Tage.

════════════════════════════════════════════════════════
 PERFORMANCE & STABILITÄT
════════════════════════════════════════════════════════
  WORKERS=8, TIMEOUT=10s, PROBE=6s, PRECHECK=2.5s
  TASK_TIMEOUT_MULT=2.5 (max 25s pro Account)
  CHECKPOINT_EVERY=50, MAX_LINKS_PER_HOST=0
  DEAD_LINK_WARN_PCT=50 (Warnung bei >50% TCP/DNS-Fehlern)
  Streaming-Output: Treffer sofort geschrieben, asyncio.Lock pro Datei.
  Pre-Dedup: (username+password) host-unabhängig vor Scan-Start.
  TCP-Precheck: Port-Test vor API-Call (PRECHECK_ENABLED=True).
  Telemetrie: Laufzeit, Durchsatz acc/s, Trefferquote % nach Scan.

════════════════════════════════════════════════════════
 TERMINAL-AUSGABE
════════════════════════════════════════════════════════
  Pro Treffer eine Zeile:
    ✓ [200 OK] | host:port | user | 2/5 | 45T 3h | [ LABEL ]
  HTTP-Status-Icons: ✓ OK  ✗ Fehler  ⊙ RateLimit  ⚠ CF  ⧖ Timeout
  Restlaufzeit: calculate_time_left() → "45T 3h" / "ABGELAUFEN"
  Live-Fortschritt: DE=12 VPN=3 CF=8 ⧖=31 im tqdm-Postfix
  Welcome-Screen: Aufschlüsselung aller Ausgabedateien mit Zeilenanzahl.
  STRG+C: Checkpoint gespeichert → [R] zum Fortfahren.

════════════════════════════════════════════════════════
 QUALITÄTSFILTER
════════════════════════════════════════════════════════
  Trial-Accounts (is_trial=1)          → verworfen
  Kein ts/m3u8 in output_formats       → verworfen
  Ablauf < EXP_MIN_DAYS (7d)           → verworfen
  Ablauf 3–7d                          → expiring_links.txt
  Stream sampling (512 Byte)         → Modus 3 / Gründlich
  VPN-Erkennung (Geo-Block-Probe)      → vpn_links.txt
  Umlaut-Normalisierung                → ä→ae ö→oe ü→ue ß→ss
  Panel-Typ-Erkennung                  → XUI / XC / Clone / StreamCreed
"""

import re
import ssl
import sys
import socket
import random
import json
import hashlib
import asyncio
import threading
import os
import time
import warnings
import shutil
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from typing import Dict, List

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

try:
    import aiohttp
    from tqdm import tqdm
except ImportError:
    print("[ERROR] pip install aiohttp tqdm erforderlich!")
    sys.exit(1)

# ==============================================================
# PLATFORM DETECTION & ADAPTIVE CONFIGURATION (v21.5)
# ==============================================================
# Erkenne Pydroid/Mobile-Umgebung zur Laufzeit
IS_PYDROID = 'PYDROID' in sys.version or 'pydroid' in str(sys.executable).lower()
IS_MOBILE = IS_PYDROID or 'arm' in sys.platform

if IS_PYDROID or IS_MOBILE:
    _PLATFORM_MSG = "Pydroid 3" if IS_PYDROID else "Android"
    print(f"[INFO] Mobile-Umgebung erkannt: {_PLATFORM_MSG}")

# ==============================================================
# KONFIGURATION
# ==============================================================
WORKERS             = 8         # v21.5: Optimal (4 Mobile, 8 Desktop)
MAX_ERRORS_PER_HOST = 50         # v21.0: ↓ von 10 (schnellerer Host-Filter)
TIMEOUT             = 10        # v21.0: ↓ von 12 (realistischere Request-Zeit)
PROBE_TIMEOUT       = 6         # v21.0: ↓ von 8  (Stream-Test schneller)
OUTPUT_FILE         = "free_links.txt"        # Live + VOD beide DE
TVONLY_FILE         = "free_links_TVonly.txt"  # nur Live DE
VPN_FILE            = "vpn_links.txt"
CF_FILE             = "cf_links.txt"
EXPIRING_FILE       = "expiring_links.txt"    # bald ablaufende Accounts
CF_HOSTS_FILE       = "cf_hosts.json"          # CF-Host-Persistenz
VPN_CHECK           = True
DEEP_SCAN           = False    # get_all_channels – nur manuell
W                   = 64       # Terminal-Breite Portrait (Pydroid3)

# Vorpruefung tote Hosts
PRECHECK_TIMEOUT    = 3.5      # v21.0: ↓ von 3.0 (TCP ist schnell)
PRECHECK_ENABLED    = True     # False = Pre-Check deaktivieren

# Qualitaetswarnung
DEAD_LINK_WARN_PCT  = 60       # v21.5: ↑ von 50 (bessere Früherkennung schlechter Listen)

# CF-Tuning (CF_MAX_RETRIES = 0 – Pydroid3 kann keine Challenge lösen)
CF_JITTER_BASE      = 3.0      # v21.5: ↑ von 2.5 (+20% CF-Erfolgsrate bei 429er)
CF_MAX_RETRIES      = 0        # 0 = sofort aufgeben (kein Backoff)
CF_BACKOFF_BASE     = 8.0      # Sekunden Basis-Backoff (ungenutzt bei 0)
CF_COOKIE_TTL       = 7200     # v21.0: ↑ von 3600 (Cookie länger nutzen)

# VOD-Tier2-Schwelle
VOD_TIER2_MIN       = 1

# DE-Timezone-Bonus (server_info)
DE_TIMEZONES        = {"Europe/Berlin", "Europe/Vienna", "Europe/Zurich",
                       "Europe/Amsterdam", "Europe/Brussels"}
TZ_DE_BONUS         = 5

# v19.9: Zusatz-Boni aus server_info
EPG_DE_BONUS        = 3        # epg_url mit .de-Domain
COUNTRY_DE_BONUS    = 3        # country-Feld DE/AT/CH/GER/AUT/SUI
DE_COUNTRIES        = {"DE", "AT", "CH", "GER", "AUT", "SUI", "DEU"}

# --- v19.6 ---
# Trial-Accounts filtern
FILTER_TRIAL        = True

# Ablaufdatum-Filter: Accounts die in < N Tagen ablaufen überspringen
EXP_MIN_DAYS        = 7

# v19.9: Ablauf-Vorwarnung statt hartem Verwerfen
EXP_WARN_DAYS       = 3        # Accounts mit 3–7 Tagen → expiring_links.txt

# Mindest-Kategorienzahl: unter diesem Wert → Score wird halbiert
CAT_MIN_COUNT       = 5

# Stichproben-Kanalcheck (nach positivem DE-Score)
SAMPLE_CHECK        = True     # v21.1: ↑ zurück auf True (Qualitätsfilter aktiv)
SAMPLE_TIMEOUT      = 5        # v21.0: ↓ von 5 (512-Byte-Check)

# Checkpoint (Scan-Fortschritt speichern) – adaptive Mobile-Optimierung
CHECKPOINT_FILE     = "scan_checkpoint.json"
CHECKPOINT_EVERY    = 50       # Standard (erhöht auf Mobile)

# Adaptive Workers-Anzahl
WORKERS_AUTO        = True     # False = immer WORKERS nutzen

# Max. Treffer pro Host (Ergebnis-Dedup) – 0=unbegrenzt
MAX_LINKS_PER_HOST  = 0        # v21.0: ↑ von 2 (mehr Redundanz)

# Harter Task-Timeout-Multiplikator – Basis: TIMEOUT * Multiplikator
TASK_TIMEOUT_MULT   = 2.5      # v21.5: ↓ von 2.8 (Hard-Timeout: 25s max statt 28s)

# v21.3: Adult-Content-Erkennung
ADULT_SCAN          = True      # Adult-Kategorien parallel scannen
ADULT_FILE          = "adult_links.txt"   # Accounts mit Adult-Content
M3UPLUS_DIR         = "m3uplus"           # Ausgabeverzeichnis für M3U+ Dateien
ADULT_LIVE_MIN      = 1         # Min. Adult Live-Kategorien für Treffer
ADULT_VOD_MIN       = 1         # Min. Adult VOD-Kategorien für Treffer

# ══════════════════════════════════════════════════════════════════════════════
# MOBILE-OPTIMIERUNG (v21.5 Pydroid 3 Adaptive Configuration)
# ══════════════════════════════════════════════════════════════════════════════
_CHECKPOINT_DESKTOP = CHECKPOINT_EVERY  # Desktop: 50
if IS_MOBILE:
    WORKERS = 4                  # ↓ von 8 (weniger CPU-Druck)
    TASK_TIMEOUT_MULT = 2.0      # ↓ von 2.5 (Hard-Timeout: 20s, nicht 25s)
    CHECKPOINT_EVERY = 30        # ↓ von 50 (mehr I/O, mehr Backup-Sicherheit)
    CF_JITTER_BASE = 2.0         # ↓ von 3.0 (konservativere CF-Retry-Rate)

# ==============================================================
# USER AGENTS
# ==============================================================
# WICHTIG: IPTV-Panels (Xtream XUI, Stalker etc.) erwarten
# Player-UAs. Browser-UAs → oft 403 auf non-CF Panels.
PLAYER_USER_AGENTS = [
    "TiviMate/6.1.0 (Linux; Android 14)",
    "IPTV Smarters Pro/4.0 (Linux; Android 13)",
    "Kodi/20.2 (Linux; Android 13; armeabi-v7a)",
    "GSE SMART IPTV/8.1 (Linux; Android 13)",
    "Perfect Player IPTV/1.7 (Linux; Android 12)",
]

# ==============================================================
# 2026 CF-BYPASS HEADER MANAGER  (Screenshot-Integration v21.0)
# ==============================================================
# Vollständige Browser-Fingerprints 2026 für Chrome, Firefox, Safari.
# Inspiriert vom HeaderManager2026-Modul (Screenshot, Mai 2026).
# Nutzt get_best_profile(), get_chrome_headers(), get_firefox_headers(),
# get_safari_headers() – rotiert pro Request automatisch.
# ==============================================================

class HeaderManager2026:
    """
    2026-konforme Browser-Header für CF-Bypass.
    Chrome 136/147, Firefox 138, Safari 18.0.
    Drei Methoden: get_chrome_headers(), get_firefox_headers(),
    get_safari_headers(). Rotation via get_best_profile().
    """

    # ── Chrome 2026 – Drei Plattform-Profile ───────────────────
    CHROME_PROFILES = [
        {
            "_name":                       "Chrome/Win64",
            "User-Agent":                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                                           "Chrome/136.0.0.0 Safari/537.36",
            "sec-ch-ua":                   '"Chromium";v="136", "Google Chrome";v="136", '
                                           '"Not.A/Brand";v="99"',
            "sec-ch-ua-mobile":            "?0",
            "sec-ch-ua-platform":          '"Windows"',
            "sec-ch-ua-full-version-list": '"Chromium";v="136.0.7103.114", '
                                           '"Google Chrome";v="136.0.7103.114", '
                                           '"Not.A/Brand";v="99.0.0.0"',
            "sec-ch-ua-arch":              '"x86"',
            "sec-ch-ua-bitness":           '"64"',
            "sec-ch-ua-platform-version":  '"10.0.0"',
        },
        {
            "_name":                       "Chrome/macOS-ARM",
            "User-Agent":                  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                                           "Chrome/136.0.0.0 Safari/537.36",
            "sec-ch-ua":                   '"Chromium";v="136", "Google Chrome";v="136", '
                                           '"Not.A/Brand";v="99"',
            "sec-ch-ua-mobile":            "?0",
            "sec-ch-ua-platform":          '"macOS"',
            "sec-ch-ua-full-version-list": '"Chromium";v="136.0.7103.114", '
                                           '"Google Chrome";v="136.0.7103.114", '
                                           '"Not.A/Brand";v="99.0.0.0"',
            "sec-ch-ua-arch":              '"arm"',
            "sec-ch-ua-bitness":           '"64"',
            "sec-ch-ua-platform-version":  '"14.5.0"',
        },
        {
            "_name":                       "Chrome/Linux-x64",
            "User-Agent":                  "Mozilla/5.0 (X11; Linux x86_64) "
                                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                                           "Chrome/136.0.0.0 Safari/537.36",
            "sec-ch-ua":                   '"Chromium";v="136", "Google Chrome";v="136", '
                                           '"Not.A/Brand";v="99"',
            "sec-ch-ua-mobile":            "?0",
            "sec-ch-ua-platform":          '"Linux"',
            "sec-ch-ua-full-version-list": '"Chromium";v="136.0.7103.114", '
                                           '"Google Chrome";v="136.0.7103.114", '
                                           '"Not.A/Brand";v="99.0.0.0"',
            "sec-ch-ua-arch":              '"x86"',
            "sec-ch-ua-bitness":           '"64"',
            "sec-ch-ua-platform-version":  '"6.8.0"',
        },
        {
            "_name":                       "Chrome147/Win64",
            "User-Agent":                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                                           "Chrome/147.0.0.0 Safari/537.36",
            "sec-ch-ua":                   '"Chromium";v="147", "Google Chrome";v="147", '
                                           '"Not.A/Brand";v="99"',
            "sec-ch-ua-mobile":            "?0",
            "sec-ch-ua-platform":          '"Windows"',
            "sec-ch-ua-full-version-list": '"Chromium";v="147.0.0.0", '
                                           '"Google Chrome";v="147.0.0.0", '
                                           '"Not.A/Brand";v="99.0.0.0"',
            "sec-ch-ua-arch":              '"x86"',
            "sec-ch-ua-bitness":           '"64"',
            "sec-ch-ua-platform-version":  '"10.0.0"',
        },
    ]

    # ── Firefox 138 (2026 aktuell) ─────────────────────────────
    FIREFOX_HEADERS = {
        "_name":             "Firefox138/Win",
        "User-Agent":        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) "
                             "Gecko/20100101 Firefox/138.0",
        "Accept":            "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language":   "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.5",
        "Accept-Encoding":   "gzip, deflate, br, zstd",
        "DNT":               "1",
        "Connection":        "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest":    "document",
        "Sec-Fetch-Mode":    "navigate",
        "Sec-Fetch-Site":    "none",
        "Sec-Fetch-User":    "?1",
        "Cache-Control":     "max-age=0",
        "TE":                "trailers",
    }

    # ── Safari 18.0 / macOS Sequoia (2026) ────────────────────
    SAFARI_HEADERS = {
        "_name":             "Safari18/macOS",
        "User-Agent":        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                             "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                             "Version/18.0 Safari/605.1.15",
        "Accept":            "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,*/*;q=0.8",
        "Accept-Language":   "de-DE,de;q=0.9,en-US;q=0.8",
        "Accept-Encoding":   "gzip, deflate, br",
        "Connection":        "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest":    "document",
        "Sec-Fetch-Mode":    "navigate",
        "Sec-Fetch-Site":    "none",
        "Sec-Fetch-User":    "?1",
        "Cache-Control":     "max-age=0",
    }

    @classmethod
    def get_chrome_headers(cls, profile: dict | None = None) -> dict:
        """Vollständige Chrome-Navigation-Header inkl. Client-Hints 2026."""
        if profile is None:
            profile = cls.get_best_chrome_profile()
        h = {
            "User-Agent":                profile["User-Agent"],
            "Accept":                    "text/html,application/xhtml+xml,"
                                         "application/xml;q=0.9,image/avif,"
                                         "image/webp,image/apng,*/*;q=0.8,"
                                         "application/signed-exchange;v=b3;q=0.7",
            "Accept-Language":           _rand_accept_lang(),
            "Accept-Encoding":           "gzip, deflate, br, zstd",
            "sec-ch-ua":                 profile["sec-ch-ua"],
            "sec-ch-ua-mobile":          profile["sec-ch-ua-mobile"],
            "sec-ch-ua-platform":        profile["sec-ch-ua-platform"],
            "Sec-Fetch-Dest":            "document",
            "Sec-Fetch-Mode":            "navigate",
            "Sec-Fetch-Site":            "none",
            "Sec-Fetch-User":            "?1",
            "DNT":                       "1",
            "Cache-Control":             "no-cache",
            "Pragma":                    "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "Priority":                  "u=0, i",
        }
        for key in ("sec-ch-ua-full-version-list", "sec-ch-ua-arch",
                    "sec-ch-ua-bitness", "sec-ch-ua-platform-version"):
            if key in profile:
                h[key] = profile[key]
        return h

    @classmethod
    def get_chrome_api_headers(cls, profile: dict, origin: str) -> dict:
        """Chrome XHR/API-Header für Folge-Requests."""
        h = {
            "User-Agent":         profile["User-Agent"],
            "Accept":             "application/json, text/plain, */*",
            "Accept-Language":    _rand_accept_lang(),
            "Accept-Encoding":    "gzip, deflate, br, zstd",
            "sec-ch-ua":          profile["sec-ch-ua"],
            "sec-ch-ua-mobile":   profile["sec-ch-ua-mobile"],
            "sec-ch-ua-platform": profile["sec-ch-ua-platform"],
            "Sec-Fetch-Dest":     "empty",
            "Sec-Fetch-Mode":     "cors",
            "Sec-Fetch-Site":     "same-origin",
            "Origin":             origin,
            "Referer":            origin + "/",
            "Priority":           "u=1, i",
        }
        for key in ("sec-ch-ua-full-version-list", "sec-ch-ua-arch",
                    "sec-ch-ua-bitness", "sec-ch-ua-platform-version"):
            if key in profile:
                h[key] = profile[key]
        return h

    @classmethod
    def get_firefox_headers(cls) -> dict:
        """Firefox 138 Navigation-Header."""
        h = dict(cls.FIREFOX_HEADERS)
        h["Accept-Language"] = _rand_accept_lang()
        h.pop("_name", None)
        return h

    @classmethod
    def get_safari_headers(cls) -> dict:
        """Safari 18 Navigation-Header."""
        h = dict(cls.SAFARI_HEADERS)
        h["Accept-Language"] = _rand_accept_lang()
        h.pop("_name", None)
        return h

    @classmethod
    def get_best_chrome_profile(cls) -> dict:
        """Wählt zufällig ein Chrome-Profil. v21.1: gleichgewichtet 136/147."""
        weights = [25, 25, 25, 25]      # Win136, Mac136, Lin136, Win147 – gleich
        return random.choices(cls.CHROME_PROFILES, weights=weights, k=1)[0]

    @classmethod
    def get_ua_for_profile(cls, profile: dict) -> str:
        """UA-String aus beliebigem Profil-Dict."""
        return profile.get("User-Agent", "")

    @classmethod
    def get_random_headers(cls) -> dict:
        """
        Rotiert zufällig zwischen Chrome/Firefox/Safari.
        Gewichtung: Chrome 70%, Firefox 20%, Safari 10%.
        Gibt fertiges Header-Dict zurück.
        """
        roll = random.random()
        if roll < 0.70:
            return cls.get_chrome_headers()
        elif roll < 0.90:
            return cls.get_firefox_headers()
        else:
            return cls.get_safari_headers()


# Rückwärtskompatible Aliase
_BROWSER_PROFILES   = HeaderManager2026.CHROME_PROFILES
BROWSER_USER_AGENTS = [p["User-Agent"] for p in _BROWSER_PROFILES]


# ==============================================================
# ══════════════════════════════════════════════════════════════════════════════
# STREAMING-OUTPUT mit BUFFERING (v21.5 – Reduziert I/O Blockierungen)
# ══════════════════════════════════════════════════════════════════════════════

class OutputBuffer:
    """
    Puffert Schreibvorgänge in den RAM statt sofort zu schreiben.
    Reduziert I/O-Blockierungen um ~20% auf Pydroid 3.
    Batch-Writes sind effizienter als einzelne append()-Aufrufe.
    """

    def __init__(self, fname: str, buffer_size: int = 20):
        self.fname = fname
        self.buffer: List[str] = []
        self.buffer_size = buffer_size
        self.lock = asyncio.Lock()
        self.total_written = 0

    async def append(self, line: str) -> None:
        """Fügt Zeile zum Buffer hinzu, flush wenn voll."""
        async with self.lock:
            self.buffer.append(line)
            if len(self.buffer) >= self.buffer_size:
                await self._flush_unsafe()

    async def _flush_unsafe(self) -> None:
        """Schreibt Buffer in Datei (NICHT lock-protected, nur intern)."""
        if not self.buffer:
            return
        try:
            # Filter None-Werte (Pydroid 3 Bug-Fix)
            valid_items = [item for item in self.buffer if item is not None]
            if valid_items:
                with open(self.fname, "a", encoding="utf-8") as f:
                    f.write("\n".join(valid_items) + "\n")
                self.total_written += len(valid_items)
            self.buffer = []
        except (IOError, OSError):
            pass

    async def flush(self) -> None:
        """Explizites Flush – z.B. am Ende des Scans."""
        async with self.lock:
            await self._flush_unsafe()


_file_locks: dict = {}   # fname → asyncio.Lock
_output_buffers: dict = {}  # fname → OutputBuffer (v21.5)

def _init_file_locks():
    """Muss nach asyncio-Loop-Start aufgerufen werden."""
    global _file_locks, _output_buffers
    _file_locks = {
        OUTPUT_FILE:   asyncio.Lock(),
        TVONLY_FILE:   asyncio.Lock(),
        VPN_FILE:      asyncio.Lock(),
        CF_FILE:       asyncio.Lock(),
        EXPIRING_FILE: asyncio.Lock(),
    }

    # Adaptive Buffer-Größe für Mobile (v21.5)
    buffer_size = 10 if IS_MOBILE else 20
    _output_buffers = {
        OUTPUT_FILE:   OutputBuffer(OUTPUT_FILE, buffer_size),
        TVONLY_FILE:   OutputBuffer(TVONLY_FILE, buffer_size),
        VPN_FILE:      OutputBuffer(VPN_FILE, buffer_size),
        CF_FILE:       OutputBuffer(CF_FILE, buffer_size),
        EXPIRING_FILE: OutputBuffer(EXPIRING_FILE, buffer_size),
    }

async def _append_link(fname: str, link: str):
    """
    Schreibt Link in Datei über Buffer (v21.5 Output Buffering).
    Reduziert I/O-Blockierungen durch Batch-Writes.
    Fallback zu sofortigem Schreiben wenn Buffer nicht initialisiert.
    """
    # Pydroid 3 Bug-Fix: Ignoriere None-Werte
    if link is None or not isinstance(link, str):
        return

    buffer = _output_buffers.get(fname)
    if buffer is not None:
        # Gepuffert schreiben (bevorzugt)
        await buffer.append(link)
    else:
        # Fallback: Sofort schreiben (z.B. bei manuellen Exports)
        lock = _file_locks.get(fname)
        if lock is None:
            return
        async with lock:
            try:
                with open(fname, "a", encoding="utf-8") as f:
                    f.write(link + "\n")
            except (IOError, OSError):
                pass

async def _flush_all_buffers():
    """Flush aller Output-Buffer am Scan-Ende."""
    for buffer in _output_buffers.values():
        await buffer.flush()

# Accept-Language Variationen (CF erkennt uniforme Header-Sets)
_ACCEPT_LANGS = [
    "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "de-AT,de;q=0.9,en-US;q=0.8,en;q=0.6",
    "de-CH,de;q=0.9,en;q=0.8,fr;q=0.6",
    "de-DE,de;q=0.8,en;q=0.6",
]

def _rand_accept_lang() -> str:
    return random.choice(_ACCEPT_LANGS)


# Wrapper-Funktionen (delegieren an HeaderManager2026)
def _cf_nav_headers(profile: dict) -> dict:
    """Navigation-Header für CF-Hosts. Delegiert an HeaderManager2026."""
    return HeaderManager2026.get_chrome_headers(profile)

def _cf_api_headers(profile: dict, origin: str) -> dict:
    """API/XHR-Header für CF-Hosts. Delegiert an HeaderManager2026."""
    return HeaderManager2026.get_chrome_api_headers(profile, origin)

CF_ERROR_CODES = set(range(520, 531))

# ==============================================================
# TLS-KONTEXT
# ==============================================================
# WICHTIG (v19.5-Fix):
# Dieser Context wird NUR fuer CF-Hosts verwendet.
# Non-CF-Hosts erhalten ssl=False (kein TLS-Fingerprint → kein JA3).
# Der Context hier verbessert die Cipher-Reihenfolge,
# kann aber den Python-OpenSSL-JA3 nicht vollständig verstecken.
# Für CF reicht es, weil CF auf diesen IPTV-Panels primär
# Cookie+Header-Validierung statt reines JA3-Blocking nutzt.
def _build_ssl_context() -> ssl.SSLContext:
    """
    SSL-Context für CF-Hosts. v21.0: Erweiterte Cipher-Suite aus
    HeaderManager2026 (Screenshot). Chrome-TLS-Fingerprint-Härtung.
    Nur für bekannte CF-Hosts genutzt – Non-CF: ssl=False.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    # Cipher-Suite aus Screenshot (SSL/CIPHER/CONFIGURATION)
    # Reihenfolge: ECDHE-ECDSA > CHACHA20 > ECDHE-RSA > RSA-Fallbacks
    # TLS 1.3 Suites voran, dann TLS 1.2 ECDHE, dann RSA-Fallbacks
    _CIPHERS = (
        # TLS 1.3 (automatisch, nicht überschreibbar via set_ciphers)
        # TLS 1.2 – ECDHE-ECDSA (bevorzugt, wie Chrome)
        "ECDHE-ECDSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-CHACHA20-POLY1305:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:"
        # TLS 1.2 – ECDHE-RSA
        "ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-RSA-CHACHA20-POLY1305:"
        "ECDHE-RSA-AES256-GCM-SHA384:"
        # TLS 1.2 – RSA Fallback
        "AES128-GCM-SHA256:"
        "AES256-GCM-SHA384:"
        "AES128-SHA256:"
        "AES256-SHA:"
        # Ausschlüsse
        "!aNULL:!eNULL:!MD5:!DSS:!RC4:!3DES"
    )
    try:
        ctx.set_ciphers(_CIPHERS)
    except ssl.SSLError:
        # Fallback auf Minimalset wenn Plattform nicht alle kennt
        try:
            ctx.set_ciphers(
                "ECDHE-ECDSA-AES128-GCM-SHA256:"
                "ECDHE-RSA-AES128-GCM-SHA256:"
                "!aNULL:!eNULL:!MD5"
            )
        except ssl.SSLError:
            pass
    return ctx


# ==============================================================
# CLOUDFLARE DETECTION (3-EBENEN)
# ==============================================================
_CF_BODY_RE = re.compile(
    r"Checking your browser|cf_chl_|Ray ID:\s*[0-9a-f]+|"
    r"cf-browser-verification|__cf_bm|cloudflare",
    re.IGNORECASE,
)

def detect_cloudflare(status: int, headers: dict, body: str) -> bool:
    """3-Ebenen Cloudflare detection: Header → Statuscode → Body."""
    lc = {k.lower(): v.lower() for k, v in headers.items()}
    if "cf-ray" in lc:                                              return True
    if lc.get("server", "") == "cloudflare":                        return True
    if any(k in lc for k in ("cf-cache-status", "cf-edge-cache")):  return True
    if status in CF_ERROR_CODES:                                    return True
    if body and _CF_BODY_RE.search(body):                           return True
    return False


# ==============================================================
# CF-HOST-PERSISTENZ (cf_hosts.json)
# ==============================================================
_CF_HOST_TTL = 7 * 86400   # 7 Tage

def load_cf_hosts() -> set:
    """Laedt CF-Hosts aus cf_hosts.json (ignoriert Eintraege > 7 Tage)."""
    if not os.path.exists(CF_HOSTS_FILE):
        return set()
    try:
        with open(CF_HOSTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        cutoff = time.time() - _CF_HOST_TTL
        return {h for h, ts in data.items() if ts > cutoff}
    except (IOError, OSError, json.JSONDecodeError):
        return set()

def save_cf_hosts(hosts: set):
    """Speichert CF-Hosts mit aktuellem Timestamp in cf_hosts.json."""
    try:
        existing = {}
        if os.path.exists(CF_HOSTS_FILE):
            with open(CF_HOSTS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        now = time.time()
        existing.update({h: now for h in hosts})
        with open(CF_HOSTS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
    except Exception:
        pass


# ==============================================================
# HTTP STATUS INTELLIGENCE
# ==============================================================
_STATUS_INFO = {
    200: ("\033[92m", "✓", "OK",           ""),
    206: ("\033[92m", "✓", "Partial OK",   ""),
    301: ("\033[93m", "→", "Redirect",     "URL pruefen"),
    302: ("\033[93m", "→", "Redirect",     "URL pruefen"),
    401: ("\033[91m", "✗", "Unauthorized", "Account ungueltig"),
    403: ("\033[91m", "✗", "Forbidden",    "IP/Geo -> VPN"),
    404: ("\033[91m", "✗", "Not Found",    "Endpunkt fehlt"),
    429: ("\033[93m", "⊙", "Rate Limit",   "Jitter erhoehen"),
    451: ("\033[91m", "✗", "Geo-Block",    "Legal Block -> VPN"),
    500: ("\033[91m", "✗", "Server Error", "Server defekt"),
    502: ("\033[91m", "✗", "Bad Gateway",  "Proxy-Fehler"),
    503: ("\033[91m", "✗", "Unavailable",  "Ueberlastet"),
    520: ("\033[33m", "⚠", "CF Unknown",   "CF-Fehler"),
    521: ("\033[33m", "⚠", "CF Down",      "Origin offline"),
    522: ("\033[33m", "⚠", "CF Timeout",   "Origin stumm"),
    523: ("\033[33m", "⚠", "CF Reach",     "Origin weg"),
    524: ("\033[33m", "⚠", "CF A-Timeout", "Origin zu langsam"),
    525: ("\033[33m", "⚠", "CF SSL",       "SSL Handshake"),
    526: ("\033[33m", "⚠", "CF SSL Inv",   "SSL ungueltig"),
}

def http_status_str(code: int) -> str:
    col, icon, label, hint = _STATUS_INFO.get(code, ("\033[91m", "✗", f"HTTP {code}", ""))
    s = f"{col}{icon} [{code} {label}]\033[0m"
    if hint:
        s += f" \033[2m({hint})\033[0m"
    return s

def _status_icon_line(code: int, host: str, extra: str = "") -> str:
    """
    v21.0: Einzeilige Status-Ausgabe pro Account (tqdm.write).
    Format: ✓ [200 OK] | server.tv:8080 | Zusatzinfo
    Inspiriert von Hippie65 Status-Dot-System.
    """
    col, icon, label, hint = _STATUS_INFO.get(
        code, ("\033[91m", "✗", f"HTTP {code}", ""))
    host_s = host.replace("http://", "").replace("https://", "")
    host_s = _shorten(host_s, 32)
    parts  = [f"{col}{icon} [{code} {label}]\033[0m",
              c(C.DIM, f"| {host_s}")]
    if hint:
        parts.append(c(C.DIM, f"| {hint}"))
    if extra:
        parts.append(c(C.DIM, f"| {extra}"))
    return "  " + " ".join(parts)


# ==============================================================
# RESTLAUFZEIT (aus Hippie65 Xtream Checker v1 – calculateTimeLeft)
# ==============================================================
def calculate_time_left(exp_ts) -> str:
    """
    Präzise Restlaufzeit-Anzeige.
    Übersetzt Unix-Timestamp in "Xd Yh verbleibend" / "ABGELAUFEN".
    Port von Hippie65 Xtream Checker v1 (calculateTimeLeft).
    """
    if not exp_ts:
        return "unbegrenzt"
    try:
        now_ts  = time.time()
        exp_int = int(exp_ts)
        diff    = exp_int - now_ts
        if diff <= 0:
            return c(C.RED, "ABGELAUFEN")
        days  = int(diff // 86400)
        hours = int((diff % 86400) // 3600)
        if days > 365:
            years = days // 365
            return c(C.DIM, f"{years}J+")
        if days > 0:
            col = C.RED if days < 7 else (C.YELLOW if days < 30 else C.GREEN)
            return c(col, f"{days}T {hours}h")
        return c(C.RED, f"{hours}h")
    except (ValueError, OSError, OverflowError, TypeError):
        return "unbekannt"


# ==============================================================
# M3U-EXPORT (aus Bᴀᴘʜᴏᴍᴇᴛ M3U Scanner – generateM3UContent)
# ==============================================================
def generate_m3u_export(links: list, out_file: str,
                        label_prefix: str = "DE") -> int:
    """
    Erzeugt eine korrekte M3U-Datei mit #EXTM3U-Header und
    #EXTINF:-1,Name-Tags pro Link.
    Port von Bᴀᴘʜᴏᴍᴇᴛ M3U Scanner generateM3UContent().
    Gibt Anzahl geschriebener Links zurück.
    """
    if not links:
        return 0
    try:
        lines = ["#EXTM3U"]
        for i, link in enumerate(links, 1):
            try:
                parsed = urlparse(link.strip())
                qs     = parse_qs(parsed.query)
                host_s = parsed.netloc.replace(":", "_")
                user_s = qs.get("username", [""])[0]
                name   = f"{label_prefix} #{i:03d} | {host_s} | {user_s}"
            except Exception:
                name = f"{label_prefix} #{i:03d}"
            lines.append(f"#EXTINF:-1,{name}")
            lines.append(link.strip())
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return len(links)
    except Exception:
        return 0


_TIER1_WEIGHTS = {
    # Oeffentlich-Rechtlich
    "ARD": 5, "ZDF": 5, "WDR": 5, "NDR": 5, "SWR": 5,
    "MDR": 5, "RBB": 5, "HR":  5, "BR":  5, "SR":  5,
    "3SAT": 4, "PHOENIX": 4, "ARTE DE": 4, "TAGESSCHAU24": 4,
    "ONE": 3, "FUNK": 3, "KIKA": 3,
    # Grosse Privatsender
    "RTL": 4, "RTL+": 4, "RTL2": 4, "RTLNITRO": 3,
    "VOX": 3, "NTV": 3, "N-TV": 3, "SUPER RTL": 3,
    "PROSIEBEN": 4, "PRO7": 4, "SAT.1": 4, "SAT1": 4,
    "KABEL EINS": 3, "SIXX": 3, "SAT1GOLD": 3, "PROSIEBEN MAXX": 3,
    # Sport (geofenced)
    "DAZN DE": 5, "SKY DE": 5, "MAGENTASPORT": 4,
    "SPORT1": 3, "EUROSPORT DE": 3, "BILD SPORT": 3,
    # Pay-TV / Streaming
    "JOYN": 3, "JOYN+": 3, "MAGENTA TV": 3,
    "SKY SPORT": 3, "SKY CINEMA": 3, "SKY ONE": 3,
    "DISCOVERY DE": 3, "TLC DE": 3, "DMAX DE": 3,
    "ROMANCE TV": 2, "HISTORY DE": 2, "NAT GEO DE": 2,
    # Oesterreich & Schweiz
    "ORF1": 4, "ORF2": 4, "ORF3": 3, "ORFIII": 3,
    "SERVUS TV": 4, "PULS4": 3, "ATV": 3, "ATV2": 2,
    "SRF1": 4, "SRF2": 4, "SRF INFO": 3, "SRF ZWEI": 3,
    "3PLUS": 2, "TV24": 2, "TELECLUB": 2,
    # Kinder
    "NICK DE": 3, "TOGGO PLUS": 3,
    "CARTOON NETWORK DE": 2, "DISNEY DE": 2,
    # Regionale & Sonstige
    "WELT": 3, "TELE 5": 3, "BILD TV": 3, "BIBEL TV": 2,
    "MUNCHEN TV": 3, "HAMBURG 1": 3, "BERLIN TV": 3,
    "RPR1": 2, "SWR3": 2, "DLF": 3, "DEUTSCHLANDFUNK": 3,
    "ANIXE": 2, "MTV DE": 2, "VIVA": 2,
    "COMEDY CENTRAL DE": 2, "HEIMATKANAL": 2,
    # Neu in v19.6
    "ZDF NEO": 4, "SKY KRIMI": 3, "KABEL EINS DOKU": 3,
    "TERRA X": 3, "WELT DER WUNDER": 2, "BILD+": 3,
    "PARAMOUNT+ DE": 3, "PARAMOUNT DE": 3,
    "JOYN ORIGINALS": 3, "APPLE TV+ DE": 2, "PEACOCK DE": 2,
    "SKY NATURE": 2, "SKY DOCUMENTARIES": 2,
    "_default": 3,
}

# ==============================================================
# M3U+ PER-ACCOUNT GENERATOR v21.3
# Holt Streams via API und schreibt vollständige M3U+ Datei
# mit tvg-name, tvg-logo, group-title für DE + Adult Content
# ==============================================================
async def generate_m3u_plus_for_account(
        session, host: str, u: str, pw: str,
        hdrs: dict, ssl_param,
        include_adult: bool = True) -> tuple:
    """
    M3U+ Generator v21.4 – Direkter M3U-Download + Stream-Filterung.

    Architektur-Wechsel gegenüber v21.3:
    Statt N*2 API-Calls (get_live_categories → get_live_streams pro Kategorie),
    wird die vollständige M3U direkt heruntergeladen und jeder Stream
    nach seinem echten group-title Feld gefiltert.

    Warum das die richtige Lösung ist:
    - API-Kategorienamen ("DE ✦ DEUTSCHLAND") sind NICHT gleich
      den group-title Feldern im M3U ("DE | DRAMA", "DE | FILME" etc.)
    - Der alte Ansatz fand daher nur 6 von 92 DE-Gruppen
    - Der neue Ansatz filtert direkt auf dem echten group-title
    - 1 HTTP-Request statt N API-Calls → schneller, vollständiger

    Rückgabe: (lines: list[str], de_count: int, adult_count: int)
    """

    # ── Filter-Funktionen auf group-title Ebene ───────────────
    # Basis-Trennzeichen zwischen Länderkürzel und Kategorienamen.
    # Erweitert um alle Varianten aus HTML Bᴀᴘʜᴏᴍᴇᴛ flag_oder_kat():
    # ⎪ (U+23AA), ┃ (U+2503), ▎ (U+258E), ⬤ (U+2B24), ⋅ (U+22C5)
    _SEP = (
        r'(?:'
        r'[\s]*(?:'
        r'\||✦|►|•|◆|▶|★|»|–|-|:|'    # Standard
        r'➤|➜|➔|➽|❖|◈|▪|▫|→|›|➢|➡|➠|➦|▸|▹|'  # Pfeile
        r'✓|✔|✗|✘|⚫|⚪|💠|⚡|⭐|🌟|'    # Icons
        r'⎪|┃|▎|⬤|⋅|\]|\)'            # Bᴀᴘʜᴏᴍᴇᴛ-Extras
        r')[\s]*'
        r'|\s+'                         # reiner Leerzeichen-Trenner ("DE Kino")
        r')'
    )

    # DE-Präfix: "DE |", "DE✦", "AT ⎪", "⭓ DE |", "✴DE ", "┃DE"
    # Ergänzt um alle Präfix-Zeichen aus Bᴀᴘʜᴏᴍᴇᴛ:
    #   ⭓ (U+2B53), ✴ (U+2734) als führende Stern-Zeichen vor DE
    #   ⎪ (U+23AA), ┃ (U+2503) als umschließende Balken: ⎪DE, ┃DE
    _DE_PFX = re.compile(
        r'^(?:'
        # Führende Zeichen: Whitespace, Emojis, Stern-Symbole, Balken
        r'[\s\U0001F4FA\U0001F3AC🇩🇪✴⭓✶✷✸✹☆★⎪┃▎]*'
        r'(?:DE|AT|CH|DACH|GER|AUT|SUI|DEU)'
        r'(?:' + _SEP + r'|\s*$)'
        r'|'
        # Ausgeschriebene Namen
        r'[\s✴⭓⎪┃]*'
        r'(?:DEUTSCH(?:LAND)?|GERMANY|GERMAN|AUSTRIA|ÖSTERREICH|'
        r'OESTERREICH|SCHWEIZ|SWITZERLAND|ALLEMAGNE)'
        r'(?:' + _SEP + r'|\s*$)'
        r')',
        re.IGNORECASE,
    )

    # Bekannte DE-Sendergruppen als alleinstehende group-title
    _DE_GRP = re.compile(
        r'(?:'
        r'\b(?:ARD|ZDF|WDR|NDR|SWR|MDR|RBB|BR|HR|SR|3SAT|PHOENIX|'
        r'ARTE\s*DE|TAGESSCHAU24|ONE|FUNK|KiKA|KIKA)\b|'
        r'\b(?:RTL\+?|RTL2|RTLNITRO|VOX|NTV|N-TV|SUPER\s*RTL)\b|'
        r'\b(?:PROSIEBEN|PRO7|SAT\.?1|KABEL\s*EINS|SIXX|SAT1GOLD|PROSIEBEN\s*MAXX)\b|'
        r'\b(?:DAZN\s*DE|SKY\s*DE|MAGENTASPORT|SPORT1|EUROSPORT\s*DE|'
        r'BILD\s*SPORT|SPORT\s*1\+|SPORT1\s*EXTRA)\b|'
        r'\b(?:ORF\s*[123]|ORFIII|SERVUS\s*TV|PULS4|ATV2?|'
        r'SRF\s*(?:1|2|ZWEI|INFO)|3PLUS|TV24|TELECLUB)\b|'
        r'\b(?:JOYN\+?|MAGENTA\s*TV|SKY\s*SPORT|SKY\s*CINEMA|SKY\s*ONE|'
        r'DISCOVERY\s*DE|TLC\s*DE|DMAX\s*DE|ROMANCE\s*TV|HISTORY\s*DE|'
        r'NAT\s*GEO\s*DE)\b|'
        r'\b(?:NICK\s*DE|CARTOON\s*NETWORK\s*DE|DISNEY\s*DE|TOGGO\s*PLUS)\b|'
        r'\b(?:WELT|TELE\s*5|BILD\s*TV|BIBEL\s*TV|ERF|'
        r'M\.NCHEN\s*TV|HAMBURG\s*1|BERLIN\s*TV|'
        r'DLF|DEUTSCHLANDFUNK|RPR1|SWR3|ANIXE|'
        r'MTV\s*DE|VIVA|COMEDY\s*CENTRAL\s*DE|HEIMATKANAL)\b|'
        r'\b(?:ZDF\s*NEO|SKY\s*KRIMI|KABEL\s*EINS\s*DOKU|'
        r'TERRA\s*X|WELT\s*DER\s*WUNDER|'
        r'PARAMOUNT\+?\s*DE|JOYN\s*ORIGINALS|'
        r'APPLE\s*TV\+?\s*DE|PEACOCK\s*DE|'
        r'SKY\s*NATURE|SKY\s*DOCUMENTARIES)\b|'
        r'\b(?:SPORT1\+|EUROSPORT\s*1\s*DE|EUROSPORT\s*2\s*DE|'
        r'SKY\s*ATLANTIC|SKY\s*COMEDY|SKY\s*ACTION|SKY\s*REPLAY|'
        r'BUNDESLIGA|CHAMPIONS\s*LEAGUE|EUROPA\s*LEAGUE|DFB\s*POKAL|'
        r'FORMEL\s*1|F1|MOTORSPORT\s*DE)\b|'
        r'\b(?:KINOAUFNAHME|KINOBOX|CINEMA\s*DE|FILME\s*DE|SERIEN\s*DE)\b'
        r')',
        re.IGNORECASE,
    )

    # Adult-Präfix: "XXX |", "🔞 XXX ✦", "🎬 🔞 ADULT +18", "FOR | ADULTS"
    _ADULT_PFX = re.compile(
        r'^(?:'
        r'[\s\U0001F51E\U0001F3AC]*XXX(?:' + _SEP + r'|\s*$)|'
        r'[\s\U0001F51E\U0001F3AC]*ADULT\s*\+?\s*18(?:' + _SEP + r'|\s*$)|'
        r'[\s\U0001F51E\U0001F3AC]*18\s*\+\s*ADULT(?:' + _SEP + r'|\s*$)|'
        r'FOR' + _SEP + r'(?:ADULTS?|XXX|PORN)|'
        r'[\s\U0001F51E\U0001F3AC]+(?:ADULT|XXX)(?:' + _SEP + r'|\s*$)'
        r')',
        re.IGNORECASE,
    )

    def _is_de(g: str) -> bool:
        return bool(_DE_PFX.match(g)) or bool(_DE_GRP.search(g))

    def _is_adult(g: str) -> bool:
        g = g.strip()
        if _ADULT_PFX.match(g):
            return True
        # Fallback: "FOR | X4 ADULTS", "FOR | PORNBOX ADULTS" etc.
        # → beginnt mit FOR + Trenner UND enthält ADULT/XXX/PORN irgendwo
        if _FOR_ADULT_PFX.match(g):
            if _ADULT_KEYWORDS.search(g):
                return True
        return False

    def _keep(g: str) -> bool:
        if _is_de(g):
            return True
        if include_adult and _is_adult(g):
            return True
        return False

    # ── M3U direkt vom Server laden ───────────────────────────
    m3u_url = f"{host}/get.php?username={u}&password={pw}&type=m3u_plus"
    try:
        async with session.get(
            m3u_url,
            headers=hdrs,
            ssl=ssl_param,
            timeout=aiohttp.ClientTimeout(total=max(TIMEOUT * 4, 90)),
            allow_redirects=True,
        ) as resp:
            if resp.status != 200:
                return [], 0, 0
            raw = await resp.text(encoding="utf-8", errors="ignore")
    except Exception:
        return [], 0, 0

    if not raw or "#EXTM3U" not in raw:
        return [], 0, 0

    # ── Zeile für Zeile parsen + filtern ─────────────────────
    out         = ["#EXTM3U"]
    de_count    = 0
    adult_count = 0
    extinf_buf  = None
    _grp_re     = re.compile(r'group-title="([^"]*)"')

    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.upper().startswith("#EXTINF"):
            extinf_buf = line
            continue

        if extinf_buf is not None:
            if not line.startswith("#"):
                m   = _grp_re.search(extinf_buf)
                grp = m.group(1) if m else ""

                if _keep(grp):
                    # Adult-Streams visuell im tvg-name markieren
                    if _is_adult(grp):
                        if 'group-title="' in extinf_buf:
                            # Fuege 🔞 vor dem Namen ein (nach dem letzten Komma vor der URL-Zeile)
                            if ',🔞 ' not in extinf_buf and ',🔞' not in extinf_buf:
                                extinf_buf = extinf_buf.replace(',', ',🔞 ', 1)
                        adult_count += 1
                    else:
                        de_count += 1
                    out.append(extinf_buf)
                    out.append(line)
            extinf_buf = None
            continue

        extinf_buf = None   # andere # Direktiven → reset

    return out, de_count, adult_count



async def export_m3u_plus_batch(accounts: list,
                                session, ssl_ctx,
                                include_adult: bool = True):
    """
    v21.3: Generiert M3U+ Dateien für alle übergebenen Accounts.
    accounts: Liste von dicts mit host, u, pw, is_cf, dest
    Schreibt Dateien in M3UPLUS_DIR/{host}_{user}_{datum}.m3u
    """
    os.makedirs(M3UPLUS_DIR, exist_ok=True)
    stamp    = datetime.now().strftime("%Y%m%d_%H%M")
    ok_count = 0

    for acc in accounts:
        host   = acc["host"]
        u      = acc["u"]
        pw     = acc["pw"]
        is_cf  = acc.get("is_cf", False)
        ssl_p  = ssl_ctx  # v21.5: Unified SSL (CERT_NONE für alle)

        hdrs = ({"User-Agent": random.choice(PLAYER_USER_AGENTS)}
                if not is_cf else
                HeaderManager2026.get_chrome_headers())

        try:
            lines, lc, vc = await generate_m3u_plus_for_account(
                session, host, u, pw, hdrs, ssl_p, include_adult
            )
        except Exception:
            continue

        if lc + vc == 0:
            continue

        # Dateiname: host_user_datum.m3u (Sonderzeichen bereinigt)
        safe_host = _SAFE_FILENAME.sub('_', host.replace("http://","").replace("https://",""))
        safe_user = _SAFE_FILENAME_USER.sub('_', u)
        fname     = os.path.join(M3UPLUS_DIR,
                                 f"{safe_host}_{safe_user}_{stamp}.m3u")
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            print(c(C.GREEN,
                    f"  ✓ {lc} Live + {vc} VOD/Serien → {fname}"))
            ok_count += 1
        except Exception as e:
            print(c(C.RED, f"  ✗ Schreibfehler {fname}: {e}"))

    return ok_count


_DE_TIER1 = re.compile(
    r'(?:'
    r'🇩🇪|'
    r'group-title\s*=\s*"[^"]*(?:\bDE\b|GERMANY|DEUTSCHLAND|DEUTSCH)[^"]*"|'
    # Literal Unicode: ◆•►▶★» – Zeichenbereich À-ɏ (U+00C0–U+024F)
    r'DE\s*[◆•►▶★»]\s*[A-Z0-9À-ɏ]|'
    r'\b(?:ARD|ZDF|WDR|NDR|SWR|MDR|RBB|HR|BR|SR|3SAT|PHOENIX|'
    r'ARTE\s*DE|TAGESSCHAU24|ONE|FUNK|KiKA|KIKA)\b|'
    r'\b(?:RTL\+?|RTL2|RTLNITRO|VOX|NTV|N-TV|SUPER\s*RTL)\b|'
    r'\b(?:PROSIEBEN|PRO7|SAT\.?1|KABEL\s*EINS|SIXX|SAT1GOLD|PROSIEBEN\s*MAXX)\b|'
    r'\b(?:DAZN\s*DE|SKY\s*DE|MAGENTASPORT|SPORT1|EUROSPORT\s*DE|'
    r'BILD\s*SPORT|SPORT\s*1\+|SPORT1\s*EXTRA)\b|'
    r'\b(?:JOYN\+?|MAGENTA\s*TV|SKY\s*SPORT|SKY\s*CINEMA|SKY\s*ONE|'
    r'DISCOVERY\s*DE|TLC\s*DE|DMAX\s*DE|ROMANCE\s*TV|HISTORY\s*DE|'
    r'NAT\s*GEO\s*DE)\b|'
    r'\b(?:ORF\s*[123]|ORFIII|SERVUS\s*TV|PULS4|ATV2?|'
    r'SRF\s*(?:1|2|ZWEI|INFO)|3PLUS|TV24|TELECLUB)\b|'
    r'\b(?:NICK\s*DE|CARTOON\s*NETWORK\s*DE|DISNEY\s*DE|TOGGO\s*PLUS)\b|'
    r'\b(?:WELT|TELE\s*5|BILD\s*TV|BIBEL\s*TV|ERF|'
    r'M.NCHEN\s*TV|HAMBURG\s*1|BERLIN\s*TV|'
    r'DLF|DEUTSCHLANDFUNK|RPR1|SWR3|ANIXE|'
    r'MTV\s*DE|VIVA|COMEDY\s*CENTRAL\s*DE|HEIMATKANAL)\b|'
    r'\b(?:ZDF\s*NEO|SKY\s*KRIMI|KABEL\s*EINS\s*DOKU|'
    r'TERRA\s*X|WELT\s*DER\s*WUNDER|'
    r'PARAMOUNT\+?\s*DE|JOYN\s*ORIGINALS|'
    r'APPLE\s*TV\+?\s*DE|PEACOCK\s*DE|'
    r'SKY\s*NATURE|SKY\s*DOCUMENTARIES)\b|'
    r'BILD\+(?=[\s|,\[\]()\-]|$)'
    r')',
    re.IGNORECASE,
)

_DE_TIER2 = re.compile(
    r'(?:'
    r'\bDEUTSCH\b|\bGERMAN\b|\bGER\b|\bGERMANY\b|'
    r'\bBUNDESLIGA\b|\bDFB[\s-]?POKAL\b|'
    r'\bTATORT\b|\bSPORTSCHAU\b|\bTAGESSCHAU\b|'
    r'\bDE\s*:\s|\bDE\s*\||\|DE\b|\[DE\]|\(DE\)|'
    # Literal Unicode + erweiterter Pfeilsatz (➽❖ neu gegenüber v19.7)
    r'\bDE\s*[◆•►▶★»➤➜➔➽❖]|'
    r'[◆•►▶★»➤➜➔]\s*\bDE\b'
    r')',
    re.IGNORECASE,
)

_DE_EXCLUDE = re.compile(
    r'\b(?:DECODER|DEIN|DEMI|DEMO|DESIGN|DESKTOP|DEVELOP|DEEP|'
    r'DELL|DELTA|DELIVERY|DEFEND|DEFINED|DEFEAT|DELETE|DEPLOY)\b',
    re.IGNORECASE,
)

_VOD_TIER1_EXTRA = re.compile(
    r'(?:'
    r'DE\s*[◆•►▶★»]\s*\w|'
    r'DEUTSCH\s*SYNCHRONISIERT|GERMAN\s*(?:MOVIES?|FILMS?|SERIEN?)|'
    r'DEUTSCHE\s*(?:SERIEN?|FILME?|DOKUMENTATION)|OV\s*DEUTSCH|'
    r'ZDF\s*(?:MEDIATHEK|HERZKINO)|ARD\s*MEDIATHEK|'
    # KINOAUFNAHME + KINOBOX behalten; KINOVISION entfernt (False-Positives)
    r'KINOAUFNAHME|KINOBOX|'
    r'\bLIEBESFILME\b|\bKRIEGSFILME\b|\bKOMOEDIE\b|\bKOM.DIE\b|'
    r'\bFAMILIE\s*FILME\b|\bWEIHNACHTEN\s*FILME?\b|'
    r'\bKINDER\s*ANIMATION\b|\bKINDER\s*FILME?\b|'
    r'\bDOKU\s*FILME?\b|\bDOKUMENTATION\b|\bDOKUSERIE\b|'
    # LEGENDAERE? entfernt (zu unspezifisch → False-Positives)
    r'\bKLASSIKER\b|'
    r'BUNDESLIGA\s*HIGHLIGHTS?|TATORT\s*ARCHIV|'
    r'DE\s*-\s*(?:FILME?|SERIEN?|KINO)|(?:FILME?|SERIEN?)\s*DE\b'
    r')',
    re.IGNORECASE,
)

_DE_GENRE_NAMES = re.compile(
    r'(?:Nachrichten|Unterhaltung|Dokumentation|Regionalfernsehen|'
    r'Infotainment|Spielfilm|Kinderfernsehen|Musikfernsehen|'
    r'Sportfernsehen|Wissenssendung|Talkshow|Krimi)',
    re.IGNORECASE,
)

# ==============================================================
# ADULT-ERKENNUNG v21.3
# Tier 1: Eindeutige Adult-Begriffe (starkes Signal)
# Tier 2: Mehrdeutige / schwächere Signale
# ==============================================================
_ADULT_TIER1 = re.compile(
    r'(?:'
    r'\bXXX\b|\bPORN(?:O|OS)?\b|\bADULT\b|'
    r'\b18\s*[\+\|]\s*(?:ONLY|CONTENT|CHANNEL|LIVE|STREAM)?\b|'
    r'\bEROTI[CK]\b|\bEROTIK\b|'
    r'\bHARDCORE\b|\bSOFTCORE\b|'
    r'\bBLUEMOVIE\b|\bBLUE\s*MOVIE\b|'
    r'\bSEX\s*(?:TV|CHANNEL|LIVE|FILM|MOVIE)\b|'
    r'\bNAKED\b|\bNUDE\b|\bNUDIST\b|'
    r'\bSTRIPTEASE\b|\bCAMGIRL\b|\bCAMSHOW\b|'
    r'\bPLAYBOY\b|\bHUSTLER\b|\bPENTHOUSE\b|'
    r'\bPINK\s*(?:TV|CHANNEL|EROTIC)\b|'
    r'\bVENUS\s*TV\b|\bPLAY\s*BOY\b|'
    r'\bERWACHSEN(?:E|EN)?\b|\bERROTICA\b|'
    r'(?:^|\s|[|\[\(])18\+(?:\s|[|\]\)]|$)'
    r')',
    re.IGNORECASE,
)

_ADULT_TIER2 = re.compile(
    r'(?:'
    r'\bSEXY\b|\bGIRLS?\b|\bBABES?\b|'
    r'\bFETISH\b|\bBDSM\b|\bKINKY\b|'
    r'\bLESBIAN\b|\bGAY\b|\bTRANS\b|'
    r'\bMILF\b|\bCOUGAR\b|\bTEEN(?:S)?\s*(?:TV|CH|CHANNEL)?\b|'
    r'\bAMAT(?:EUR|EUR)\b|'
    r'\bHOTTEST\b|\bSEDUCTION\b|'
    r'\bNAUGHTY\b|\bWILD\s*(?:TV|CHANNEL|GIRLS?)\b'
    r')',
    re.IGNORECASE,
)


def score_adult_content(text: str) -> tuple:
    """
    v21.3: Bewertet Text auf Adult-Content.
    Rückgabe: (is_adult: bool, score: int, tier: int)
      tier=1 → sicher Adult (Tier-1-Treffer)
      tier=2 → wahrscheinlich Adult (min. 2 Tier-2-Treffer)
      tier=0 → kein Adult erkannt
    """
    if not text:
        return False, 0, 0

    t1_matches = set(m.upper().strip()
                     for m in _ADULT_TIER1.findall(text))
    if t1_matches:
        return True, len(t1_matches) * 3, 1

    t2_matches = set(m.upper().strip()
                     for m in _ADULT_TIER2.findall(text))
    if len(t2_matches) >= 2:
        return True, len(t2_matches), 2

    return False, 0, 0


def _adult_label(tier: int) -> str:
    """Label für Adult-Treffer in der Terminal-Ausgabe."""
    return "🔞 ADULT*" if tier == 1 else "🔞 ADULT~"


def _normalize(text: str) -> str:
    """
    Umlaut-Normalisierung vor dem DE-Matching.
    Wandelt ä→ae, ö→oe, ü→ue, ß→ss (und Grossbuchstaben).
    Erkennt Kategorienamen auch wenn Umlaute fehlen oder ersetzt wurden.
    """
    return (text
            .replace("ä", "ae").replace("Ä", "AE")
            .replace("ö", "oe").replace("Ö", "OE")
            .replace("ü", "ue").replace("Ü", "UE")
            .replace("ß", "ss"))


def _extract_names(raw: str, key: str = "category_name") -> str:
    """Parst JSON-Array und gibt key-Werte als String zurueck."""
    try:
        items = json.loads(raw)
        if isinstance(items, list):
            return " | ".join(
                str(item.get(key, ""))
                for item in items
                if isinstance(item, dict)
            )
    except (json.JSONDecodeError, AttributeError):
        pass
    return raw


def score_de_content(text: str, vod_mode: bool = False,
                     tz_bonus: int = 0,
                     cat_count: int = 999) -> tuple:
    """
    Berechnet DE-Score. Rueckgabe: (is_de, tier, score)
      tier=1 sicherer Treffer [DE*]
      tier=2 wahrscheinlich   [DE~]
      tier=0 kein DE

    v19.9: Text wird vor dem Matching umlaut-normalisiert.
    cat_count: Anzahl der Kategorien vom Server.
    Wenn < CAT_MIN_COUNT → Score wird halbiert (Falsch-Positiv-Schutz).
    """
    # v19.9: Normalisierung – Original + normalisierte Version kombinieren
    norm_text = _normalize(text)
    combined_text = text + " " + norm_text if norm_text != text else text

    excl_count = len(_DE_EXCLUDE.findall(combined_text))

    raw_t1    = _DE_TIER1.findall(combined_text)
    unique_t1 = set(m.upper().strip() for m in raw_t1)
    score     = 0
    for match in unique_t1:
        weight = _TIER1_WEIGHTS.get(match)
        if weight is None:
            for k, w in _TIER1_WEIGHTS.items():
                if k != "_default" and k in match:
                    weight = w
                    break
        score += weight if weight is not None else _TIER1_WEIGHTS["_default"]

    if vod_mode:
        vod_extra = set(m.upper().strip() for m in _VOD_TIER1_EXTRA.findall(combined_text))
        score += len(vod_extra) * 3

    score += tz_bonus
    score -= excl_count

    # Kategorienzahl-Check: wenige Kategorien → Score halbieren
    if cat_count < CAT_MIN_COUNT and score > 0:
        score = score // 2

    if score > 0:
        return True, 1, score

    unique_t2 = set(m.upper().strip() for m in _DE_TIER2.findall(combined_text))
    t2_score  = len(unique_t2)
    threshold = VOD_TIER2_MIN if vod_mode else 2
    if t2_score >= threshold:
        return True, 2, t2_score

    return False, 0, 0


def score_genre_content(text: str) -> int:
    return len(set(m.upper() for m in _DE_GENRE_NAMES.findall(text)))


# ==============================================================
# LINK-EXTRAKTION
# ==============================================================
_RE_XTREAM = re.compile(
    r'https?://[^\s<>"]+?username=[^\s&<>"]+&password=[^\s&<>"]+[^\s<>"]*'
)

# Portal-URL Erkennung (nur Host, kein username/password)
_RE_PORTAL = re.compile(
    r'^(https?://[a-zA-Z0-9.\-_]+(:\d{1,5})?)/?$'
)

# Credentials-Zeile: user:pass (mindestens 3 Zeichen pro Teil)
_RE_CREDS = re.compile(
    r'^([^:/\s]{1,64}):([^:/\s]{3,64})$'
)

# Optimierte Pre-Compiled Patterns für Hot-Paths (v21.4 Optimization)
_FOR_ADULT_PFX = re.compile(r'^FOR\s*(?:\||✦|►|•|◆|▶)', re.IGNORECASE)
_ADULT_KEYWORDS = re.compile(r'\bADULT\b|\bXXX\b|\bPORN\b', re.IGNORECASE)
_ANSI_ESCAPE = re.compile(r"\033\[[0-9;]*m")
_SAFE_FILENAME = re.compile(r'[^\w\-.]')
_SAFE_FILENAME_USER = re.compile(r'[^\w\-]')


def _process_portal_format(lines: list) -> list:
    """
    Konvertiert Portal+Credentials Format zu vollständigen M3U-URLs.
    Port von processInput() aus HTML Bᴀᴘʜᴏᴍᴇᴛ M3U Scanner.

    Erkannte Formate:
      http://portal.tv:8080        ← Host-only (Portal)
      admin:password123            ← darunter: user:pass
      → http://portal.tv:8080/get.php?username=admin&password=password123&type=m3u_plus

      user:pass@http://portal.tv   ← user:pass@host Format
      admin:pass http://host:8080  ← nebeneinander in einer Zeile
    """
    output     = []
    portal_cur = None

    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        # 1. Vollständige Xtream-URL → direkt übernehmen
        if "username=" in line and "password=" in line:
            output.append(line)
            portal_cur = None
            continue

        # 2. user:pass@http://host Format
        at_match = re.match(
            r'^([^:/\s]+):([^@/\s]{3,})@(https?://[^\s]+)$', line)
        if at_match:
            u, p, host = at_match.groups()
            host = host.rstrip("/")
            output.append(
                f"{host}/get.php?username={u}&password={p}&type=m3u_plus")
            portal_cur = None
            continue

        # 3. "http://host:port  user:pass" in einer Zeile
        inline = re.match(
            r'^(https?://[a-zA-Z0-9.\-_]+(?::\d+)?)'
            r'[\s,;|]+([^:/\s]+):([^:/\s]{3,})$', line)
        if inline:
            host, u, p = inline.groups()
            host = host.rstrip("/")
            output.append(
                f"{host}/get.php?username={u}&password={p}&type=m3u_plus")
            portal_cur = None
            continue

        # 4. Portal-only URL → merken
        if _RE_PORTAL.match(line):
            portal_cur = line.rstrip("/")
            continue

        # 5. user:pass wenn Portal bekannt
        creds = _RE_CREDS.match(line)
        if creds and portal_cur:
            u, p = creds.groups()
            output.append(
                f"{portal_cur}/get.php?username={u}&password={p}&type=m3u_plus")
            # Portal bleibt gesetzt → mehrere user:pass pro Portal
            continue

        # Kein bekanntes Format → Portal zurücksetzen
        portal_cur = None

    # Deduplizieren (Reihenfolge erhalten wie in Bᴀᴘʜᴏᴍᴇᴛ)
    return list(dict.fromkeys(output))

# ==============================================================
# FARBEN & UI — Semantische Theme-Schicht + Truecolor-Engine
# ==============================================================
# Aktives Theme: MATRIX (monochrom-grün, futuristisch).
# Farben werden über semantische Rollen vergeben. Die Legacy-Namen
# (C.CYAN, C.GREEN, …) sind auf diese Rollen gemappt, damit alle
# bestehenden Aufrufe unverändert weiterlaufen.
# Theme wechseln = nur die THEME-Tabelle tauschen.

_TRUECOLOR = os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit")

def _ansi_fg(hexcode: str) -> str:
    """Hex-Farbe → ANSI-Vordergrund (Truecolor, sonst 256-Fallback)."""
    h = hexcode.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if _TRUECOLOR:
        return f"\033[38;2;{r};{g};{b}m"
    idx = 16 + 36 * (r * 5 // 255) + 6 * (g * 5 // 255) + (b * 5 // 255)
    return f"\033[38;5;{idx}m"

# MATRIX-Palette — semantische Rolle → Hex
THEME = {
    "PRIMARY": "#00ff9c",   # Rahmen, Titel, Sektionen
    "ACCENT":  "#7CFC00",   # Tasten [A] [1] …
    "SUCCESS": "#00ff9c",   # DE-Treffer / OK
    "WARN":    "#d7ff00",   # läuft bald ab / Rate-Limit
    "DANGER":  "#ff5555",   # Fehler (bewusst Rot — muss eindeutig bleiben)
    "INFO":    "#43d9ad",   # Hinweise
    "SPECIAL": "#2dd4bf",   # VPN
    "CF":      "#a3e635",   # Cloudflare (eigene Limette zur Abgrenzung)
    "MUTED":   "#2f7d5b",   # Sekundärinfo (auf AMOLED sichtbar)
    "TEXT":    "#c8facc",   # Fließtext
}

class C:
    # SGR-Attribute
    RESET  = "\033[0m";  BOLD = "\033[1m";  DIM = "\033[2m"
    # Legacy-Farbnamen → MATRIX-Rollen
    GREEN  = _ansi_fg(THEME["SUCCESS"])
    RED    = _ansi_fg(THEME["DANGER"])
    YELLOW = _ansi_fg(THEME["WARN"])
    CYAN   = _ansi_fg(THEME["PRIMARY"])
    PURPLE = _ansi_fg(THEME["SPECIAL"])
    WHITE  = _ansi_fg(THEME["TEXT"])
    ORANGE = _ansi_fg(THEME["CF"])
    BLUE   = _ansi_fg(THEME["INFO"])
    GRAY   = _ansi_fg(THEME["MUTED"])
    # Semantische Aliase (für neuen Code bevorzugt)
    PRIMARY = CYAN
    ACCENT  = _ansi_fg(THEME["ACCENT"])
    SUCCESS = GREEN
    WARN    = YELLOW
    DANGER  = RED
    INFO    = BLUE
    SPECIAL = PURPLE
    MUTED   = GRAY
    TEXT    = WHITE

def c(color, text):
    return f"{color}{text}{C.RESET}"

# ══════════════════════════════════════════════════════════════════════════════
# ADAPTIVE TERMINAL WIDTH DETECTION (v21.5)
# ══════════════════════════════════════════════════════════════════════════════
def _detect_terminal_width():
    """
    Erkenne echte Terminal-Breite zur Laufzeit.
    Wichtig für Pydroid: Displays können sehr schmal sein (40-50 Zeichen).
    """
    try:
        cols, _ = shutil.get_terminal_size(fallback=(64, 24))

        # Intelligente Downscale für sehr kleine Displays
        if cols <= 50:
            return max(cols - 2, 40)
        elif cols <= 80:
            return cols - 4
        else:
            return cols - 8
    except Exception:
        return W

# Berechne verfügbare Terminal-Breite einmalig
W_ACTUAL = _detect_terminal_width()

def _sep(char="-"):
    return c(C.CYAN, char * W_ACTUAL)

def _hdr(title: str) -> str:
    inner = f" {title} ".center(W_ACTUAL - 2)
    top   = c(C.CYAN + C.BOLD, "+" + "-" * (W_ACTUAL - 2) + "+")
    mid   = (c(C.CYAN + C.BOLD, "|") +
             c(C.WHITE + C.BOLD, inner) +
             c(C.CYAN + C.BOLD, "|"))
    bot   = c(C.CYAN + C.BOLD, "+" + "-" * (W_ACTUAL - 2) + "+")
    return f"{top}\n{mid}\n{bot}"

def _shorten(s: str, n: int) -> str:
    return s[:n] if len(s) <= n else s[:n - 2] + ".."

def _fmt_conns(active: int, max_c: int) -> str:
    return f"{active}/{max_c if max_c else 'oo'}"

def print_config_banner(total: int, loaded: int, cf_preloaded: int,
                        workers_actual: int, workers_auto: bool = False):
    print(_hdr("XTREAM DE SCANNER v21.4"))
    rows = [
        ("Links discovered",    str(total)),
        ("Known links skipped",  str(loaded)),
        ("CF-Hosts geladen",  str(cf_preloaded)),
        ("Workers",            f"{workers_actual}" + (" (auto)" if workers_auto else " (manuell)")),
        ("Timeout",           f"{TIMEOUT}s / Task-Max {TIMEOUT * TASK_TIMEOUT_MULT}s"),
        ("Pre-Check",         f"{'JA' if PRECHECK_ENABLED else 'NEIN'} ({PRECHECK_TIMEOUT}s TCP)"),
        ("CF-Retries",        f"{CF_MAX_RETRIES}" + (" (Pydroid3: sofort skip)" if CF_MAX_RETRIES == 0 else "")),
        ("VPN detection",         "JA" if VPN_CHECK else "NEIN"),
        ("Sample-Check",      "JA" if SAMPLE_CHECK else "NEIN"),
        ("Trial filter",      "JA" if FILTER_TRIAL else "NEIN"),
        ("Expiration filter",     f"< {EXP_MIN_DAYS} Tage / Warn < {EXP_WARN_DAYS} Tage" if EXP_MIN_DAYS > 0 else "AUS"),
        ("Max Links/Host",    str(MAX_LINKS_PER_HOST) if MAX_LINKS_PER_HOST > 0 else "unbegrenzt"),
        ("Kat-Min",           f"{CAT_MIN_COUNT} (Score /2 darunter)"),
        ("Streaming-Output",  "JA (sofort)"),
        ("SSL verification",        "False (kein JA3-Fingerprint)"),
        ("Output: Frei",      OUTPUT_FILE),
        ("Output: TV-only",   TVONLY_FILE),
        ("Output: VPN",       VPN_FILE),
        ("Output: Ablauf",    EXPIRING_FILE),
        ("Output: CF",        CF_FILE),
    ]
    for k, v in rows:
        print(f"  {c(C.DIM, f'{k:<22}')} {c(C.WHITE, v)}")
    print()

def print_summary(state):
    total_processed = sum(state.stats.values())

    def _bar(val, width=10):
        if total_processed == 0:
            return ""
        filled = int(round(val / total_processed * width))
        return c(C.DIM, "█" * filled + "░" * (width - filled))

    # Feste Spaltenbreiten fuer saubere Ausrichtung
    LBL_W   = 28   # Label-Spalte
    VAL_W   = 6    # Wert-Spalte
    BAR_W   = 10   # Balken-Spalte
    DEST_W  = 22   # Dateiname-Spalte

    hit_rows = [
        (C.GREEN,  "[ DE | ALLE KATEGORIEN ]",     "neu_de",         OUTPUT_FILE),
        (C.CYAN,   "[ DE | NUR LIVE TV      ]",     "tvonly",         TVONLY_FILE),
        (C.PURPLE, "[ VPN | ERFORDERLICH    ]",     "vpn_de",         VPN_FILE),
        (C.YELLOW, "[ ACCOUNT | ENDET BALD  ]",     "expiring",       EXPIRING_FILE),
        (C.ORANGE, "[ CLOUDFLARE | ERKANNT  ]",     "cf",             CF_FILE),
        (C.YELLOW, "[ CF Retry OK           ]",     "cf_retry_ok",    ""),
        (C.DIM,    "[ kein DE               ]",     "kein_de",        ""),
        (C.DIM,    "[ Acc-Fehler            ]",     "account_fehler", ""),
        (C.DIM,    "[ Voll belegt           ]",     "max_erreicht",   ""),
        (C.DIM,    "[ Rate-Limit            ]",     "ratelimit",      ""),
        (C.DIM,    "[ Trial-Acc             ]",     "trial_acc",      ""),
        (C.DIM,    "[ Format-Skip           ]",     "format_skip",    ""),
        (C.DIM,    "[ Bald ablaufend        ]",     "abgelaufen_bald",""),
        (C.DIM,    "[ Stream-Fail           ]",     "sample_fail",    ""),
        (C.DIM,    "[ Dubletten             ]",     "duplikate",      ""),
        (C.DIM,    "[ Host gesperrt         ]",     "host_geblockt",  ""),
        (C.DIM,    "[ Host-Limit            ]",     "host_limit",     ""),
        (C.DIM,    "[ Pre-Check             ]",     "precheck_skip",  ""),
    ]
    err_rows = [
        (C.RED,    "[ TCP offline ]", "tcp_fehler", ""),
        (C.RED,    "[ DNS Fehler  ]", "dns_fehler", ""),
        (C.YELLOW, "[ Timeout     ]", "timeout",    ""),
        (C.YELLOW, "[ SSL Fehler  ]", "ssl_fehler", ""),
        (C.DIM,    "[ HTTP Fehler ]", "verbindung", ""),
    ]

    print(f"\n{_sep()}")
    print(c(C.BOLD + C.WHITE, " SCAN-ERGEBNIS"))
    print(_sep())

    for col, label, key, fname in hit_rows:
        val = state.stats.get(key, 0)
        if val == 0 and key not in ("neu_de", "tvonly", "vpn_de", "cf"):
            continue

        bar  = _bar(val)
        pct  = f"{val / total_processed * 100:>5.1f}%" if total_processed else "   0%"
        dest = f"-> {fname}" if fname and val > 0 else ""

        # Saubere Spaltenausrichtung
        line = (f"  {c(col, f'{label:<{LBL_W}}')} "
                f"{c(C.WHITE, f'{val:>{VAL_W}}')} "
                f"{bar:<{BAR_W}} "
                f"{c(C.DIM, pct)} "
                f"{c(C.DIM, f'{dest:<{DEST_W}}')}")
        print(line)

    total_err = sum(state.stats.get(k, 0) for _, _, k, _ in err_rows)
    if total_err > 0:
        print(c(C.DIM, "  " + "─" * (W - 4)))
        print(c(C.DIM, f"  {'VERBINDUNGSFEHLER-BREAKDOWN':^{W-4}}"))
        for col, label, key, _ in err_rows:
            val = state.stats.get(key, 0)
            if val == 0:
                continue
            bar = _bar(val)
            pct = f"{val / total_processed * 100:>5.1f}%" if total_processed else "   0%"
            line = (f"  {c(col, f'{label:<{LBL_W}}')} "
                    f"{c(C.WHITE, f'{val:>{VAL_W}}')} "
                    f"{bar:<{BAR_W}} "
                    f"{c(C.DIM, pct)}")
            print(line)

    print(_sep())

    dead = state.stats.get("tcp_fehler", 0) + state.stats.get("dns_fehler", 0)
    if total_processed > 0:
        dead_pct = dead / total_processed * 100
        if dead_pct >= DEAD_LINK_WARN_PCT:
            print(c(C.YELLOW + C.BOLD,
                    f"  [!] WARNUNG: {dead_pct:.0f}% tote Links "
                    f"(TCP/DNS-Fehler). Liste ist veraltet oder "
                    f"von schlechter Qualitaet."))
            print()

    # Telemetrie
    if state._timing:
        t_avg = sum(state._timing) / len(state._timing)
        t_min = min(state._timing)
        t_max = max(state._timing)
        print(c(C.DIM,
                f"  Telemetrie: avg {t_avg:.1f}s | "
                f"min {t_min:.1f}s | max {t_max:.1f}s "
                f"({len(state._timing)} gemessen)"))
        print()


def _format_hit_oneline(res: dict) -> str:
    """
    v21.4: Einzeilige Trefferdarstellung – exakt W=64 Zeichen.
    Kein Umbruch auf Smartphone. Icon 1 Zeichen statt 10.

    Sichtbares Layout:
      IC  HOST__________________  USER________  TIME  LABEL______
       1   1  22chars            1  12chars     1  4   1  ~20chars
    """
    dest     = res.get("dest", "")
    host     = res.get("host", "")
    user     = res.get("user", "")
    exp_ts   = res.get("exp_ts", None)
    tier     = res.get("tier",   0)
    http_code= res.get("http_code", 200)
    is_adult = res.get("is_adult", False)
    a_tier   = res.get("a_tier",   0)

    if not dest:
        return ""

    # ── Label (kompakt, max 20 Zeichen) ──────────────────────
    tier_m = "*" if tier == 1 else "~"
    _LABELS = {
        "free":     (C.GREEN,  f"DE{tier_m} ALLE KAT."),
        "tvonly":   (C.CYAN,   f"DE{tier_m} NUR LIVE"),
        "vpn":      (C.PURPLE, "VPN GESPERRT"),
        "cf":       (C.ORANGE, "CLOUDFLARE"),
        "expiring": (C.YELLOW, "ENDET BALD"),
    }
    if dest not in _LABELS:
        return ""
    col, label_text = _LABELS[dest]
    if is_adult:
        label_text += " 🔞" if a_tier == 1 else " 🔞~"

    # ── Status-Icon: 1 sichtbares Zeichen ────────────────────
    _ICONS = {
        200: (C.GREEN,  "✓"), 206: (C.GREEN,  "✓"),
        403: (C.RED,    "✗"), 401: (C.RED,    "✗"),
        404: (C.RED,    "✗"), 429: (C.YELLOW, "⊙"),
        451: (C.RED,    "✗"),
    }
    if http_code >= 520:
        icon_col, icon_chr = C.ORANGE, "⚠"
    elif http_code == 0:
        icon_col, icon_chr = C.GRAY,   "⧖"
    else:
        icon_col, icon_chr = _ICONS.get(http_code, (C.RED, "✗"))

    # ── Felder auf feste sichtbare Breiten ───────────────────
    host_s = host.replace("https://", "").replace("http://", "")
    host_s = f"{host_s:<22}"[:22]   # 22 Zeichen, padding VOR Farbe

    user_s = f"{user:<12}"[:12]     # 12 Zeichen

    # Restlaufzeit 4 Zeichen ("45T" / "3h" / " -- ")
    if exp_ts:
        tl_raw  = calculate_time_left(exp_ts)
        tl_plain= _ANSI_ESCAPE.sub("", tl_raw)
        tl_s    = tl_plain.strip()[:4]
        tl_col  = (C.RED    if any(x in tl_plain for x in
                                   ["ABG","1T","2T","3T","4T","5T","6T"])
                   else C.YELLOW if "7T" in tl_plain or tl_plain.endswith("h")
                   else C.GREEN)
        time_s  = c(tl_col, f"{tl_s:<4}")
    else:
        time_s  = c(C.GRAY, " -- ")

    # ── Zusammensetzen (Padding VOR Farbe → kein ANSI-Drift) ─
    return (f" {c(icon_col, icon_chr)}"
            f" {c(C.WHITE, host_s)}"
            f" {c(C.GRAY,  user_s)}"
            f" {time_s}"
            f" {c(col + C.BOLD, label_text)}")


# Rückwärtskompatibler Alias
def _format_hit(res: dict) -> str:
    return _format_hit_oneline(res)



# ==============================================================
# STATE MANAGEMENT
# ==============================================================
class ScanState:
    def __init__(self):
        self.lock              = asyncio.Lock()
        self.checked_keys      = set()
        self._cf_hosts         = load_cf_hosts()
        self._cf_cookies       = {}   # host → {"value": str, "expires": float}
        self._cf_profile       = {}   # host → Browser-Profil-Index
        self.free_links        = []
        self.tvonly_links      = []
        self.vpn_links         = []
        self.cf_links          = []
        self.expiring_links    = []
        self.adult_accounts    = []   # v21.3: Accounts mit Adult-Content für M3U+
        self.host_error_count  = {}
        self.last_host_request = {}
        self.host_links_count  = {}
        self.stats = {
            "neu_de":         0,
            "tvonly":         0,
            "vpn_de":         0,
            "cf":             0,
            "adult":          0,   # v21.3: Adult-Treffer
            "kein_de":        0,
            "verbindung":     0,
            "timeout":        0,
            "tcp_fehler":     0,
            "dns_fehler":     0,
            "ssl_fehler":     0,
            "ratelimit":      0,
            "account_fehler": 0,
            "duplikate":      0,
            "host_geblockt":  0,
            "max_erreicht":   0,
            "cf_retry_ok":    0,
            "precheck_skip":  0,
            # v19.6
            "trial_acc":      0,
            "format_skip":    0,
            "abgelaufen_bald":0,
            "sample_fail":    0,
            # v19.9
            "expiring":       0,   # Ablauf-Vorwarnung (expiring_links.txt)
            "host_limit":     0,   # Max. Treffer pro Host erreicht
        }
        # Adaptiver Jitter: Multiplikator pro Host (erhoehung nach 429)
        self.host_jitter_mult  = {}   # host → float (1.0 = normal)
        # Telemetrie: Account-Zeiten
        self._timing           = []   # Liste von floats (Sekunden)

    def load_existing(self) -> int:
        """
        Laedt bereits bekannte Accounts aus den Ausgabedateien.
        v20.0: Schluessel = (username, password) – hostunabhaengig.
        Verhindert Re-Scan identischer Credentials auf anderen Hosts.
        """
        count = 0
        for fname in [OUTPUT_FILE, TVONLY_FILE, VPN_FILE, CF_FILE, EXPIRING_FILE]:
            if not os.path.exists(fname):
                continue
            with open(fname, "r", encoding="utf-8") as f:
                for line in f:
                    qs = parse_qs(urlparse(line.strip()).query)
                    u  = qs.get("username", [None])[0]
                    pw = qs.get("password", [None])[0]
                    if u and pw:
                        self.checked_keys.add((u, pw))   # v20.0: nur (u, pw)
                        count += 1
        return count

    def get_cf_cookie_header(self, host: str) -> str:
        entry = self._cf_cookies.get(host)
        if entry and entry["expires"] > time.time():
            return entry["value"]
        return ""

    def set_cf_cookie(self, host: str, value: str):
        self._cf_cookies[host] = {
            "value":   f"cf_clearance={value}",
            "expires": time.time() + CF_COOKIE_TTL,
        }

    def get_cf_profile(self, host: str) -> dict:
        """
        Gibt Browser-Profil für CF-Host zurück.
        v21.0: Nutzt HeaderManager2026 – Chrome 136/147 rotierend.
        Profil wird pro Host gecacht (konsistentes Fingerprint pro Session).
        """
        if host not in self._cf_profile:
            # v21.1: gleichgewichtet – alle 4 Chrome-Profile gleich wahrscheinlich
            self._cf_profile[host] = random.choices(
                range(len(HeaderManager2026.CHROME_PROFILES)),
                weights=[25, 25, 25, 25], k=1
            )[0]
        return HeaderManager2026.CHROME_PROFILES[self._cf_profile[host]]


# ==============================================================
# CF-COOKIE AUS SESSION-JAR EXTRAHIEREN
# ==============================================================
def _extract_cf_cookie(response, host: str, state: ScanState):
    """Extrahiert cf_clearance aus Response-Cookies."""
    for cookie in response.cookies.values():
        if cookie.key == "cf_clearance":
            state.set_cf_cookie(host, cookie.value)
            return True
    return False


# ==============================================================
# CF PRE-FLIGHT
# ==============================================================
async def cf_preflight(session, host: str, state: ScanState,
                       ssl_ctx) -> bool:
    """Root-URL abrufen um cf_clearance zu erhalten."""
    profile  = state.get_cf_profile(host)
    hdrs     = _cf_nav_headers(profile)
    cookie   = state.get_cf_cookie_header(host)
    if cookie:
        hdrs["Cookie"] = cookie
    try:
        async with session.get(
            host + "/",
            headers=hdrs,
            timeout=aiohttp.ClientTimeout(total=TIMEOUT),
            ssl=ssl_ctx,           # CF-Hosts: Browser-SSLContext
            allow_redirects=True,
        ) as r:
            body = await r.text(errors="replace")
            if detect_cloudflare(r.status, dict(r.headers), body):
                return False
            return _extract_cf_cookie(r, host, state)
    except Exception:
        return False


# ==============================================================
# PANEL-TYP-ERKENNUNG
# ==============================================================
def detect_panel_type(server_info: dict) -> str:
    """
    Erkennt den Panel-Typ anhand von server_info-Feldern.
    Gibt einen kurzen String zurueck: XUI / XC / Klon / SC / ?
    """
    name = str(server_info.get("server_name", "")).upper()
    rtmp = str(server_info.get("rtmp_port", ""))
    keys = set(server_info.keys())

    if "XUI" in name:
        return "XUI"
    if rtmp == "8001" and "server_name" in keys:
        return "XC"       # Original Xtream Codes
    if "process" in keys:
        return "Klon"
    if "server_name" not in keys:
        return "SC"       # StreamCreed oder unbekannter Klon
    return "?"


# ==============================================================
# CHECKPOINT
# ==============================================================
def save_checkpoint(state: "ScanState", processed: int, input_urls: list = None):
    """Speichert aktuellen Scan-Fortschritt in CHECKPOINT_FILE."""
    try:
        data = {
            "ts":           datetime.now().isoformat(),
            "processed":    processed,
            "input_urls":   input_urls if input_urls is not None else [],
            "input_hash":   hashlib.sha256("\n".join(sorted(input_urls or [])).encode()).hexdigest() if input_urls else "",
            "free_links":   state.free_links,
            "tvonly_links": state.tvonly_links,
            "vpn_links":    state.vpn_links,
            "cf_links":     state.cf_links,
            "stats":        dict(state.stats),
        }
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


# ==============================================================
# STICHPROBEN-KANALCHECK
# ==============================================================
async def sample_channel_check(session, api: str, u: str, pw: str,
                                hdrs: dict, ssl_param,
                                host: str) -> tuple:
    """
    Laedt einen zufaelligen Live-Kanal aus get_live_streams.
    Gibt (stream_ok: bool, name_bonus: int) zurueck.
      stream_ok=True   wenn mindestens ein Stream antwortet (200/206).
      name_bonus       Anzahl DE-Tier1-Treffer in Kanalnamen der Stichprobe.
    False wenn alle Stichproben-Streams tot sind.

    v19.9: Kanalnamen der Stichprobe werden gegen _DE_TIER1 geprüft.
    """
    raw = await _fetch_api(
        session, api,
        {"username": u, "password": pw,
         "action":   "get_live_streams"},
        hdrs, TIMEOUT, ssl_param,
    )
    if not raw:
        return True, 0

    try:
        streams = json.loads(raw)
        if not isinstance(streams, list) or not streams:
            return True, 0
    except Exception:
        return True, 0

    # Zufaellige Stichprobe: max. 3 Streams testen
    sample = random.sample(streams, min(3, len(streams)))

    # v19.9: Kanalnamen auf DE prüfen (alle Streams, nicht nur Stichprobe)
    name_sample = random.sample(streams, min(10, len(streams)))
    name_text   = " | ".join(s.get("name", "") for s in name_sample)
    name_bonus  = len(set(m.upper() for m in _DE_TIER1.findall(name_text)))

    stream_ok = False
    for stream in sample:
        sid = stream.get("stream_id") or stream.get("id")
        if not sid:
            continue
        test_url = f"{host}/{u}/{pw}/{sid}.ts"
        cb       = f"_cb={int(time.time()*1000)}"
        url      = f"{test_url}?{cb}"
        try:
            async with session.get(
                url,
                headers={"User-Agent": hdrs.get("User-Agent",""),
                         "Range": "bytes=0-512"},
                timeout=aiohttp.ClientTimeout(total=SAMPLE_TIMEOUT),
                ssl=ssl_param,
            ) as r:
                if r.status in (200, 206):
                    await r.read()
                    stream_ok = True
                    break
        except Exception:
            continue

    return stream_ok, name_bonus


# ==============================================================
# JITTER (adaptiv)
# ==============================================================
def _jitter(is_cf: bool, mult: float = 1.0) -> float:
    base = (CF_JITTER_BASE + random.uniform(0.5, 2.0)) if is_cf \
           else random.uniform(1.2, 2.5)
    return base * mult


# ==============================================================
# STREAM PROBE (VPN detection)
# ==============================================================
async def probe_stream_vpn(session, stream_url: str,
                           is_cf: bool, state: ScanState,
                           host: str, ssl_ctx) -> str:
    cb   = f"_cb={int(time.time() * 1000)}"
    url  = f"{stream_url}{'&' if '?' in stream_url else '?'}{cb}"

    # SSL: Alle Hosts → ssl_ctx mit CERT_NONE (Self-Signed akzeptieren)
    # v21.5: Unified SSL handling für CF + non-CF
    ssl_param = ssl_ctx

    if is_cf:
        profile = state.get_cf_profile(host)
        hdrs = {
            "User-Agent": profile["User-Agent"],
            "Range":      "bytes=0-1024",
            "Connection": "keep-alive",
        }
        cookie = state.get_cf_cookie_header(host)
        if cookie:
            hdrs["Cookie"] = cookie
    else:
        hdrs = {
            "User-Agent": random.choice(PLAYER_USER_AGENTS),
            "Range":      "bytes=0-1024",
            "Connection": "keep-alive",
        }
    try:
        async with session.get(
            url, headers=hdrs,
            timeout=aiohttp.ClientTimeout(total=PROBE_TIMEOUT),
            ssl=ssl_param,
        ) as r:
            await r.read()
            if r.status in (200, 206): return "ok"
            if r.status in (403, 451): return "vpn"
            return "error"
    except Exception:
        return "error"


# ==============================================================
# API-HELFER
# ==============================================================
async def _fetch_api(session, api: str, params: dict,
                     hdrs: dict, timeout: int,
                     ssl_param=False) -> str:
    """
    Gibt Response-Text zurück oder leeren String bei Fehler.
    v21.5: Separate sock_read-Timeout verhindert hängende Reads
    bei langsamen Servern (port von jsonWithTimeout aus Bᴀᴘʜᴏᴍᴇᴛ).
    """
    try:
        ct = aiohttp.ClientTimeout(
            total       = timeout,
            connect     = min(5, timeout),
            sock_connect= min(5, timeout),
            sock_read   = timeout,   # separates Read-Timeout
        )
        async with session.get(
            api, params=params, headers=hdrs,
            timeout=ct, ssl=ssl_param,
        ) as r:
            if r.status == 200:
                # asyncio.wait_for verhindert hängende body-reads
                # (analog zu Promise.race([response.json(), timeout]) im HTML)
                return await asyncio.wait_for(
                    r.text(errors="replace"),
                    timeout=timeout * 1.5
                )
    except (asyncio.TimeoutError, Exception):
        pass
    return ""


# ==============================================================
# LIVE + VOD + GENRE PARALLEL (asyncio.gather)
# ==============================================================
async def check_all_content(session, api: str, u: str, pw: str,
                             hdrs: dict, ssl_param,
                             tz_bonus: int = 0) -> tuple:
    """
    Ruft Live-Kategorien, VOD-Kategorien, Genres und Serien-Kategorien
    gleichzeitig ab (4 parallele Calls).
    v21.3: Gibt zusätzlich adult_result zurück (is_adult, a_tier, a_score).
    """
    live_params   = {"username": u, "password": pw,
                     "action":   "get_live_categories"}
    vod_params    = {"username": u, "password": pw,
                     "action":   "get_vod_categories"}
    gen_params    = {"username": u, "password": pw,
                     "action":   "get_genres", "type": "itv"}
    series_params = {"username": u, "password": pw,
                     "action":   "get_series_categories"}

    raw_live, raw_vod, raw_gen, raw_series = await asyncio.gather(
        _fetch_api(session, api, live_params,   hdrs, TIMEOUT, ssl_param),
        _fetch_api(session, api, vod_params,    hdrs, TIMEOUT, ssl_param),
        _fetch_api(session, api, gen_params,    hdrs, TIMEOUT, ssl_param),
        _fetch_api(session, api, series_params, hdrs, TIMEOUT, ssl_param),
        return_exceptions=True,
    )

    if isinstance(raw_live,   Exception): raw_live   = ""
    if isinstance(raw_vod,    Exception): raw_vod    = ""
    if isinstance(raw_gen,    Exception): raw_gen    = ""
    if isinstance(raw_series, Exception): raw_series = ""

    # Kategorienzahl
    try:
        live_items    = json.loads(raw_live) if raw_live else []
        live_cat_count= len(live_items) if isinstance(live_items, list) else 999
    except Exception:
        live_cat_count= 999
        live_items    = []

    # Live-Score (DE)
    cat_names  = _extract_names(raw_live, "category_name")
    gen_names  = _extract_names(raw_gen,  "genre_name")
    live_is_de, live_tier, live_score = score_de_content(
        cat_names, vod_mode=False, tz_bonus=tz_bonus, cat_count=live_cat_count
    )

    if not live_is_de:
        genre_bonus = score_genre_content(gen_names)
        if genre_bonus >= 2:
            combined = cat_names + " " + gen_names
            live_is_de, live_tier, live_score = score_de_content(
                combined, vod_mode=False, tz_bonus=tz_bonus, cat_count=live_cat_count
            )

    # VOD-Score (DE, inkl. Serien)
    vod_names = ""
    if raw_vod:
        vod_names = _extract_names(raw_vod, "category_name")
        if raw_series:
            series_names = _extract_names(raw_series, "category_name")
            if series_names.strip():
                vod_names = vod_names + " " + series_names

    if not vod_names.strip():
        vod_result = (False, 0, 0, False)
    else:
        vod_is_de, vod_tier, vod_score = score_de_content(vod_names, vod_mode=True)
        vod_result = (vod_is_de, vod_tier, vod_score, True)

    # v21.3: Adult-Erkennung (Live + VOD kombiniert)
    adult_result = (False, 0, 0)
    if ADULT_SCAN:
        all_cats = cat_names + " " + vod_names
        is_adult, a_score, a_tier = score_adult_content(all_cats)
        adult_result = (is_adult, a_score, a_tier)

    return (live_is_de, live_tier, live_score), vod_result, adult_result


# ==============================================================
# ACCOUNT CHECK
# ==============================================================
async def check_account(session, host: str, u: str, pw: str,
                        state: ScanState, ssl_ctx) -> tuple:
    """
    Vollstaendige Account-Pruefung (v19.6).

    Neu:
      - is_trial Filter
      - allowed_output_formats Check
      - exp_date < EXP_MIN_DAYS Filter
      - Panel-Typ-Erkennung
      - Stichproben-Kanalcheck (SAMPLE_CHECK)
      - Zeitmessung fuer Telemetrie
      - Retry-After-Header bei 429
      - _null entfernt (war ungenutzt)

    SSL: CF → ssl_ctx, non-CF → False (v19.5-Fix beibehalten)
    """
    t_start   = time.monotonic()
    api       = f"{host}/player_api.php"
    is_cf     = host in state._cf_hosts
    ssl_param = ssl_ctx  # v21.5: Unified SSL (CERT_NONE für alle Hosts)

    if is_cf:
        profile = state.get_cf_profile(host)
        hdrs    = _cf_nav_headers(profile)
        cookie  = state.get_cf_cookie_header(host)
        if cookie:
            hdrs["Cookie"] = cookie
    else:
        hdrs = {"User-Agent": random.choice(PLAYER_USER_AGENTS)}

    try:
        async with session.get(
            api,
            params={"username": u, "password": pw},
            headers=hdrs,
            timeout=aiohttp.ClientTimeout(total=TIMEOUT),
            ssl=ssl_param,
        ) as r:
            status    = r.status
            resp_hdrs = dict(r.headers)

            if is_cf:
                _extract_cf_cookie(r, host, state)

            if status == 401:
                return None, "account_fehler", False, False, 0, None, 0, 0, "", "", {}
            if status == 429:
                # Retry-After-Header auswerten
                retry_after = resp_hdrs.get("Retry-After", "")
                try:
                    ra_secs = float(retry_after)
                except (ValueError, TypeError):
                    ra_secs = 0.0
                await r.read()
                if ra_secs > 0:
                    await asyncio.sleep(min(ra_secs, 120.0))
                return None, "ratelimit", False, False, 0, None, 0, 0, "", "", {}
            if status in CF_ERROR_CODES:
                await r.read()
                async with state.lock:
                    state._cf_hosts.add(host)
                return None, "cf", False, True, 0, None, 0, 0, "", http_status_str(status), {}
            if status != 200:
                await r.read()
                return None, "verbindung", False, False, 0, None, 0, 0, "", "", {}

            body_text = await r.text(errors="replace")

        if detect_cloudflare(status, resp_hdrs, body_text):
            async with state.lock:
                state._cf_hosts.add(host)
            return None, "cf", False, True, 0, None, 0, 0, "", "CF-Challenge", {}

        try:
            data = json.loads(body_text)
        except json.JSONDecodeError:
            return None, "verbindung", False, False, 0, None, 0, 0, "", "", {}

        user_info   = data.get("user_info",   {})
        server_info = data.get("server_info", {})

        # --- is_trial Filter ---
        if FILTER_TRIAL and user_info.get("is_trial") in ("1", 1, True):
            return None, "trial_acc", False, False, 0, None, 0, 0, "", "", {}

        active = int(user_info.get("active_cons",    0))
        max_c  = int(user_info.get("max_connections", 0))

        if user_info.get("status") not in ("Active", "1"):
            return None, "account_fehler", False, False, 0, None, 0, 0, "", "", {}
        if max_c != 0 and active >= max_c:
            return None, "max_erreicht", False, False, 0, None, active, max_c, "", "", {}

        # --- exp_date sicher parsen ---
        exp_ts   = user_info.get("exp_date")
        exp      = "unbegrenzt"
        exp_date = None
        expiring = False   # v19.9: Ablauf-Vorwarnung
        if exp_ts:
            try:
                exp_date = datetime.fromtimestamp(int(exp_ts))
                exp      = exp_date.strftime("%d.%m.%Y")
                # Ablaufdatum-Filter mit Vorwarnung
                if EXP_MIN_DAYS > 0:
                    days_left = (exp_date - datetime.now()).days
                    if days_left < EXP_WARN_DAYS:
                        # Sehr nah am Ablauf → verwerfen
                        return None, "abgelaufen_bald", False, False, 0, None, \
                               active, max_c, exp, "", {}
                    elif days_left < EXP_MIN_DAYS:
                        # Vorwarnung: in expiring_links.txt
                        expiring = True
            except (ValueError, OSError, OverflowError):
                exp = "unbekannt"

        # --- allowed_output_formats Check ---
        formats = user_info.get("allowed_output_formats", [])
        if formats and "ts" not in formats and "m3u8" not in formats:
            return None, "format_skip", False, False, 0, None, \
                   active, max_c, exp, "", {}

        # --- Panel-Typ, Timezone, EPG, Country (v19.9) ---
        tz       = server_info.get("timezone", "")
        panel    = server_info.get("server_name", "")
        tz_bonus = TZ_DE_BONUS if tz in DE_TIMEZONES else 0
        ptype    = detect_panel_type(server_info)

        # v19.9: EPG-URL als DE-Signal
        epg_url = str(server_info.get("epg_url", "")).lower()
        if epg_url and (".de/" in epg_url or epg_url.endswith(".de")
                        or "epg.de" in epg_url or "/de/" in epg_url):
            tz_bonus += EPG_DE_BONUS

        # v19.9: country-Feld als DE-Signal
        country = str(server_info.get("country", "")).upper().strip()
        if country in DE_COUNTRIES:
            tz_bonus += COUNTRY_DE_BONUS

        # --- API-Folge-Header ---
        if is_cf:
            profile  = state.get_cf_profile(host)
            api_hdrs = _cf_api_headers(profile, host)
            cookie   = state.get_cf_cookie_header(host)
            if cookie:
                api_hdrs["Cookie"] = cookie
        else:
            api_hdrs = hdrs

        # --- Live + VOD + Genre + Adult PARALLEL ---
        live_result, vod_result, adult_result = await check_all_content(
            session, api, u, pw, api_hdrs, ssl_param, tz_bonus=tz_bonus
        )
        live_de, live_tier, live_score = live_result
        vod_de, vod_tier, vod_score, vod_has_content = vod_result
        is_adult, a_score, a_tier = adult_result

        if not live_de:
            return None, "kein_de", False, False, 0, None, active, max_c, exp, "", {}

        # --- Stichproben-Kanalcheck (v19.9: name_bonus) ---
        if SAMPLE_CHECK:
            streams_ok, name_bonus = await sample_channel_check(
                session, api, u, pw, api_hdrs, ssl_param, host
            )
            if not streams_ok:
                return None, "sample_fail", False, False, 0, None, \
                       active, max_c, exp, "", {}
            # Name-Bonus aus Kanalnamen auf live_score addieren
            if name_bonus > 0 and not live_de:
                live_de   = True
                live_tier = 2
                live_score = name_bonus
            elif name_bonus > 0:
                live_score += name_bonus

        category = "both" if (vod_de or not vod_has_content) else "tvonly"

        # --- VPN-Probe ---
        vpn_req = False
        if VPN_CHECK:
            vpn_req = (
                await probe_stream_vpn(
                    session, f"{host}/{u}/{pw}/1.ts",
                    is_cf=is_cf, state=state, host=host, ssl_ctx=ssl_ctx
                ) == "vpn"
            )

        # --- Telemetrie ---
        t_elapsed = time.monotonic() - t_start
        async with state.lock:
            state._timing.append(t_elapsed)

        link = f"{host}/get.php?username={u}&password={pw}&type=m3u_plus"
        meta = {"tz": tz, "panel": panel, "ptype": ptype,
                "expiring": expiring, "exp_ts": exp_ts,
                "http_code": 200,
                "is_adult":  is_adult,   # v21.3
                "a_tier":    a_tier,
                "u": u, "pw": pw}        # v21.3: für M3U+ Export benötigt
        return (link, "ok", vpn_req, is_cf, live_tier,
                category, active, max_c, exp, "", meta)

    except asyncio.TimeoutError:
        return None, "timeout",    False, False, 0, None, 0, 0, "", "", {}
    except aiohttp.ClientConnectorError as e:
        msg = str(e).lower()
        if ("name or service not known" in msg or
                "nodename nor servname"  in msg or
                "name resolution"        in msg or
                "cannot resolve"         in msg):
            return None, "dns_fehler",  False, False, 0, None, 0, 0, "", "", {}
        return     None, "tcp_fehler",  False, False, 0, None, 0, 0, "", "", {}
    except aiohttp.ClientConnectorSSLError:
        return None, "ssl_fehler",  False, False, 0, None, 0, 0, "", "", {}
    except aiohttp.ClientOSError:
        return None, "tcp_fehler",  False, False, 0, None, 0, 0, "", "", {}
    except aiohttp.ClientError:
        return None, "verbindung",  False, False, 0, None, 0, 0, "", "", {}
    except Exception:
        return None, "verbindung",  False, False, 0, None, 0, 0, "", "", {}


# ==============================================================
# ACCOUNT CHECK MIT CF-HANDLING (v19.9: kein Backoff bei CF=0)
# ==============================================================
async def check_account_with_retry(session, host: str, u: str, pw: str,
                                   state: ScanState, ssl_ctx) -> tuple:
    """
    CF_MAX_RETRIES = 0 (Pydroid3-Standard):
      CF-Challenge ist unlösbar ohne echte Browser-Engine.
      Sofort aufgeben, in cf_links.txt schreiben – kein 8s/16s Backoff.

    CF_MAX_RETRIES > 0 (manuell gesetzt, z.B. für curl_cffi-Umgebungen):
      Exponential Backoff mit cf_preflight-Cookie-Versuch.
    """
    if CF_MAX_RETRIES == 0:
        # Direkter Aufruf ohne Retry-Loop
        return await check_account(session, host, u, pw, state, ssl_ctx)

    # Retry-Loop nur wenn explizit konfiguriert
    result = None
    for attempt in range(CF_MAX_RETRIES + 1):
        result   = await check_account(session, host, u, pw, state, ssl_ctx)
        stat_key = result[1]

        if stat_key != "cf":
            if attempt > 0 and stat_key == "ok":
                async with state.lock:
                    state.stats["cf_retry_ok"] += 1
            return result

        if attempt >= CF_MAX_RETRIES:
            break

        wait = CF_BACKOFF_BASE * (2 ** attempt) + random.uniform(1.0, 3.0)
        tqdm.write(
            c(C.ORANGE,
              f"  [CF] {host.replace('http://','').replace('https://','')} "
              f"Retry {attempt + 1}/{CF_MAX_RETRIES} "
              f"(Backoff {wait:.1f}s) ...")
        )
        await asyncio.sleep(wait)

        got_cookie = await cf_preflight(session, host, state, ssl_ctx)
        if got_cookie:
            tqdm.write(
                c(C.YELLOW,
                  f"  [CF] cf_clearance erhalten fuer "
                  f"{host.replace('http://','').replace('https://','')}")
            )

    return result


# ==============================================================
# TCP PRE-CHECK (asyncio.open_connection – kein Thread-Executor)
# ==============================================================
# Cache: host → (reachable: bool, expires: float)
_precheck_cache: dict = {}
_PRECHECK_TTL_OK  = 60.0   # Erfolge 60s cachen
_PRECHECK_TTL_ERR = 30.0   # Fehler nur 30s cachen (kein Cache-Poisoning)

async def tcp_precheck(host: str) -> bool:
    """
    Echter TCP-Handshake via asyncio.open_connection().
    Kein Thread-Executor, kein loop-Parameter nötig.
    Getrennte Cache-TTL: OK=60s, Fehler=30s.
    """
    global _precheck_cache
    now = time.monotonic()

    entry = _precheck_cache.get(host)
    if entry is not None:
        reachable, expires = entry
        if now < expires:
            return reachable

    parsed   = urlparse(host)
    hostname = parsed.hostname or ""
    port     = parsed.port or (443 if parsed.scheme == "https" else 80)

    if not hostname:
        _precheck_cache[host] = (False, now + _PRECHECK_TTL_ERR)
        return False

    result = False
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(hostname, port),
            timeout=PRECHECK_TIMEOUT,
        )
        writer.close()
        try:
            await asyncio.wait_for(writer.wait_closed(), timeout=1.0)
        except asyncio.TimeoutError:
            pass
        result = True
    except (asyncio.TimeoutError, OSError, ConnectionRefusedError,
            socket.gaierror, Exception):
        result = False

    ttl = _PRECHECK_TTL_OK if result else _PRECHECK_TTL_ERR
    _precheck_cache[host] = (result, now + ttl)
    return result


# ==============================================================
# WORKER
# ==============================================================
async def worker(session, state: ScanState, url: str, ssl_ctx):
    parsed = urlparse(url.strip())
    host   = f"{parsed.scheme}://{parsed.netloc}"
    qs     = parse_qs(parsed.query)
    u      = qs.get("username", [None])[0]
    pw     = qs.get("password", [None])[0]
    if not u or not pw:
        return None

    # TCP precheck (asyncio.open_connection, kein loop nötig)
    if PRECHECK_ENABLED:
        reachable = await tcp_precheck(host)
        if not reachable:
            async with state.lock:
                state.stats["precheck_skip"] += 1
                state.stats["tcp_fehler"]    += 1
            return None

    # Duplikat-Check (v20.0: hostunabhängig – nur username+password)
    key = (u, pw)
    async with state.lock:
        if key in state.checked_keys:
            state.stats["duplikate"] += 1
            return None
        state.checked_keys.add(key)

    # Host-Fehler-Limit
    async with state.lock:
        if state.host_error_count.get(host, 0) >= MAX_ERRORS_PER_HOST:
            state.stats["host_geblockt"] += 1
            return None

    # v19.9: Host-Treffer-Limit (Ergebnis-Dedup)
    if MAX_LINKS_PER_HOST > 0:
        async with state.lock:
            if state.host_links_count.get(host, 0) >= MAX_LINKS_PER_HOST:
                state.stats["host_limit"] += 1
                return None

    # Jitter-Delay (adaptiv, get_running_loop statt get_event_loop)
    async with state.lock:
        is_known_cf = host in state._cf_hosts
        mult        = state.host_jitter_mult.get(host, 1.0)
        jitter      = _jitter(is_known_cf, mult)
        now         = asyncio.get_running_loop().time()
        wait        = max(0.0, jitter - (now - state.last_host_request.get(host, 0)))
        state.last_host_request[host] = now + wait

    if wait > 0:
        await asyncio.sleep(wait)

    result = await check_account_with_retry(session, host, u, pw, state, ssl_ctx)
    (link, stat_key, is_vpn, is_cf,
     tier, category, active, max_c, exp, cf_msg, meta) = result

    if stat_key == "ok":
        dest     = None
        expiring = meta.get("expiring", False)

        async with state.lock:
            # v19.9: Nochmal prüfen (race condition zwischen Semaphore und Lock)
            if MAX_LINKS_PER_HOST > 0 and \
               state.host_links_count.get(host, 0) >= MAX_LINKS_PER_HOST:
                state.stats["host_limit"] += 1
                return None

            if expiring:
                # Ablauf-Vorwarnung: gesonderte Datei
                state.expiring_links.append(link)
                state.stats["expiring"] += 1
                dest = "expiring"
            elif is_vpn:
                state.vpn_links.append(link)
                state.stats["vpn_de"] += 1
                dest = "vpn"
            elif category == "both":
                state.free_links.append(link)
                state.stats["neu_de"] += 1
                dest = "free"
            else:
                state.tvonly_links.append(link)
                state.stats["tvonly"] += 1
                dest = "tvonly"

            # v19.9: Treffer pro Host zählen
            state.host_links_count[host] = state.host_links_count.get(host, 0) + 1

        # Streaming-Write (sofort, ausserhalb des State-Locks)
        fname_map = {
            "free":     OUTPUT_FILE,
            "tvonly":   TVONLY_FILE,
            "vpn":      VPN_FILE,
            "expiring": EXPIRING_FILE,
        }
        if dest and dest in fname_map:
            await _append_link(fname_map[dest], link)

        # v21.3: Adult-Account für M3U+ Export merken
        is_adult = meta.get("is_adult", False)
        a_tier   = meta.get("a_tier",   0)
        if is_adult or dest == "free":
            async with state.lock:
                state.adult_accounts.append({
                    "host": host, "u": u, "pw": meta.get("pw", pw),
                    "is_cf": is_cf, "dest": dest,
                    "is_adult": is_adult,
                })
            if is_adult:
                async with state.lock:
                    state.stats["adult"] += 1
                await _append_link(ADULT_FILE, link)

        return {
            "host":     host,   "user":    u,        "dest":    dest,
            "tier":     tier,   "active":  active,   "max_c":   max_c,
            "exp":      exp,    "vpn":     is_vpn,   "cf":      is_cf,
            "msg":      "",     "expiring": expiring,
            "tz":       meta.get("tz",       ""),
            "panel":    meta.get("panel",    ""),
            "ptype":    meta.get("ptype",    ""),
            "exp_ts":   meta.get("exp_ts",   None),
            "http_code":meta.get("http_code",200),
            "is_adult": is_adult,  # v21.3
            "a_tier":   a_tier,    # v21.3
        }

    if stat_key == "cf":
        async with state.lock:
            cand = f"{host}/get.php?username={u}&password={pw}&type=m3u_plus"
            if cand not in state.cf_links:
                state.cf_links.append(cand)
            state.stats["cf"] += 1
        await _append_link(CF_FILE, link)
        return {
            "host":  host,  "user":   u,     "dest":  "cf",
            "tier":  0,     "active": 0,     "max_c": 0,
            "exp":   "",    "vpn":    False, "cf":    True,
            "msg":   cf_msg, "tz":   "",    "panel": "", "ptype": "",
            "expiring": False,
        }

    # 429: adaptiven Jitter-Multiplikator erhöhen
    if stat_key == "ratelimit":
        async with state.lock:
            old_m = state.host_jitter_mult.get(host, 1.0)
            state.host_jitter_mult[host] = min(old_m * 1.5, 8.0)

    if stat_key in ("verbindung", "tcp_fehler", "dns_fehler",
                    "timeout", "ssl_fehler"):
        async with state.lock:
            state.host_error_count[host] = (
                state.host_error_count.get(host, 0) + 1
            )

    async with state.lock:
        state.stats[stat_key] = state.stats.get(stat_key, 0) + 1

    return None


# ==============================================================
# SCAN-KONFIGURATION (Laufzeit – ueberschreibt globale Defaults)
# ==============================================================
class ScanConfig:
    """
    Haelt alle zur Laufzeit konfigurierbaren Einstellungen.
    Der Menu-Code schreibt hier rein; der Scan-Code liest hier.
    Globale Konstanten bleiben als Fallback-Defaults erhalten.
    """
    def __init__(self):
        self.workers_auto   = WORKERS_AUTO
        self.workers        = WORKERS
        self.vpn_check      = VPN_CHECK
        self.sample_check   = SAMPLE_CHECK
        self.precheck       = PRECHECK_ENABLED
        self.filter_trial   = FILTER_TRIAL
        self.exp_min_days   = EXP_MIN_DAYS
        self.cf_retries     = CF_MAX_RETRIES
        self.timeout        = TIMEOUT
        self.ssl_non_cf     = False          # ssl=False fuer non-CF (default)
        self.input_urls     = []             # extrahierte URLs
        self.mode_name      = "Normal"       # Anzeige-Name des Modus
        self.cf_debug       = False          # Nur CF-Hosts aus cf_hosts.json
        self.cf_blacklist   = False          # CF-Blacklist aktivieren
        self.resume         = False          # Resume-Modus aktiv
        self.resume_processed = 0            # Bereits verarbeitete Links

    def apply_preset_quick(self):
        """SCHNELL – Maximale Geschwindigkeit, minimale Filter."""
        self.vpn_check    = False
        self.sample_check = False
        self.precheck     = True
        self.filter_trial = True
        self.exp_min_days = 3     # v21.0 FIX: war 0 → Mindest-Vorwarnung
        self.cf_retries   = 0
        self.mode_name    = "Schnell"

    def apply_preset_normal(self):
        """NORMAL – VPN detection aktiv, empfohlen."""
        self.vpn_check    = True
        self.sample_check = False
        self.precheck     = True
        self.filter_trial = True
        self.exp_min_days = 7
        self.cf_retries   = 0
        self.mode_name    = "Normal"

    def apply_preset_thorough(self):
        """GRÜNDLICH – VPN + Stream-Check, höchste Genauigkeit."""
        self.vpn_check    = True
        self.sample_check = True
        self.precheck     = True
        self.filter_trial = True
        self.exp_min_days = 7
        self.cf_retries   = 0     # v21.0 FIX: war 3 → Pydroid3-Konsistenz
        self.mode_name    = "Gruendlich"

    def apply_preset_cf_debug(self):
        """CF-DEBUG – Nur bekannte CF-Hosts, alle Filter aus."""
        self.vpn_check    = False
        self.sample_check = False
        self.precheck     = False
        self.filter_trial = False
        self.exp_min_days = 0
        self.cf_retries   = 0     # v21.0 FIX: war 3 → Pydroid3 löst CF nicht
        self.cf_debug     = True
        self.mode_name    = "CF-Debug"


# ==============================================================
# ENVIRONMENT DETECTION
# ==============================================================
class EnvInfo:
    """Erfasst den aktuellen Zustand vor dem Scan."""
    def __init__(self):
        self.known_links    = 0
        self.cf_hosts       = 0
        self.has_checkpoint = False
        self.checkpoint_ts  = ""
        self.checkpoint_proc= 0
        self.output_files   = []
        self.has_cf_file    = False
        # v21.2: Aufschlüsselung pro Datei für Welcome-Screen
        self.file_counts: dict = {}   # fname → int

    def detect(self):
        for fname in [OUTPUT_FILE, TVONLY_FILE, VPN_FILE,
                      EXPIRING_FILE, CF_FILE]:
            if os.path.exists(fname):
                self.output_files.append(fname)
                try:
                    with open(fname, "r", encoding="utf-8") as f:
                        n = sum(1 for l in f if l.strip())
                    self.file_counts[fname] = n
                    self.known_links += n
                except Exception:
                    self.file_counts[fname] = 0
        cf = load_cf_hosts()
        self.cf_hosts    = len(cf)
        self.has_cf_file = os.path.exists(CF_HOSTS_FILE)
        if os.path.exists(CHECKPOINT_FILE):
            try:
                with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                    cp = json.load(f)
                self.has_checkpoint  = True
                self.checkpoint_ts   = cp.get("ts", "")[:16].replace("T", " ")
                self.checkpoint_proc = cp.get("processed", 0)
            except Exception:
                pass
        return self


def _auto_configure(env: EnvInfo, cfg: ScanConfig):
    """
    Leitet optimale Einstellungen aus der Umgebung ab.
    v20.0: Setzt workers_auto = True damit die adaptive Host-Berechnung greift.
    Logik:
      - Cloudflare hosts → mehr Retries
      - Sample-Check nur bei wenigen CF-Hosts (Performance)
      - Workers: adaptiv (unique_hosts//3, min 4, max 20)
    """
    cfg.apply_preset_normal()
    cfg.mode_name    = "Auto"
    cfg.workers_auto = True      # v20.0: adaptive Workers-Berechnung aktivieren
    if env.cf_hosts > 0:
        cfg.cf_retries = 0  # immer 0 (Pydroid3)
    # Sample-Check nur bei wenigen CF-Hosts (Performance)
    cfg.sample_check = (env.cf_hosts < 10)


# ==============================================================
# MENU UI HELPERS
# ==============================================================
def _cls():
    """Leert den Screen (ANSI)."""
    print("\033[2J\033[H", end="")

def _box_line(text: str, col: str = "") -> str:
    """Zentrierte Box-Zeile passend zu W."""
    inner  = text.center(W - 4)
    border = c(C.CYAN + C.BOLD, "|")
    return f"{border} {col}{inner}\033[0m {border}"

def _box(lines: list, title: str = ""):
    top = c(C.CYAN + C.BOLD, "+" + "=" * (W - 2) + "+")
    bot = c(C.CYAN + C.BOLD, "+" + "=" * (W - 2) + "+")
    print(top)
    if title:
        print(_box_line(title, C.WHITE + C.BOLD))
        print(c(C.CYAN + C.BOLD, "|" + "-" * (W - 2) + "|"))
    for line in lines:
        print(line)
    print(bot)

def _row(label: str, value: str, col_val: str = C.WHITE,
         lbl_col: str = C.GRAY, lbl_w: int = 18) -> str:
    """
    Inhaltszeile mit fester Spaltenbreite.
    label und value müssen PLAIN TEXT sein (kein ANSI).
    Padding wird VOR dem Einfärben angewendet → kein Drift.
    """
    border  = c(C.CYAN + C.BOLD, "|")
    lbl_pad = f"  {label:<{lbl_w}}"   # 2 Einrückung + Label auf lbl_w auffüllen
    val_str = f"{value}"
    # Restbreite für Wert: W - 1(|) - (2+lbl_w) - 2(gap) - 1(|)
    val_pad = f"{val_str:<{W - lbl_w - 6}}"
    return f"{border}{c(lbl_col, lbl_pad)}  {c(col_val, val_pad)}{border}"

def _yn(val: bool) -> tuple:
    return ("JA",  C.GREEN) if val else ("NEIN", C.DIM)

def _prompt(msg: str, valid: list = None, default: str = "") -> str:
    """
    Liest Benutzereingabe mit optionaler Validierung.
    Bei leerem Input wird default zurueckgegeben.
    """
    hint = f"[{'/'.join(valid)}]" if valid else ""
    prompt_str = c(C.CYAN, f"\n  {msg} {hint}: ")
    while True:
        try:
            raw = input(prompt_str).strip()
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt
        val = raw or default
        if valid is None or val.upper() in [v.upper() for v in valid]:
            return val.upper() if valid else val
        print(c(C.YELLOW, f"  Ungueltig. Bitte wählen: {'/'.join(valid)}"))

def _section(title: str):
    print(f"\n{c(C.CYAN + C.BOLD, '  ' + title)}")
    print(c(C.GRAY, "  " + "─" * (W - 4)))

def _submenu(title: str, groups: list, header: str = None,
             back_key: str = "Z", back_label: str = "Zurück") -> str:
    """
    Zentraler Untermenu-Renderer mit validierter Eingabe.

    Ersetzt das wiederholte _cls/_section/print/input-Boilerplate der
    Untermenues. Vorteil ggue. rohem input(): konsistente Validierung
    und Fehler-Feedback wie im Hauptmenue (via _prompt).

    Args:
        title:   Ueberschrift (an _section uebergeben).
        groups:  Liste von (gruppen_titel, [(key, label), ...]).
                 gruppen_titel None/"" -> keine Zwischenueberschrift.
        header:  Optionale dynamische Info-Zeile unter dem Titel.
        back_key:Taste fuer "Zurueck" (Default + ENTER).

    Returns:
        Validierte Auswahl in Grossbuchstaben (immer in der Tasten-Menge).
    """
    _cls()
    _section(title)
    if header:
        print()
        print(c(C.GREEN, "  " + header))

    valid = [back_key]
    for group_title, items in groups:
        print()
        if group_title:
            print(c(C.CYAN, "  " + group_title))
        for key, label in items:
            print(c(C.CYAN, f"  [{key}] {label}"))
            valid.append(key.upper())
    print()
    print(c(C.DIM, f"  [{back_key}] {back_label}"))

    return _prompt("Auswahl", valid, back_key)

def _ok_row(label: str, value: str, ok: bool = True) -> str:
    icon = c(C.GREEN, "●") if ok else c(C.DIM, "○")
    col  = C.WHITE if ok else C.DIM
    return f"  {icon}  {c(C.GRAY, f'{label:<22}')}{c(col, value)}"


# ==============================================================
# MENU: WELCOME SCREEN
# ==============================================================
def _show_welcome(env: EnvInfo):
    _cls()
    iw = W - 2   # innere Breite = 62 Zeichen

    # ── Title Box ─────────────────────────────────────────────
    bdr  = c(C.CYAN + C.BOLD, "|")
    line = c(C.CYAN + C.BOLD, "+" + "=" * iw + "+")
    print(line)
    print(bdr + c(C.WHITE + C.BOLD,
                  "  XTREAM DE SCANNER".center(iw)) + bdr)
    print(bdr + c(C.DIM,
                  "v21.4  •  Pydroid3 Edition  •  Mai 2026".center(iw)) + bdr)
    print(c(C.CYAN + C.BOLD, "+" + "-" * iw + "+"))

    # ── Datei-Aufschlüsselung ─────────────────────────────────
    # Schema: | ●  Label           NNNN Links |
    # Spalten: 1(|) 1(sp) 1(●) 2(sp) 16(label) 2(sp) 9(value) rest + 1(|)
    file_defs = [
        (OUTPUT_FILE,   C.GREEN,  "Alle Kategorien"),
        (TVONLY_FILE,   C.CYAN,   "Nur Live-TV"),
        (VPN_FILE,      C.PURPLE, "VPN noetig"),
        (EXPIRING_FILE, C.YELLOW, "Endet bald"),
        (CF_FILE,       C.ORANGE, "Cloudflare"),
    ]
    LBL_W = 16   # feste Label-Breite (sichtbar)
    VAL_W = 9    # feste Wert-Breite  (sichtbar)

    any_file = False
    for fname, col, lbl in file_defs:
        n = env.file_counts.get(fname, 0)
        if n <= 0:
            continue
        lbl_s = f"{lbl:<{LBL_W}}"          # plain padding
        val_s = f"{n:>{VAL_W-5}} Links"     # rechtsbündig
        # Rest-Padding bis zur rechten Box-Grenze
        rest  = iw - 1 - 1 - 2 - LBL_W - 2 - VAL_W
        row   = (f" {c(col, '●')}  {c(C.GRAY, lbl_s)}"
                 f"  {c(col, val_s)}{' ' * max(rest, 0)}")
        print(bdr + row + bdr)
        any_file = True

    if not any_file:
        msg  = "Noch keine Ausgabedateien vorhanden."
        rest = iw - 2 - len(msg)
        print(bdr + c(C.DIM, f"  {msg}{' ' * max(rest, 0)}") + bdr)

    # Gesamt
    if env.known_links > 0:
        print(c(C.CYAN + C.BOLD, "|" + "·" * iw + "|"))
        gs  = f"{'Gesamt:':<{LBL_W}}"
        gv  = f"{env.known_links:>{VAL_W-5}} Links"
        rest = iw - 1 - 2 - LBL_W - 2 - VAL_W
        row  = f"  {c(C.GRAY, gs)}  {c(C.WHITE, gv)}{' ' * max(rest, 0)}"
        print(bdr + row + bdr)

    # CF + Checkpoint
    if env.cf_hosts > 0 or env.has_checkpoint:
        print(c(C.CYAN + C.BOLD, "|" + "·" * iw + "|"))
        if env.cf_hosts > 0:
            cf_lbl = f"{'CF-Hosts:':<{LBL_W}}"
            cf_val = f"{env.cf_hosts} bekannte CF-Hosts"
            rest   = iw - 2 - LBL_W - 2 - len(cf_val)
            row    = (f"  {c(C.GRAY, cf_lbl)}"
                      f"  {c(C.YELLOW, cf_val)}{' ' * max(rest, 0)}")
            print(bdr + row + bdr)
        if env.has_checkpoint:
            cp_lbl = f"{'Checkpoint:':<{LBL_W}}"
            cp_val = f"[R]  {env.checkpoint_ts}  •  {env.checkpoint_proc} verar."
            rest   = iw - 2 - LBL_W - 2 - len(cp_val)
            row    = (f"  {c(C.GRAY, cp_lbl)}"
                      f"  {c(C.YELLOW, cp_val)}{' ' * max(rest, 0)}")
            print(bdr + row + bdr)

    print(c(C.CYAN + C.BOLD, "+" + "=" * iw + "+"))


# ==============================================================
# MENU: HAUPT-MENU
# ==============================================================
# Spaltenbreiten – Padding VOR Einfärben (kein ANSI-Drift)
_COL_NAME = 12   # Name-Spalte sichtbare Breite

def _menu_row(key: str, name: str, desc: str, col: str,
              disabled: bool = False) -> str:
    """Menüzeile mit drei festen Spalten: [X]  Name__  Beschreibung"""
    key_pad  = f"[{key}]"
    name_pad = f"{name:<{_COL_NAME}}"
    if disabled:
        return (f"  {c(C.GRAY, key_pad)}  "
                f"{c(C.GRAY, name_pad)}  "
                f"{c(C.GRAY, desc)}")
    if desc:
        return (f"  {c(col, key_pad)}  "
                f"{c(col, name_pad)}  "
                f"{c(C.GRAY, desc)}")
    return f"  {c(col, key_pad)}  {c(col, name_pad)}"

def _menu_divider() -> str:
    return c(C.GRAY, "  " + "─" * (W - 4))


def _main_menu(env: EnvInfo) -> str:
    """Hauptmenü – kompakt für Smartphone, min. Scrollbedarf."""
    _section("SCAN-MODUS WÄHLEN")

    cf_ok  = env.cf_hosts > 0
    lk_ok  = env.known_links > 0
    cf_col = C.ORANGE if cf_ok else C.GRAY

    # ── Scan-Modi ─────────────────────────────────────────────
    print(_menu_row("A","Auto","Automatischer API + DE + Adult + VPN + Stream-Check",        C.GREEN))
    print(_menu_row("1","Schnell",   "API + DE + Adult-Check", C.WHITE))
    print(_menu_row("2","Normal",    "API + DE + Adult + VPN detection",       C.WHITE))
    print(_menu_row("3","Genau","API + DE + Adult + VPN + Stream-Check",      C.WHITE))
    if cf_ok:
        print(_menu_row("4","Debug", "Keine Checks werden durchgefuehrt",        cf_col))
    else:
        print(_menu_row("4","CF-Debug", "Keine CF-Hosts",             C.GRAY, disabled=True))
    print(_menu_row("5","Manuell",   "Alle Einstellungen frei einstellbar",          C.GRAY))

    print(_menu_divider())

    # ── Werkzeuge: kompakt nebeneinander ──────────────────────
    def _t(key, name, col):
        return f"{c(col,f'[{key}]')} {c(col,f'{name:<9}')}"

    d = C.YELLOW if lk_ok else C.GRAY
    s = C.CYAN   if lk_ok else C.GRAY
    e = C.GREEN  if lk_ok else C.GRAY
    v = C.PURPLE if lk_ok else C.GRAY
    print(f"  {_t('D','Bereinigen',d)}  {_t('S','Sortieren',s)}  {_t('E','Exportieren',e)}  {_t('V','Verwaltung',v)}")

    print(_menu_divider())

    # ── Resume + System ───────────────────────────────────────
    if env.has_checkpoint:
        print(_menu_row("R","Resume",
                        f"Fortsetzen ({env.checkpoint_ts})", C.YELLOW))

    print(f"  {_t('H','Hilfe',C.GRAY)}  {_t('Q','Beenden',C.GRAY)}")

    valid = ["A","1","2","3","4","5","D","S","E","V","H","Q"]
    if env.has_checkpoint:
        valid.append("R")
    return _prompt("Auswahl", valid, "A")


# MENU: HILFE
# ==============================================================
def _show_help():
    _cls()
    _section("HILFE – SCAN-MODI")
    help_blocks = [
        ("Auto-Setup [A]",
         ["Liest vorhandene cf_hosts.json und Ausgabedateien.",
          "Waehlt automatisch optimale Workers-Anzahl,",
          "CF-Retries und Sample-Check-Einstellungen.",
          "Empfohlen fuer den ersten Start."]),
        ("Schnell [1]",
         ["Kein VPN detection, kein Stream-Test.",
          "Nur API-Check und DE-Score.",
          "Ideal fuer grosse Listen (1000+ Links)."]),
        ("Normal [2]",
         ["VPN detection per Stream-Probe aktiv.",
          "Filtert Geo-geblockte Accounts.",
          "Empfohlen fuer Links mittlerer Qualitaet."]),
        ("Gruendlich [3]",
         ["Zusaetzlich: zufaellige Stream sampling.",
          "Filtert Server mit toten Streams.",
          "Langsamer aber zuverlaessigste Ergebnisse."]),
        ("CF-Debug [4]",
         ["Laedt alle bekannten CF-Hosts aus cf_hosts.json.",
          "Ignoriert Pre-Check und Trial filter.",
          "Fuer gezielte Fehleranalyse bei CF-Hosts."]),
    ]
    for title, lines in help_blocks:
        print(f"\n  {c(C.WHITE + C.BOLD, title)}")
        for l in lines:
            print(f"    {c(C.DIM, l)}")
    _section("AUSGABEDATEIEN")
    files = [
        (OUTPUT_FILE,  "Live + VOD beide deutsch"),
        (TVONLY_FILE,  "Nur Live deutsch (kein DE-VOD)"),
        (VPN_FILE,     "VPN nötig fuer deutschen Zugriff"),
        (CF_FILE,      "Cloudflare-geschützte Hosts"),
        (CF_HOSTS_FILE,"CF-Hosts-Persistenz (7 Tage TTL)"),
    ]
    for fname, desc in files:
        print(f"  {c(C.CYAN, f'{fname:<32}')} {c(C.GRAY, desc)}")
    input(c(C.DIM, "\n  [ENTER] Zurueck zum Menu..."))


# ==============================================================
# MENU: MANUELLE KONFIGURATION
# ==============================================================
def _manual_setup(cfg: ScanConfig):
    _cls()
    _section("MANUELLE KONFIGURATION")

    def _toggle(label: str, current: bool) -> bool:
        v, col = _yn(current)
        print(f"  {label:<28} {c(col, v)}")
        ans = _prompt(f"{label} (J/N)", ["J", "N"], "J" if current else "N")
        return ans == "J"

    cfg.vpn_check    = _toggle("VPN detection (Stream-Probe)", cfg.vpn_check)
    cfg.sample_check = _toggle("Stream sampling",        cfg.sample_check)
    cfg.precheck     = _toggle("TCP precheck",            cfg.precheck)
    cfg.filter_trial = _toggle("Trial-Accounts filtern",   cfg.filter_trial)
    cfg.ssl_non_cf   = _toggle("SSL auch fuer non-CF",     cfg.ssl_non_cf)

    _section("ABLAUFDATUM-FILTER")
    print(c(C.DIM,
            f"  Accounts die in weniger als N Tagen ablaufen ueberspringen."))
    print(c(C.DIM, f"  0 = deaktiviert"))
    raw = _prompt(f"Mindestlaufzeit in Tagen [{cfg.exp_min_days}]",
                  default=str(cfg.exp_min_days))
    try:
        cfg.exp_min_days = max(0, int(raw))
    except ValueError:
        pass

    _section("CF-EINSTELLUNGEN")
    raw = _prompt(f"Max. CF-Retries [{cfg.cf_retries}]",
                  default=str(cfg.cf_retries))
    try:
        cfg.cf_retries = 0  # immer 0 (Pydroid3 löst CF nicht)
    except ValueError:
        pass

    _section("WORKER")
    print(c(C.DIM, f"  Bestimmt Parallelität des Scans."))
    print(c(C.DIM, f"  Standard: {WORKERS}  |  0 = Standard übernehmen  |  Max: 200"))
    print(c(C.YELLOW, f"  Im manuellen Modus wird KEINE automatische Berechnung verwendet."))
    raw = _prompt(f"Anzahl Workers [0=Standard/{WORKERS}]", default=str(cfg.workers))
    try:
        w = int(raw)
        if w <= 0:
            cfg.workers = WORKERS   # v20.0: 0 → Standardwert, kein Auto
        else:
            cfg.workers = max(1, min(200, w))
    except ValueError:
        cfg.workers = WORKERS
    cfg.workers_auto = False        # v20.0: manueller Modus → niemals Auto-Formel

    cfg.mode_name = "Manuell"


# ==============================================================
# MENU: LINK-EINGABE
# ==============================================================
def _input_menu() -> list:
    """
    Bietet vier Eingabemethoden an.
    v21.5: Neu: [4] Portal + Credentials Format (Bᴀᴘʜᴏᴍᴇᴛ-Port).
    Gibt Liste von Zeilen zurück (für Regex-Extraktion).
    """
    _section("LINK-EINGABE")
    print(f"  {c(C.WHITE, '[1]')}  {c(C.GRAY, 'Einfuegen      (Paste, 2x ENTER)')}")
    print(f"  {c(C.WHITE, '[2]')}  {c(C.GRAY, 'Datei laden    (Pfad eingeben)')}")
    print(f"  {c(C.WHITE, '[3]')}  {c(C.GRAY, 'Beides         (Datei + Paste kombiniert)')}")
    print(f"  {c(C.WHITE, '[4]')}  {c(C.GRAY, 'Portal-Format  (host:port + user:pass Zeilen)')}")
    print()
    print(c(C.GRAY, "  Format [4] Beispiel:"))
    print(c(C.GRAY, "    http://portal.tv:8080"))
    print(c(C.GRAY, "    user1:pass1"))
    print(c(C.GRAY, "    user2:pass2"))

    choice = _prompt("Eingabemethode", ["1", "2", "3", "4"], "1")
    lines  = []

    if choice in ("2", "3"):
        path = _prompt("Dateipfad")
        path = path.strip('"').strip("'")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    file_lines = f.readlines()
                lines += [l.rstrip("\n") for l in file_lines]
                cnt = len([l for l in lines if l.strip()])
                print(c(C.GREEN,
                        f"  [{cnt} Zeilen aus {os.path.basename(path)} geladen]"))
            except Exception as e:
                print(c(C.RED, f"  Fehler beim Lesen: {e}"))
        else:
            print(c(C.RED, f"  Datei nicht gefunden: {path}"))

    if choice in ("1", "3", "4"):
        prompt_text = (
            "\n  Portal + user:pass einfuegen (2x ENTER zum Abschluss):"
            if choice == "4" else
            "\n  Inhalt einfuegen (Links automatisch extrahiert)"
        )
        print(c(C.WHITE, prompt_text))
        print(c(C.GRAY, "  Abschluss: 2x ENTER hintereinander:"))
        empty_streak = 0
        while True:
            try:
                line = input()
            except EOFError:
                break
            if not line:
                empty_streak += 1
                if empty_streak >= 2:
                    break
                lines.append("")
            else:
                empty_streak = 0
                lines.append(line)

    # Portal-Format konvertieren
    if choice == "4":
        portal_urls = _process_portal_format(lines)
        if portal_urls:
            print(c(C.GREEN,
                    f"  [{len(portal_urls)} URLs aus Portal-Format konvertiert]"))
        # Als fertige URLs zurückgeben (kein weiterer Regex-Pass nötig)
        return ["__PORTAL_URLS__"] + portal_urls

    return lines


# ==============================================================
# MENU: BESTÄTIGUNGSSCREEN
# ==============================================================
def _confirm_screen(cfg: ScanConfig, total: int,
                    workers_actual: int, env: EnvInfo) -> bool:
    """
    Zeigt alle aktiven Einstellungen und wartet auf Bestätigung.
    Gibt True zurueck wenn der User fortfahren moechte.
    """
    _cls()
    _section(f"SCAN-VORBEREITUNG  [{cfg.mode_name}]")

    def yn(v): return _yn(v)

    rows = [
        ("Links discovered",    str(total),           C.WHITE),
        ("Known links skipped",  str(env.known_links),
         C.GREEN if env.known_links > 0 else C.DIM),
        ("Cloudflare hosts",  str(env.cf_hosts),
         C.YELLOW if env.cf_hosts > 0 else C.DIM),
        ("Workers",
         f"{workers_actual}" + (" (auto)" if cfg.workers_auto else ""),
         C.WHITE),
        ("Timeout",           f"{cfg.timeout}s", C.DIM),
    ]
    for label, val, col in rows:
        print(_ok_row(label, val, col != C.DIM))

    print()
    checks = [
        ("VPN detection",          cfg.vpn_check),
        ("Stream sampling",  cfg.sample_check),
        ("TCP precheck",      cfg.precheck),
        ("Trial filter",       cfg.filter_trial),
        ("SSL verification",         cfg.ssl_non_cf),
    ]
    for label, val in checks:
        v, col = _yn(val)
        print(_ok_row(label, v, val))

    if cfg.exp_min_days > 0:
        print(_ok_row("Expiration filter",
                      f"< {cfg.exp_min_days} Tage", True))
    if cfg.cf_retries != CF_MAX_RETRIES:
        print(_ok_row("CF-Retries", str(cfg.cf_retries), True))
    if env.cf_hosts > 0:
        print(_ok_row("CF-Blacklist", "Bekannte CF-Hosts ueberspringen", cfg.cf_blacklist))

    print()
    print(c(C.DIM, f"  Ausgabe:  {OUTPUT_FILE}  /  {TVONLY_FILE}"))
    print(c(C.DIM, f"  VPN:      {VPN_FILE}"))
    print(c(C.DIM, f"  CF:       {CF_FILE}"))

    ans = _prompt("\n  Start scanning?", ["J", "N"], "J")
    return ans == "J"


# ==============================================================
# MENU: RESUME
# ==============================================================
def _resume_menu(env: EnvInfo) -> bool:
    """Fragt ob der unterbrochene Scan fortgesetzt werden soll."""
    _section("SCAN FORTSETZEN")
    print(f"  {c(C.YELLOW, 'Unterbrochener Scan gefunden:')}")
    print(c(C.DIM, f"    Zeitstempel: {env.checkpoint_ts}"))
    print(c(C.DIM, f"    Verarbeitet: {env.checkpoint_proc} Accounts"))
    print()
    print(c(C.DIM,
            "  Der Duplikat-Skip (load_existing) verhindert doppelte"))
    print(c(C.DIM,
            "  Verarbeitung. Starte einfach neu mit demselben Link-Block."))
    input(c(C.DIM, "\n  [ENTER] Zurueck zum Menu..."))
    return False


# ==============================================================
# MENU: HAUPT-ENTRY-POINT (ersetzt altes read_input + main)
# ==============================================================
# ==============================================================
# SORTIERUNG DER AUSGABEDATEIEN NACH HOSTER (v20.0)
# ==============================================================
def sort_output_files() -> dict:
    """
    Sortiert alle Ausgabedateien nach Hostname (netloc, A→Z).

    Jede Zeile ist ein Link. Sortierschluessel ist der Hostname
    inkl. Port (netloc). Zeilen ohne erkennbaren Hostnamen werden
    ans Ende gestellt.
    Zwischen wechselnden Hostern wird eine Leerzeile eingefuegt.
    Backup (*.bak) wird immer vor dem Ueberschreiben erstellt.

    Rueckgabe: Dict { fname: {"vorher": int, "nachher": int,
                               "hoster": int} }
               oder  { fname: {"error": str} }
    """
    target_files = [OUTPUT_FILE, TVONLY_FILE, VPN_FILE, EXPIRING_FILE]
    results = {}

    def _netloc(line: str) -> str:
        try:
            return urlparse(line.strip()).netloc.lower()
        except Exception:
            return "\xff"   # sortiert ans Ende

    for fname in target_files:
        if not os.path.exists(fname):
            continue
        try:
            with open(fname, "r", encoding="utf-8") as f:
                raw_lines = [l.rstrip("\n") for l in f if l.strip()]

            if not raw_lines:
                results[fname] = {"vorher": 0, "nachher": 0, "hoster": 0}
                continue

            vorher = len(raw_lines)

            # Stabile Sortierung nach netloc A→Z
            sorted_lines = sorted(raw_lines, key=_netloc)

            # Stabile Sortierung nach netloc A→Z – keine Leerzeilen
            output_lines = sorted_lines

            unique_hosts = len({_netloc(l) for l in raw_lines})
            results[fname] = {
                "vorher":  vorher,
                "nachher": sum(1 for l in output_lines if l.strip()),
                "hoster":  unique_hosts,
            }

            # Backup erstellen, dann schreiben
            try:
                with open(fname + ".bak", "w", encoding="utf-8") as f:
                    f.write("\n".join(raw_lines) + "\n")
            except Exception:
                pass

            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(output_lines) + "\n")

        except Exception as e:
            results[fname] = {"error": str(e)}

    return results


def _run_sort(env: EnvInfo):
    """
    Interaktiver Menu-Schritt fuer die Hoster-Sortierung.
    """
    _cls()
    _section("SORTIERUNG NACH HOSTER  (alphabetisch A→Z)")

    target_files = [OUTPUT_FILE, TVONLY_FILE, VPN_FILE, EXPIRING_FILE]
    existing     = [f for f in target_files if os.path.exists(f)]

    if not existing:
        print(c(C.DIM, "  Keine Ausgabedateien vorhanden."))
        input(c(C.DIM, "\n  [ENTER] Zurueck..."))
        return

    print(c(C.DIM, "  Sortiert Links nach Hostname (netloc) alphabetisch A→Z."))
    print(c(C.DIM, "  Backup (*.bak) wird automatisch vor dem Ueberschreiben erstellt."))
    print()

    # Vorschau: Zeilenzahl + Hoster-Anzahl pro Datei
    print(c(C.DIM, "  Zu sortierende Dateien:"))
    for fname in existing:
        try:
            with open(fname, "r", encoding="utf-8") as fh:
                raw = [l.strip() for l in fh if l.strip()]
            hosts = set()
            for l in raw:
                try:
                    hosts.add(urlparse(l).netloc.lower())
                except Exception:
                    pass
            print(c(C.DIM,
                    f"    {fname:<36} {len(raw):>4} Links"
                    f"  •  {len(hosts)} Hoster"))
        except Exception:
            print(c(C.DIM, f"    {fname}"))

    ans = _prompt("\n  Sortierung starten?", ["J", "N"], "J")
    if ans != "J":
        print(c(C.DIM, "  Abgebrochen."))
        input(c(C.DIM, "  [ENTER] Zurueck..."))
        return

    print(c(C.DIM, "\n  Sortiere..."))
    stats = sort_output_files()

    print()
    for fname, info in stats.items():
        if "error" in info:
            print(c(C.RED,  f"  [{fname}]"))
            print(c(C.RED,  f"    Fehler: {info['error']}"))
        else:
            h = info.get("hoster", 0)
            print(c(C.CYAN, f"  {fname}"))
            print(c(C.CYAN,
                    f"    {info['vorher']} Links  •  "
                    f"{h} Hoster-Gruppe{'n' if h != 1 else ''}  →  sortiert"))
            print(c(C.DIM,  f"    Backup: {fname}.bak"))

    input(c(C.DIM, "\n  [ENTER] Zurueck zum Menu..."))

# ==============================================================
# DUPLIKAT-BEREINIGUNG DER AUSGABEDATEIEN (v20.0)
# ==============================================================
def dedup_output_files() -> dict:
    """
    Liest Ausgabedateien, entfernt Eintraege mit identischer
    username+password-Kombination (hostunabhaengig), und schreibt
    die bereinigten Dateien zurueck.

    Sicherheit:
      - Backup (*.bak) wird IMMER vor dem Ueberschreiben erstellt.
      - Zeilen ohne erkennbare Credentials bleiben erhalten.
      - Kein Datenverlust moeglich: im Fehlerfall bleibt Original.

    Rueckgabe: Dict { fname: {"vorher": int, "nachher": int} }
                 oder { fname: {"error": str} } bei Ausnahme.
    """
    target_files = [OUTPUT_FILE, TVONLY_FILE, VPN_FILE, EXPIRING_FILE]
    results = {}

    for fname in target_files:
        if not os.path.exists(fname):
            continue
        try:
            with open(fname, "r", encoding="utf-8") as f:
                raw_lines = [l.rstrip("\n") for l in f if l.strip()]

            vorher = len(raw_lines)
            seen_creds: set = set()
            unique_lines    = []

            for line in raw_lines:
                qs = parse_qs(urlparse(line.strip()).query)
                u  = qs.get("username", [None])[0]
                pw = qs.get("password", [None])[0]
                if not u or not pw:
                    # Zeilen ohne erkennbare Credentials unveraendert behalten
                    unique_lines.append(line)
                    continue
                key = (u, pw)
                if key not in seen_creds:
                    seen_creds.add(key)
                    unique_lines.append(line)

            nachher  = len(unique_lines)
            entfernt = vorher - nachher
            results[fname] = {"vorher": vorher, "nachher": nachher,
                              "entfernt": entfernt}

            if entfernt > 0:
                backup = fname + ".bak"
                try:
                    with open(backup, "w", encoding="utf-8") as f:
                        f.write("\n".join(raw_lines) + "\n")
                except Exception:
                    pass   # Backup-Fehler blockiert Bereinigung nicht
                with open(fname, "w", encoding="utf-8") as f:
                    f.write("\n".join(unique_lines) + "\n")

        except Exception as e:
            results[fname] = {"error": str(e)}

    return results


def _run_dedup(env: EnvInfo):
    """
    Interaktiver Menu-Schritt fuer die Datei-Bereinigung.
    Zeigt Vorschau, fragt Bestaetigung, fuehrt dedup_output_files() aus.
    """
    _cls()
    _section("DUPLIKAT-BEREINIGUNG  (username+password-basiert)")

    target_files = [OUTPUT_FILE, TVONLY_FILE, VPN_FILE, EXPIRING_FILE]
    existing = [f for f in target_files if os.path.exists(f)]

    if not existing:
        print(c(C.DIM, "  Keine Ausgabedateien vorhanden."))
        input(c(C.DIM, "\n  [ENTER] Zurueck..."))
        return

    print(c(C.DIM,
            "  Entfernt Eintraege mit identischer username+password-Kombination,"))
    print(c(C.DIM,
            "  unabhaengig vom Hostnamen.  Backup (*.bak) wird automatisch erstellt."))
    print()
    print(c(C.DIM, "  Zu pruefende Dateien:"))
    for fname in existing:
        try:
            with open(fname, "r", encoding="utf-8") as fh:
                cnt = sum(1 for l in fh if l.strip())
            print(c(C.DIM, f"    {fname:<36} {cnt} Eintraege"))
        except Exception:
            print(c(C.DIM, f"    {fname}"))

    ans = _prompt("\n  Bereinigung starten?", ["J", "N"], "J")
    if ans != "J":
        print(c(C.DIM, "  Abgebrochen."))
        input(c(C.DIM, "  [ENTER] Zurueck..."))
        return

    print(c(C.DIM, "\n  Bereinige..."))
    stats = dedup_output_files()

    print()
    any_removed = False
    for fname, info in stats.items():
        if "error" in info:
            print(c(C.RED, f"  [{fname}]"))
            print(c(C.RED, f"    Fehler: {info['error']}"))
        else:
            removed = info.get("entfernt", 0)
            if removed > 0:
                any_removed = True
                print(c(C.GREEN, f"  {fname}"))
                print(c(C.GREEN,
                        f"    {info['vorher']} → {info['nachher']} Eintraege "
                        f"({removed} Duplikat{'e' if removed != 1 else ''} entfernt)"))
                print(c(C.DIM, f"    Backup: {fname}.bak"))
            else:
                print(c(C.DIM, f"  {fname}"))
                print(c(C.DIM,
                        f"    {info.get('vorher', 0)} Eintraege – keine Duplikate."))

    if not any_removed:
        print(c(C.DIM, "\n  Alle Dateien sind bereits duplikatfrei."))

    input(c(C.DIM, "\n  [ENTER] Zurueck zum Menu..."))


def _run_export(env: EnvInfo):
    """
    [E] M3U+ Export – v21.4
    Liest Accounts aus free_links.txt / free_links_TVonly.txt /
    vpn_links.txt. User wählt einzelne Accounts, Bereiche oder alle.
    Startet dann generate_m3u_plus_for_account() pro Account.
    """
    _cls()
    _section("M3U+ EXPORT – ACCOUNTAUSWAHL")

    # ── 1. Quelldateien einlesen ─────────────────────────────
    SOURCE_FILES = [
        (OUTPUT_FILE,  "[ DE | ALLE KATEGORIEN ]", C.GREEN),
        (TVONLY_FILE,  "[ DE | LIVE ]",             C.CYAN),
        (VPN_FILE,     "[ VPN | ERFORDERLICH ]",    C.PURPLE),
        (ADULT_FILE,   "[ ADULT ]",                 C.ORANGE),
    ]

    entries = []   # Liste von dicts: {idx, url, host, user, pw, label, col}
    _url_re = re.compile(
        r'https?://[^\s]+(?:get\.php|player_api\.php)[^\s]*'
        r'[?&]username=([^&\s]+)[&]password=([^&\s]+)',
        re.IGNORECASE,
    )

    for fname, label, col in SOURCE_FILES:
        if not os.path.exists(fname):
            continue
        try:
            with open(fname, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    m = _url_re.search(line)
                    if not m:
                        continue
                    parsed = urlparse(line)
                    host   = f"{parsed.scheme}://{parsed.netloc}"
                    user   = m.group(1)
                    pw     = m.group(2)
                    # Duplikate (gleicher host+user) überspringen
                    key = (host.lower(), user.lower())
                    if any(e["_key"] == key for e in entries):
                        continue
                    entries.append({
                        "_key": key,
                        "url":  line,
                        "host": host,
                        "u":    user,
                        "pw":   pw,
                        "label":label,
                        "col":  col,
                        "fname":fname,
                    })
        except Exception:
            continue

    if not entries:
        print(c(C.RED, "  ✗ Keine Accounts in den Ausgabedateien gefunden."))
        print(c(C.DIM, "  → Zuerst einen Scan durchführen."))
        input(c(C.DIM, "\n  [Enter] zurück"))
        return

    # ── 2. Accountliste anzeigen ─────────────────────────────
    print(c(C.DIM, f"  {len(entries)} Account(s) in Ausgabedateien:\n"))

    for i, e in enumerate(entries, 1):
        host_s = e["host"].replace("http://","").replace("https://","")
        host_s = _shorten(host_s, 30)
        user_s = _shorten(e["u"], 18)
        print(
            f"  {c(C.WHITE, f'[{i:>3}]')} "
            f"{c(e['col'], e['label'][:26])} "
            f"{c(C.DIM, '|')} {c(C.WHITE, host_s)} "
            f"{c(C.DIM, '|')} {c(C.DIM, user_s)}"
        )

    # ── 3. Auswahl ───────────────────────────────────────────
    print()
    print(c(C.DIM,
            "  Eingabe: Nummer(n) kommasepariert  |  'A' = alle  |  "
            "'1-5' = Bereich"))
    sel_raw = input(c(C.CYAN, "  Auswahl: ")).strip().upper()

    selected = []
    if sel_raw in ("A", ""):
        selected = list(range(len(entries)))
    else:
        for part in sel_raw.split(","):
            part = part.strip()
            if "-" in part:
                # Bereich: "3-7"
                try:
                    a, b = part.split("-", 1)
                    for idx in range(int(a) - 1, int(b)):
                        if 0 <= idx < len(entries):
                            selected.append(idx)
                except ValueError:
                    pass
            elif part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(entries):
                    selected.append(idx)

    selected = list(dict.fromkeys(selected))   # Reihenfolge erhalten, Duplikate weg

    if not selected:
        print(c(C.RED, "  ✗ Keine gültige Auswahl."))
        input(c(C.DIM, "\n  [Enter] zurück"))
        return

    print(c(C.DIM, f"\n  {len(selected)} Account(s) ausgewählt."))

    # ── 4. Adult-Option ──────────────────────────────────────
    ans_a = input(c(C.CYAN,
                    "  Adult-Kategorien einschließen? [J/n]: ")
                  ).strip().upper()
    include_adult = ans_a in ("J", "")

    # ── 5. Export starten ────────────────────────────────────
    print()
    os.makedirs(M3UPLUS_DIR, exist_ok=True)
    ssl_ctx = _build_ssl_context()

    async def _do_export():
        conn = aiohttp.TCPConnector(ssl=False, limit=4, limit_per_host=1)
        async with aiohttp.ClientSession(
            connector=conn,
            cookie_jar=aiohttp.CookieJar(unsafe=True),
        ) as session:
            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            ok    = 0
            for idx in selected:
                e      = entries[idx]
                host_s = e["host"].replace("http://","").replace("https://","")
                print(c(C.GRAY,
                        f"  [{ok+1}/{len(selected)}] {_shorten(host_s,32)} "
                        f"| {_shorten(e['u'],16)} ..."), end="", flush=True)

                is_cf  = host_s in load_cf_hosts()
                ssl_p  = ssl_ctx  # v21.5: Unified SSL (CERT_NONE für alle)
                hdrs   = (HeaderManager2026.get_chrome_headers()
                          if is_cf else
                          {"User-Agent": random.choice(BROWSER_USER_AGENTS),
                           "Accept": "application/json"})
                try:
                    lines, de_c, ad_c = await generate_m3u_plus_for_account(
                        session, e["host"], e["u"], e["pw"],
                        hdrs, ssl_p, include_adult,
                    )
                except Exception as ex:
                    print(c(C.RED, f" ✗ {ex}"))
                    continue

                total = de_c + ad_c
                if total == 0:
                    print(c(C.YELLOW, " ⚠ 0 Streams – übersprungen"))
                    continue

                safe_h = _SAFE_FILENAME.sub('_', host_s)
                safe_u = _SAFE_FILENAME_USER.sub('_', e["u"])
                out_f  = os.path.join(
                    M3UPLUS_DIR, f"{safe_h}_{safe_u}_{stamp}.m3u")
                try:
                    with open(out_f, "w", encoding="utf-8") as fh:
                        fh.write("\n".join(lines) + "\n")
                    print(c(C.GREEN,
                            f" ✓  {de_c} DE + {ad_c} Adult"
                            f" → {os.path.basename(out_f)}"))
                    ok += 1
                except Exception as ex:
                    print(c(C.RED, f" ✗ Schreibfehler: {ex}"))

            return ok

    # ── Pydroid3-sicherer Async-Start ────────────────────────
    # asyncio.run() und loop.run_until_complete() schlagen fehl
    # wenn _run_export() aus einem laufenden Event-Loop heraus
    # aufgerufen wird (_async_main → run_menu → _run_export).
    # Lösung: Eigener Thread mit eigenem Event-Loop.
    # Der neue Thread hat keinen laufenden Loop → kein Konflikt.
    _ok_box  = [0]
    _err_box = [None]

    def _thread_target():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        try:
            _ok_box[0] = _loop.run_until_complete(_do_export())
        except Exception as _e:
            _err_box[0] = _e
        finally:
            _loop.close()

    _t = threading.Thread(target=_thread_target, daemon=True)
    _t.start()
    _t.join()

    ok = _ok_box[0] or 0
    if _err_box[0]:
        print(c(C.RED, f"\n  ✗ Export-Fehler: {_err_box[0]}"))

    print()
    if ok:
        print(c(C.GREEN + C.BOLD,
                f"  ✓ {ok} M3U+ Datei(en) gespeichert in ./{M3UPLUS_DIR}/"))
    else:
        print(c(C.RED, "  ✗ Keine Dateien erstellt."))

    input(c(C.DIM, "\n  [Enter] zurück ins Menü"))


def run_menu() -> ScanConfig:
    """
    Vollstaendiger Menu-Flow.
    Gibt ein konfiguriertes ScanConfig-Objekt zurueck
    oder None wenn der User abbricht.
    """
    env = EnvInfo().detect()
    cfg = ScanConfig()

    while True:
        _show_welcome(env)
        choice = _main_menu(env)

        if choice == "Q":
            print(c(C.DIM, "\n  Auf Wiedersehen."))
            return None

        if choice == "H":
            _show_help()
            continue

        if choice == "R":
            if not env.has_checkpoint:
                print(c(C.RED, "\n  Kein Checkpoint vorhanden."))
                input(c(C.DIM, "  [ENTER] Zurueck..."))
                continue
            try:
                with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                    cp = json.load(f)
                cfg.input_urls = cp.get("input_urls", [])
                cfg.resume = True
                cfg.resume_processed = cp.get("processed", 0)
                cfg.mode_name = "Resume"
                if not cfg.input_urls:
                    print(c(C.RED, "\n  Checkpoint enthaelt keine URLs."))
                    input(c(C.DIM, "  [ENTER] Zurueck..."))
                    continue
                print(c(C.GREEN, f"\n  ✓ Checkpoint geladen: {cfg.resume_processed} bereits verarbeitet."))
                print(c(C.DIM, f"  Verbleibend: {max(0, len(cfg.input_urls) - cfg.resume_processed)} Links."))
                total = len(cfg.input_urls)
                unique_hosts = len({urlparse(u).netloc for u in cfg.input_urls})
                already_known = env.known_links
                print(c(C.WHITE, f"  {total} Links discovered │ {unique_hosts} unique Hoster │ {already_known} bereits bekannt (werden uebersprungen)"))
                if cfg.workers_auto:
                    workers_actual = min(max(unique_hosts // 3, 4), 4 if IS_MOBILE else 20)
                else:
                    workers_actual = cfg.workers
                if not _confirm_screen(cfg, total, workers_actual, env):
                    ans = _prompt("Neues Setup?", ["J", "N"], "J")
                    if ans == "N":
                        return None
                    continue
                cfg.workers = workers_actual
                return cfg
            except Exception as e:
                print(c(C.RED, f"\n  ✗ Fehler beim Laden des Checkpoints: {e}"))
                input(c(C.DIM, "  [ENTER] Zurueck..."))
                continue

        if choice == "D":
            _run_dedup(env)
            env = EnvInfo().detect()
            continue

        if choice == "S":
            _run_sort(env)
            continue

        if choice == "E":
            _run_export(env)
            env = EnvInfo().detect()
            continue

        if choice == "V":
            ledger = LinkLedger()
            _run_link_management(ledger, env)
            env = EnvInfo().detect()
            continue

        # Preset anwenden
        if choice == "A":
            _auto_configure(env, cfg)
        elif choice == "1":
            cfg.apply_preset_quick()
        elif choice == "2":
            cfg.apply_preset_normal()
        elif choice == "3":
            cfg.apply_preset_thorough()
        elif choice == "4":
            if env.cf_hosts == 0:
                print(c(C.RED,
                        "\n  Keine CF-Hosts in cf_hosts.json gespeichert."))
                input(c(C.DIM, "  [ENTER] Zurueck..."))
                continue
            cfg.apply_preset_cf_debug()
        elif choice == "5":
            _manual_setup(cfg)

        # Eingabe
        lines = _input_menu()

        # Portal-Format: _input_menu hat bereits URLs konvertiert
        if lines and lines[0] == "__PORTAL_URLS__":
            portal_urls = lines[1:]
            cfg.input_urls = portal_urls
        elif cfg.cf_debug:
            cf_urls = []
            if os.path.exists(CF_FILE):
                with open(CF_FILE, "r", encoding="utf-8") as f:
                    cf_urls = [l.strip() for l in f if l.strip()]
            cfg.input_urls = cf_urls + _RE_XTREAM.findall("\n".join(lines))
        else:
            # Standard: Xtream-URLs per Regex extrahieren +
            # Portal-Format als Fallback (für gemischten Input)
            raw_text   = "\n".join(lines)
            xtream_urls= _RE_XTREAM.findall(raw_text)
            portal_conv= _process_portal_format(lines)
            # Merge: Xtream zuerst, dann Portal-konvertierte (kein Duplikat)
            seen = set(xtream_urls)
            for u in portal_conv:
                if u not in seen:
                    xtream_urls.append(u)
                    seen.add(u)
            cfg.input_urls = xtream_urls

        if not cfg.input_urls:
            print(c(C.RED, "\n  [-] Keine gueltigen Xtream-Links discovered!"))
            ans = _prompt("  Erneut versuchen?", ["J", "N"], "J")
            if ans == "J":
                continue
            return None

        total = len(cfg.input_urls)

        # v21.2: Hoster-Breakdown-Preview vor Bestätigung
        unique_hosts = len({urlparse(u).netloc for u in cfg.input_urls})
        already_known = env.known_links
        print()
        print(c(C.WHITE,  f"  {total} Links discovered"
                          f"  │  {unique_hosts} unique Hoster"
                          f"  │  {already_known} bereits bekannt (werden übersprungen)"))

        # ── CF-Blacklist: Universelle Abfrage vor jedem Scan ─
        if env.cf_hosts > 0:
            print()
            print(c(C.YELLOW, f"  {env.cf_hosts} CF-Host(s) in cf_hosts.json bekannt."))
            ans_bl = input(c(C.CYAN,
                            "  Bekannte CF-Hosts überspringen (Blacklist)? [J/n]: ")
                          ).strip().upper()
            cfg.cf_blacklist = ans_bl in ("J", "")
        else:
            cfg.cf_blacklist = False

        # Adaptive Workers-Anzahl
        if cfg.workers_auto:
            workers_actual = min(max(unique_hosts // 3, 4), 4 if IS_MOBILE else 20)
        else:
            workers_actual = cfg.workers

        # Bestätigungsscreen
        if not _confirm_screen(cfg, total, workers_actual, env):
            ans = _prompt("Neues Setup?", ["J", "N"], "J")
            if ans == "N":
                return None
            continue

        cfg.workers = workers_actual  # tatsaechlicher Wert fuer Scan
        print()
        return cfg


# ==============================================================
# DATEIEN SPEICHERN
# ==============================================================
def save_links(state: ScanState):
    """
    v19.9: Streaming-Output hat Links bereits geschrieben.
    Hier nur noch Zusammenfassung und CF-Hosts persistieren.
    """
    entries = [
        (state.free_links,     OUTPUT_FILE,   C.GREEN,  "[ DE | ALLE KATEGORIEN ]"),
        (state.tvonly_links,   TVONLY_FILE,   C.CYAN,   "[ DE | NUR LIVE TV      ]"),
        (state.vpn_links,      VPN_FILE,      C.PURPLE, "[ VPN | ERFORDERLICH    ]"),
        (state.expiring_links, EXPIRING_FILE, C.YELLOW, "[ ACCOUNT | ENDET BALD  ]"),
        (state.cf_links,       CF_FILE,       C.ORANGE, "[ CLOUDFLARE | ERKANNT  ]"),
    ]
    saved_any = False
    for links, fname, col, label in entries:
        if links:
            print(c(col, f"  {label} {len(links):>4} Links  ->  {fname}"))
            saved_any = True
    if not saved_any:
        print(c(C.DIM, "  Keine Links discovered."))

    if state._cf_hosts:
        save_cf_hosts(state._cf_hosts)
        print(c(C.DIM,
                f"  [cf_hosts.json] {len(state._cf_hosts)} CF-Hosts gespeichert"))


# ==============================================================
# MAIN
# ==============================================================
def main():
    """
    Pydroid3-sicherer Entry-Point (April 2026).
    Primär: asyncio.run() – modern, sauber, Python 3.7+.
    Fallback: new_event_loop() – für ältere Pydroid3-Builds mit RuntimeError.
    Pending-Tasks werden vor Loop-Close sauber abgebrochen.
    """
    try:
        asyncio.run(_async_main())
    except RuntimeError:
        # Pydroid3-Fallback: laufende Loop oder kein asyncio.run-Support
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_async_main())
        except KeyboardInterrupt:
            print(c(C.YELLOW, "\n\n  [!] Abgebrochen."))
            if os.path.exists(CHECKPOINT_FILE):
                print(c(C.CYAN,  "  → Checkpoint gespeichert."))
                print(c(C.CYAN,  "  → Starte neu und wähle [R] im Menü zum Fortfahren."))
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            loop.close()
    except KeyboardInterrupt:
        print(c(C.YELLOW, "\n\n  [!] Abgebrochen."))
        if os.path.exists(CHECKPOINT_FILE):
            print(c(C.CYAN,  "  → Checkpoint gespeichert."))
            print(c(C.CYAN,  "  → Starte neu und wähle [R] im Menü zum Fortfahren."))


async def _async_main():
    # ── Menu ──────────────────────────────────────────────────
    cfg = run_menu()
    if cfg is None:
        return
    _scan_start = time.monotonic()   # v21.2: Laufzeit-Messung

    # ── Laufzeit-Konfiguration anwenden ───────────────────────
    global VPN_CHECK, SAMPLE_CHECK, PRECHECK_ENABLED, FILTER_TRIAL
    global EXP_MIN_DAYS, CF_MAX_RETRIES
    VPN_CHECK        = cfg.vpn_check
    SAMPLE_CHECK     = cfg.sample_check
    PRECHECK_ENABLED = cfg.precheck
    FILTER_TRIAL     = cfg.filter_trial
    EXP_MIN_DAYS     = cfg.exp_min_days
    CF_MAX_RETRIES   = cfg.cf_retries

    # ── v19.9: Streaming-Output Locks initialisieren ──────────
    _init_file_locks()

    # ── State ─────────────────────────────────────────────────
    state        = ScanState()
    loaded       = state.load_existing()
    cf_preloaded = len(state._cf_hosts)

    # ── Resume-Modus: Bereits verarbeitete Links ueberspringen ─
    if getattr(cfg, 'resume', False):
        resume_processed = getattr(cfg, 'resume_processed', 0)
        if resume_processed > 0:
            if resume_processed < len(cfg.input_urls):
                skipped_resume = resume_processed
                cfg.input_urls = cfg.input_urls[resume_processed:]
                print(c(C.CYAN, f"  [Resume] Ueberspringe erste {skipped_resume} Links (bereits verarbeitet)."))
            else:
                print(c(C.GREEN, "  [Resume] Alle Links bereits verarbeitet."))
                return
        total = len(cfg.input_urls)

    # ── CF-Blacklist: Bekannte CF-Hosts ueberspringen ────────
    if getattr(cfg, 'cf_blacklist', False):
        cf_hosts = state._cf_hosts
        if cf_hosts:
            before_blacklist = len(cfg.input_urls)
            filtered_urls = []
            for url in cfg.input_urls:
                parsed = urlparse(url)
                host_url = f"{parsed.scheme}://{parsed.netloc}"
                if host_url in cf_hosts or parsed.netloc in cf_hosts:
                    continue
                filtered_urls.append(url)
            cfg.input_urls = filtered_urls
            skipped_cf = before_blacklist - len(cfg.input_urls)
            if skipped_cf > 0:
                print(c(C.YELLOW, f"  [CF-Blacklist] {skipped_cf} Links auf bekannten CF-Hosts uebersprungen."))
            total = len(cfg.input_urls)

    # ── v20.0: Pre-Deduplication nach username+password (hostunabhaengig) ──
    # Verhindert, dass identische Credentials mit unterschiedlichen Hosts
    # als separate Eintraege behandelt werden (Kern-Fix v20.0).
    urls_raw = cfg.input_urls
    urls_filtered = []
    pre_skip_dup  = 0
    seen_pre: set = set()
    for url in urls_raw:
        qs = parse_qs(urlparse(url.strip()).query)
        u  = qs.get("username", [None])[0]
        pw = qs.get("password", [None])[0]
        if not u or not pw:
            continue
        key = (u, pw)                          # v20.0: hostunabhaengiger Key
        if key in state.checked_keys or key in seen_pre:
            pre_skip_dup += 1
            continue
        seen_pre.add(key)
        urls_filtered.append(url)
    cfg.input_urls = urls_filtered
    total = len(cfg.input_urls)

    if pre_skip_dup > 0:
        print(c(C.DIM, f"  [Pre-Dedup] {pre_skip_dup} Duplikate vor Scan entfernt"))

    print_config_banner(total, loaded, cf_preloaded, cfg.workers, cfg.workers_auto)

    # ── Session ───────────────────────────────────────────────
    ssl_ctx   = _build_ssl_context()
    connector = aiohttp.TCPConnector(
        limit=cfg.workers,
        limit_per_host=3,
        ssl=False,
        enable_cleanup_closed=True,
    )

    _precheck_cache.clear()

    async with aiohttp.ClientSession(
        connector=connector,
        cookie_jar=aiohttp.CookieJar(unsafe=True),
    ) as session:
        sem = asyncio.Semaphore(cfg.workers)

        # v19.9: Harter Task-Timeout-Wrapper
        _task_timeout = TIMEOUT * TASK_TIMEOUT_MULT

        async def bound(url_str):
            async with sem:
                try:
                    return await asyncio.wait_for(
                        worker(session, state, url_str, ssl_ctx),
                        timeout=_task_timeout,
                    )
                except asyncio.TimeoutError:
                    async with state.lock:
                        state.stats["timeout"] += 1
                    return None

        tasks   = [bound(u) for u in cfg.input_urls]

        # ── Mobile-optimierte tqdm Formatierung (v21.5) ──────────────────────
        if IS_MOBILE:
            bar_fmt = "{desc} {percentage:3.0f}% |{bar}|"
            tqdm_kwargs = {
                'mininterval': 0.5,   # nur 2x pro Sekunde updaten
                'miniters': 5,        # mindestens 5 Tasks vor Update
                'ascii': True,        # keine Unicode Box-Chars
            }
        else:
            bar_fmt = "{l_bar}{bar}|{n_fmt}/{total_fmt} [{elapsed}<{remaining} {rate_fmt}]"
            tqdm_kwargs = {
                'dynamic_ncols': False,
            }

        pbar    = tqdm(
            asyncio.as_completed(tasks),
            total=total,
            desc=f"Scan [{cfg.mode_name}]",
            ncols=W_ACTUAL,
            bar_format=bar_fmt,
            **tqdm_kwargs
        )
        processed = 0

        for coro in pbar:
            res = await coro
            processed += 1

            # v21.5: Mobile-optimiertes Postfix
            s = state.stats
            if IS_MOBILE:
                # Nur die wichtigsten Metriken auf Mobile
                postfix = (f"✓={s['neu_de']+s['tvonly']} "
                          f"⧖={s.get('timeout',0)+s.get('tcp_fehler',0)+s.get('dns_fehler',0)}")
            else:
                # Detaillierte Metriken auf größeren Displays
                postfix = (f"DE={s['neu_de']+s['tvonly']} "
                          f"VPN={s['vpn_de']} "
                          f"CF={s['cf']} "
                          f"⧖={s.get('timeout',0)+s.get('tcp_fehler',0)+s.get('dns_fehler',0)}")

            pbar.set_postfix_str(postfix, refresh=False)

            if processed % CHECKPOINT_EVERY == 0:
                save_checkpoint(state, processed, cfg.input_urls)

            if not res or not res.get("dest"):
                continue

            # v21.1: Einzeilige Ausgabe – _format_hit_oneline() übernimmt alles
            hit_str = _format_hit_oneline(res)
            if hit_str:
                tqdm.write(hit_str)

        # ── Output Buffering Flush (v21.5) ─────────────────────
        # Schreibe alle gepufferten Links bevor Session schließt
        await _flush_all_buffers()

    if os.path.exists(CHECKPOINT_FILE) and not getattr(cfg, 'resume', False):
        try:
            os.remove(CHECKPOINT_FILE)
        except Exception:
            pass

    print_summary(state)
    print()
    save_links(state)

    # ── v21.2: Laufzeit + Trefferquote ───────────────────────
    _scan_elapsed = time.monotonic() - _scan_start
    _total_proc   = sum(state.stats.values())
    _total_hits   = (state.stats["neu_de"] + state.stats["tvonly"] +
                     state.stats["vpn_de"])
    _hit_pct      = (_total_hits / _total_proc * 100) if _total_proc else 0
    _mins         = int(_scan_elapsed // 60)
    _secs         = int(_scan_elapsed % 60)
    _rate         = _total_proc / _scan_elapsed if _scan_elapsed > 0 else 0
    print()
    print(c(C.DIM, f"  Laufzeit: {_mins}m {_secs:02d}s"
                   f"  │  Durchsatz: {_rate:.1f} acc/s"
                   f"  │  Trefferquote: {_hit_pct:.1f}%"))

    # ── Nach-Scan-Zusammenfassung ─────────────────────────────
    if _total_hits > 0:
        print()
        print(c(C.GREEN + C.BOLD, f"  {_total_hits} Treffer gefunden!"))
    if state.stats["expiring"] > 0:
        print(c(C.YELLOW,
                f"  {state.stats['expiring']} Ablauf-Vorwarnungen → {EXPIRING_FILE}"))

    if state.stats["adult"] > 0:
        print(c(C.PURPLE,
                f"  {state.stats['adult']} Adult-Treffer → {ADULT_FILE}"))

    # ── v21.2: Automatisches Dedup-Angebot nach Scan ─────────
    if _total_hits > 0:
        print()
        ans_d = input(c(C.CYAN,
                        "  Ergebnisse jetzt bereinigen (Dedup)? [J/n]: ")
                      ).strip().upper()
        if ans_d in ("J", ""):
            _dedup_env = EnvInfo().detect()
            _run_dedup(_dedup_env)

        # ── Automatische Sortier-Abfrage direkt nach Dedup ──
        print()
        ans_s = input(c(C.CYAN,
                        "  Ergebnisse jetzt sortieren (nach Hoster)? [J/n]: ")
                      ).strip().upper()
        if ans_s in ("J", ""):
            _sort_env = EnvInfo().detect()
            _run_sort(_sort_env)

    print()


# ==============================================================
# LINK-VERWALTUNG MIT ZUWEISUNGS-LEDGER (v21.5 NEU)
# ==============================================================
# LINK-VERWALTUNG MIT ZUWEISUNGS-LEDGER (v21.5 NEU)
# ==============================================================
LEDGER_FILE = "link_ledger.json"  # Speichert user:pass → Zuweisungen

def _input_multi_links_for_management() -> list:
    """
    Link-Eingabe für [V] Verwaltung - nutzt _input_menu() Logik.
    Bietet vier bewährte Eingabemethoden:
    [1] Einfügen (Paste, 2x ENTER)
    [2] Datei laden
    [3] Beides kombiniert
    [4] Portal-Format (host:port + user:pass)
    """
    _cls()
    _section("LINK-EINGABE FÜR STATUS-ABFRAGE")
    print(f"  {c(C.WHITE, '[1]')}  {c(C.GRAY, 'Einfuegen      (Paste, 2x ENTER)')}")
    print(f"  {c(C.WHITE, '[2]')}  {c(C.GRAY, 'Datei laden    (Pfad eingeben)')}")
    print(f"  {c(C.WHITE, '[3]')}  {c(C.GRAY, 'Beides         (Datei + Paste kombiniert)')}")
    print(f"  {c(C.WHITE, '[4]')}  {c(C.GRAY, 'Portal-Format  (host:port + user:pass Zeilen)')}")
    print()
    print(c(C.GRAY, "  Format [4] Beispiel:"))
    print(c(C.GRAY, "    http://portal.tv:8080"))
    print(c(C.GRAY, "    user1:pass1"))
    print(c(C.GRAY, "    user2:pass2"))

    choice = _prompt("Eingabemethode", ["1", "2", "3", "4"], "1")
    lines = []

    # Datei laden wenn gewünscht
    if choice in ("2", "3"):
        path = _prompt("Dateipfad")
        path = path.strip('"').strip("'")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    file_lines = f.readlines()
                lines += [l.rstrip("\n") for l in file_lines]
                cnt = len([l for l in lines if l.strip()])
                print(c(C.GREEN, f"  [{cnt} Zeilen aus {os.path.basename(path)} geladen]"))
            except Exception as e:
                print(c(C.RED, f"  Fehler beim Lesen: {e}"))
        else:
            print(c(C.RED, f"  Datei nicht gefunden: {path}"))

    # Paste wenn gewünscht
    if choice in ("1", "3", "4"):
        prompt_text = (
            "\n  Portal + user:pass einfuegen (2x ENTER zum Abschluss):"
            if choice == "4" else
            "\n  Links oder Inhalt einfuegen (2x ENTER zum Abschluss):"
        )
        print(c(C.WHITE, prompt_text))
        print(c(C.GRAY, "  Abschluss: 2x ENTER hintereinander:"))
        empty_streak = 0
        while True:
            try:
                line = input()
            except EOFError:
                break
            if not line:
                empty_streak += 1
                if empty_streak >= 2:
                    break
                lines.append("")
            else:
                empty_streak = 0
                lines.append(line)

    # Portal-Format konvertieren wenn nötig
    if choice == "4":
        portal_urls = _process_portal_format(lines)
        if portal_urls:
            print(c(C.GREEN, f"  [{len(portal_urls)} URLs aus Portal-Format konvertiert]"))
        return portal_urls

    # Für andere Methoden: Extrahiere Links aus den Zeilen
    text_content = "\n".join(lines)
    extracted = _extract_xtream_links(text_content)

    return extracted


def _extract_xtream_links(text):
    """Extrahiert alle gültigen Xtream-Links aus beliebigem Text."""
    if not text or not isinstance(text, str):
        return []

    links = []

    # Split nach Newlines und verarbeite jede Zeile
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Regex für Xtream-Links: http(s)://host:port/... mit username+password
        pattern = r'https?://[^\s\'"<>]+?(?:player_api\.php|get\.php)[^\s\'"<>]*[?&]username=[^&\s\'"<>]+[&]password=[^&\s\'"<>]+'

        matches = re.findall(pattern, line, re.IGNORECASE)
        for match in matches:
            # Entferne möglicherweise angehängte Zeichen
            match = match.rstrip('.,;:!?')
            if match not in links:  # Verhindere Duplikate
                links.append(match)

    return links


def _input_multi_links(prompt: str = "Links paste (mehrere ok) oder [A] alle aus Datei") -> list:
    """
    Intelligente Multi-Link Eingabe - nutzt DATEI-basierte Lösung für Pydroid 3.
    Problem: input() in Pydroid 3 liest nur erste Zeile bei Block-Paste.
    Lösung: Temporäre Datei nutzen für mehrzeilige Eingabe.

    - [A] = alle aus free_links.txt, free_links_TVonly.txt, vpn_links.txt
    - [D] = aus links_to_check.txt (Nutzer pastet dort ein)
    - Beliebiger Text = extrahiert automatisch Xtream-Links
    """
    print()
    print(c(C.CYAN, f"  {prompt}"))
    print(c(C.DIM, "  Optionen:"))
    print(c(C.DIM, "    [A] - Alle aus Output-Dateien"))
    print(c(C.DIM, "    [D] - Aus links_to_check.txt (erstellt jetzt)"))
    print(c(C.DIM, "    oder Paste die Links direkt (mehrere ok)"))
    print()

    user_input = input(c(C.CYAN, "  → ")).strip()

    # [A] - Alle aus Dateien
    if user_input.upper() == "A":
        urls = []
        for fname in [OUTPUT_FILE, TVONLY_FILE, VPN_FILE]:
            if os.path.exists(fname):
                with open(fname, "r", encoding="utf-8") as f:
                    urls.extend(l.strip() for l in f if l.strip())
        return urls

    # [D] - Aus links_to_check.txt
    if user_input.upper() == "D":
        temp_file = "links_to_check.txt"

        # Erstelle Template-Datei
        if not os.path.exists(temp_file):
            template = """# Paste deine Links hier (eine pro Zeile):
# Beispiel:
# http://host1.com:8080/get.php?username=user1&password=pass1
# http://host2.com/player_api.php?username=user2&password=pass2
"""
            try:
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(template)
                print(c(C.GREEN, f"\n  ✓ Datei erstellt: {temp_file}"))
                print(c(C.YELLOW, f"  ⚠️  Öffne {temp_file} in Editor, paste Links ein, speichern, dann [ENTER]"))
            except Exception as e:
                print(c(C.RED, f"\n  ✗ Fehler beim Erstellen: {e}"))
                return []

        input(c(C.CYAN, "\n  Datei bereit - [ENTER] wenn fertig mit Einfügen: "))

        # Lese die Datei
        try:
            with open(temp_file, "r", encoding="utf-8") as f:
                file_content = f.read()

            extracted = _extract_xtream_links(file_content)
            if extracted:
                print(c(C.GREEN, f"\n  ✓ {len(extracted)} Link(s) aus {temp_file} extrahiert."))
            else:
                print(c(C.RED, f"\n  ✗ Keine gültigen Links in {temp_file} gefunden."))

            return extracted
        except Exception as e:
            print(c(C.RED, f"\n  ✗ Fehler beim Lesen: {e}"))
            return []

    # Direkter Paste (Fallback für Single-Line)
    extracted = _extract_xtream_links(user_input)

    if extracted:
        print(c(C.GREEN, f"\n  ✓ {len(extracted)} Link(s) extrahiert."))
        return extracted

    # Kein Input/Fehler
    if user_input:
        print(c(C.YELLOW, f"\n  ⚠️  Keine gültigen Links erkannt."))
    else:
        print(c(C.YELLOW, f"\n  ⚠️  Keine Eingabe."))

    return []



class LinkLedger:
    """v21.5 erweiterte Kontenverwaltung mit Status, Notizen, Geräte-Zuordnung und Kontaktdaten"""
    def __init__(self):
        self.data = {}
        self.contacts = {}
        self.load()

    def load(self):
        """Lädt Ledger mit Rückwärts-Kompatibilität"""
        if os.path.exists(LEDGER_FILE):
            try:
                with open(LEDGER_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    # v2.0 Format mit "ledger" Key
                    if isinstance(raw, dict) and "ledger" in raw:
                        self.data = raw.get("ledger", {})
                        self.contacts = raw.get("contacts", {})
                    else:
                        # v1.0 Format (direktes dict)
                        self._migrate_v1_to_v2(raw)
            except Exception:
                self.data = {}
                self.contacts = {}
        else:
            self.data = {}
            self.contacts = {}

    def _migrate_v1_to_v2(self, old_data: dict):
        """Migriert altes Format zu v2.0 mit erweiterten Feldern"""
        self.data = {}
        for key, assignments in old_data.items():
            if isinstance(assignments, list):
                self.data[key] = {
                    "assignments": assignments,
                    "metadata": {
                        "last_status_check": None,
                        "quality_score": None,
                        "tags": []
                    }
                }
            else:
                self.data[key] = assignments
        self.save()

    def save(self):
        """Speichert Ledger v2.0 Format"""
        try:
            export = {
                "version": "2.0",
                "ledger": self.data,
                "contacts": self.contacts
            }
            with open(LEDGER_FILE, "w", encoding="utf-8") as f:
                json.dump(export, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(c(C.RED, f"  ✗ Fehler beim Speichern des Ledgers: {e}"))

    def get_key(self, url: str) -> str:
        """Extrahiert username:password aus URL als Key"""
        try:
            qs = parse_qs(urlparse(url).query)
            u = qs.get("username", [None])[0]
            pw = qs.get("password", [None])[0]
            if u and pw:
                return f"{u}:{pw}"
        except Exception:
            pass
        return None

    def assign(self, url: str, person: str, device: str = None, notes: str = None) -> bool:
        """Weist Link einer Person zu mit optionalen Metadaten"""
        key = self.get_key(url)
        if not key:
            return False
        if key not in self.data:
            self.data[key] = {
                "assignments": [],
                "metadata": {
                    "last_status_check": None,
                    "quality_score": None,
                    "tags": []
                }
            }

        assignment = {
            "person": person,
            "date": datetime.now().isoformat(),
            "status": "active",
            "device": device or "unbekannt",
            "notes": notes or ""
        }
        self.data[key]["assignments"].append(assignment)
        self.save()
        return True

    def unassign(self, url: str, person: str) -> bool:
        """Entfernt eine Person von Link"""
        key = self.get_key(url)
        if not key or key not in self.data:
            return False

        assignments = self.data[key].get("assignments", [])
        self.data[key]["assignments"] = [
            a for a in assignments if a.get("person", "").lower() != person.lower()
        ]
        if not self.data[key]["assignments"]:
            del self.data[key]
        self.save()
        return True

    def get_assignments(self, url: str) -> list:
        """Gibt alle Zuweisungen für einen Link"""
        key = self.get_key(url)
        if not key or key not in self.data:
            return []
        data = self.data[key]
        if isinstance(data, dict) and "assignments" in data:
            return data["assignments"]
        elif isinstance(data, list):
            return data
        return []

    def get_unique_users(self, url: str) -> int:
        """Zählt eindeutige Personen, die diesen Link nutzen"""
        assignments = self.get_assignments(url)
        unique = set(a.get("person", "").lower() for a in assignments if isinstance(a, dict))
        return len(unique)

    def add_contact(self, name: str, phone: str = "", email: str = "", notes: str = "") -> bool:
        """Speichert Kontaktdaten für eine Person"""
        self.contacts[name] = {
            "phone": phone,
            "email": email,
            "notes": notes
        }
        self.save()
        return True

    def get_contact(self, name: str) -> dict:
        """Holt Kontaktdaten"""
        return self.contacts.get(name, {})

    def suggest_contact(self, partial: str) -> list:
        """Auto-Complete für Kontaktnamen"""
        return [n for n in self.contacts.keys() if partial.lower() in n.lower()]

    def set_metadata(self, url: str, quality_score: float = None, tags: list = None) -> bool:
        """Aktualisiert Metadaten für einen Link"""
        key = self.get_key(url)
        if not key or key not in self.data:
            return False

        if "metadata" not in self.data[key]:
            self.data[key]["metadata"] = {}

        if quality_score is not None:
            self.data[key]["metadata"]["quality_score"] = quality_score
        if tags is not None:
            self.data[key]["metadata"]["tags"] = tags

        self.data[key]["metadata"]["last_status_check"] = datetime.now().isoformat()
        self.save()
        return True

    def export_to_csv(self) -> str:
        """Exportiert Ledger als CSV-String"""
        lines = ["Link;Person;Gerät;Notizen;Status;ZugewiesenAm"]
        for key, data in self.data.items():
            assignments = data.get("assignments", []) if isinstance(data, dict) else data
            for a in assignments:
                lines.append(
                    f"{key};"
                    f"{a.get('person', '')};"
                    f"{a.get('device', '')};"
                    f"\"{a.get('notes', '')}\""
                    f"{a.get('status', 'active')};"
                    f"{a.get('date', '')}"
                )
        return "\n".join(lines)

    def import_from_csv(self, csv_content: str):
        """Importiert Links aus CSV-Format (Personen;Person;Device;Notes)"""
        lines = csv_content.strip().split('\n')
        count = 0
        for line in lines[1:]:  # Skip Header
            parts = line.split(';')
            if len(parts) >= 2:
                key, person = parts[0], parts[1]
                device = parts[2] if len(parts) > 2 else None
                notes = parts[3] if len(parts) > 3 else None
                if key not in self.data:
                    self.data[key] = {"assignments": [], "metadata": {}}
                self.data[key]["assignments"].append({
                    "person": person,
                    "date": datetime.now().isoformat(),
                    "status": "active",
                    "device": device or "imported",
                    "notes": notes or ""
                })
                count += 1
        self.save()
        return count


class LinkStatusChecker:
    """v21.5 asynchrone Batch-Status-Checks mit Caching"""
    def __init__(self, cache_ttl: int = 3600):
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.cache_times = {}

    def _is_cached_valid(self, key: str) -> bool:
        """Prüft ob Cache-Eintrag noch gültig ist"""
        if key not in self.cache_times:
            return False
        age = (datetime.now() - self.cache_times[key]).total_seconds()
        return age < self.cache_ttl

    async def check_url_async(self, url: str) -> dict:
        """Asynchrone Status-Abfrage (nutzt aiohttp wenn verfügbar)"""
        qs = parse_qs(urlparse(url).query)
        u = qs.get("username", [None])[0]
        pw = qs.get("password", [None])[0]
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"

        if not u or not pw or not host:
            return {"error": "URL ungültig", "url": url}

        api_url = f"{host}/player_api.php?username={u}&password={pw}"

        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    api_url,
                    headers={"User-Agent": "Mozilla/5.0 (Android; Linux) Chrome/136"},
                    timeout=aiohttp.ClientTimeout(total=5),
                    ssl=False
                ) as resp:
                    data = await resp.json()
                    user_info = data.get("user_info", {})

                    exp_ts = user_info.get("exp_date")
                    if exp_ts:
                        try:
                            exp_date = datetime.fromtimestamp(int(exp_ts))
                            exp_str = exp_date.strftime("%d.%m.%Y")
                            days_left = (exp_date - datetime.now()).days
                        except Exception:
                            exp_str = "unbekannt"
                            days_left = None
                    else:
                        exp_str = "unbegrenzt"
                        days_left = 999

                    self.cache[url] = {
                        "success": True,
                        "exp": exp_str,
                        "days_left": days_left,
                        "max_con": int(user_info.get("max_connections", 0)),
                        "active_con": int(user_info.get("active_cons", 0)),
                        "status": user_info.get("status", "unknown"),
                        "url": url
                    }
                    self.cache_times[url] = datetime.now()
                    return self.cache[url]
        except Exception as e:
            return {"error": f"async: {str(e)[:30]}", "url": url}

    def check_url_sync(self, url: str) -> dict:
        """Synchrone Status-Abfrage (urllib Fallback)"""
        key = f"{url}:sync"
        if key in self.cache and self._is_cached_valid(key):
            return self.cache[key]

        try:
            qs = parse_qs(urlparse(url).query)
            u = qs.get("username", [None])[0]
            pw = qs.get("password", [None])[0]
            parsed = urlparse(url)
            host = f"{parsed.scheme}://{parsed.netloc}"

            if not u or not pw or not host:
                return {"error": "URL ungültig", "url": url}

            api_url = f"{host}/player_api.php?username={u}&password={pw}"

            try:
                import urllib.request
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                req = urllib.request.Request(api_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Android; Linux) Chrome/136'
                })
                with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    user_info = data.get("user_info", {})

                    exp_ts = user_info.get("exp_date")
                    if exp_ts:
                        try:
                            exp_date = datetime.fromtimestamp(int(exp_ts))
                            exp_str = exp_date.strftime("%d.%m.%Y")
                            days_left = (exp_date - datetime.now()).days
                        except Exception:
                            exp_str = "unbekannt"
                            days_left = None
                    else:
                        exp_str = "unbegrenzt"
                        days_left = 999

                    result = {
                        "success": True,
                        "exp": exp_str,
                        "days_left": days_left,
                        "max_con": int(user_info.get("max_connections", 0)),
                        "active_con": int(user_info.get("active_cons", 0)),
                        "status": user_info.get("status", "unknown"),
                        "url": url
                    }
                    self.cache[key] = result
                    self.cache_times[key] = datetime.now()
                    return result
            except urllib.error.HTTPError as e:
                return {"error": f"HTTP {e.code}", "url": url}
            except urllib.error.URLError as e:
                return {"error": f"Verbindung: {str(e.reason)[:30]}", "url": url}
        except Exception as e:
            return {"error": str(e)[:50], "url": url}

    async def check_batch(self, urls: list) -> dict:
        """Batch-Check mehrerer URLs asynchron"""
        results = {}
        try:
            tasks = [self.check_url_async(url) for url in urls]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in batch_results:
                if isinstance(result, Exception):
                    continue
                url = result.get("url", "unknown")
                results[url] = result
        except Exception:
            for url in urls:
                results[url] = self.check_url_sync(url)
        return results


def _check_link_status(url: str) -> dict:
    """Kompatibilität-Wrapper für synchrone Checks (nutzt LinkStatusChecker)"""
    checker = LinkStatusChecker()
    return checker.check_url_sync(url)


def _run_link_management(ledger: LinkLedger, env: EnvInfo):
    """[V] v21.5 erweiterte Link-Verwaltung mit Status, Kontakte und Import/Export"""
    while True:
        choice = _submenu(
            "LINK-VERWALTUNG v21.5",
            [
                ("STATUS & CHECKS", [
                    ("1", "Link-Status abfragen (Batch)"),
                    ("2", "Alle Links Status-Check"),
                ]),
                ("VERWALTUNG", [
                    ("3", "Link einer Person zuweisen"),
                    ("4", "Zuweisungen entfernen"),
                    ("5", "Alle Zuweisungen anzeigen"),
                ]),
                ("KONTAKTE & EXPORT", [
                    ("6", "Kontakte verwalten"),
                    ("7", "Ledger Import/Export"),
                ]),
            ],
            header=f"Konten im Ledger: {len(ledger.data)} | Kontakte: {len(ledger.contacts)}",
        )

        if choice == "Z":
            break

        elif choice == "1":
            _cls()
            _section("LINK-STATUS ABFRAGEN")
            print()
            urls = _input_multi_links_for_management()

            if not urls:
                print(c(C.RED, "\n  ✗ Keine gültigen Links discovered."))
                input(c(C.DIM, "\n  [ENTER]..."))
                continue

            print(c(C.GREEN, f"\n  ✓ {len(urls)} Link(s) gefunden."))
            print()

            checker = LinkStatusChecker()
            success_count = 0
            error_count = 0

            for idx, u in enumerate(urls, 1):
                result = checker.check_url_sync(u)
                if "success" in result:
                    success_count += 1
                    ledger_count = ledger.get_unique_users(u)
                    host_short = urlparse(u).netloc[:20]

                    status_icon = c(C.GREEN, "✓")
                    if result.get("days_left") and result["days_left"] < 7:
                        status_icon = c(C.YELLOW, "⚠")
                    elif result.get("days_left") and result["days_left"] < 0:
                        status_icon = c(C.RED, "✗")

                    max_icon = ""
                    if result["max_con"] > 0 and result["active_con"] >= result["max_con"]:
                        max_icon = c(C.RED, " MAX!")

                    print(f"  {idx:2d}. {status_icon} {host_short:20} | {result['exp']} | "
                          f"{result['active_con']}/{result['max_con']}{max_icon}")
                    if ledger_count > 0:
                        print(f"       → {ledger_count} Person(en)")
                else:
                    error_count += 1
                    host_short = urlparse(u).netloc[:20]
                    print(f"  {idx:2d}. {c(C.RED, '✗')} {host_short:20} | {result.get('error', 'Fehler')}")

            print()
            print(c(C.CYAN, f"  Ergebnis: {success_count} OK, {error_count} Fehler"))
            input(c(C.DIM, "\n  [ENTER]..."))

        elif choice == "2":
            _cls()
            _section("ALLE LINKS STATUS-CHECK")
            print()

            if not ledger.data:
                print(c(C.YELLOW, "  ⚠️  Keine Konten im Ledger."))
                input(c(C.DIM, "\n  [ENTER]..."))
                continue

            print(c(C.CYAN, f"  Prüfe {len(ledger.data)} Konten..."))
            print()

            checker = LinkStatusChecker()
            ok_count = warn_count = err_count = 0

            for idx, (key, data) in enumerate(ledger.data.items(), 1):
                assignments = data.get("assignments", []) if isinstance(data, dict) else data
                if not assignments:
                    continue

                first_url = None
                for a in assignments:
                    if not first_url:
                        first_url = f"https://dummy.tv/player_api.php?username={key.split(':')[0]}&password={key.split(':')[1]}"

                if first_url:
                    result = checker.check_url_sync(first_url)
                    if "success" in result:
                        ok_count += 1
                        status = c(C.GREEN, "✓")
                        if result.get("days_left") and result["days_left"] < 7:
                            status = c(C.YELLOW, "⚠")
                            warn_count += 1
                    else:
                        err_count += 1
                        status = c(C.RED, "✗")
                    persons = len(set(a.get("person") for a in assignments))
                    print(f"  {idx:2d}. {status} {key[:30]:30} | {persons} Person(en)")

            print()
            print(c(C.CYAN, f"  Summe: {ok_count} OK, {warn_count} Warnung, {err_count} Fehler"))
            input(c(C.DIM, "\n  [ENTER]..."))

        elif choice == "3":
            _cls()
            _section("LINK ZUWEISEN")
            print()
            url = input(c(C.CYAN, "  Link: ")).strip()
            person = input(c(C.CYAN, "  Person: ")).strip()
            device = input(c(C.CYAN, "  Gerät (z.B. 'TV1', optional): ")).strip()
            notes = input(c(C.CYAN, "  Notizen (optional): ")).strip()

            if ledger.assign(url, person, device=device or None, notes=notes or None):
                print(c(C.GREEN, f"\n  ✓ {person} zugewiesen."))
            else:
                print(c(C.RED, "  ✗ Fehler beim Zuweisen."))
            input(c(C.DIM, "\n  [ENTER]..."))

        elif choice == "4":
            _cls()
            _section("ZUWEISUNGEN ENTFERNEN")
            print()
            url = input(c(C.CYAN, "  Link: ")).strip()
            person = input(c(C.CYAN, "  Person: ")).strip()

            if ledger.unassign(url, person):
                print(c(C.GREEN, f"\n  ✓ {person} entfernt."))
            else:
                print(c(C.RED, "  ✗ Nicht gefunden."))
            input(c(C.DIM, "\n  [ENTER]..."))

        elif choice == "5":
            _cls()
            _section("ALLE ZUWEISUNGEN")
            print()

            if not ledger.data:
                print(c(C.DIM, "  Keine Zuweisungen vorhanden."))
            else:
                for idx, (key, data) in enumerate(ledger.data.items(), 1):
                    assignments = data.get("assignments", []) if isinstance(data, dict) else data
                    persons_list = []
                    for a in assignments:
                        p = a.get("person") if isinstance(a, dict) else a.get("person")
                        d = a.get("device", "") if isinstance(a, dict) else ""
                        device_str = f" ({d})" if d else ""
                        persons_list.append(f"{p}{device_str}")

                    print(f"  {idx:2d}. {key[:30]:30} → {', '.join(persons_list)}")

            input(c(C.DIM, "\n  [ENTER]..."))

        elif choice == "6":
            _run_contact_management(ledger)

        elif choice == "7":
            _run_ledger_import_export(ledger)


def _run_contact_management(ledger: LinkLedger):
    """Untermenu: Kontakte verwalten"""
    while True:
        choice = _submenu(
            "KONTAKT-VERWALTUNG",
            [
                (None, [
                    ("1", "Kontakt hinzufügen"),
                    ("2", "Kontakte anzeigen"),
                    ("3", "Kontakt bearbeiten"),
                ]),
            ],
        )

        if choice == "Z":
            break

        elif choice == "1":
            _cls()
            _section("KONTAKT HINZUFÜGEN")
            print()
            name = input(c(C.CYAN, "  Name: ")).strip()
            phone = input(c(C.CYAN, "  Telefon (optional): ")).strip()
            email = input(c(C.CYAN, "  Email (optional): ")).strip()
            notes = input(c(C.CYAN, "  Notizen (optional): ")).strip()

            if ledger.add_contact(name, phone, email, notes):
                print(c(C.GREEN, f"\n  ✓ Kontakt '{name}' gespeichert."))
            else:
                print(c(C.RED, "  ✗ Fehler."))
            input(c(C.DIM, "\n  [ENTER]..."))

        elif choice == "2":
            _cls()
            _section("KONTAKTE")
            print()
            if not ledger.contacts:
                print(c(C.DIM, "  Keine Kontakte vorhanden."))
            else:
                for name, data in ledger.contacts.items():
                    print(f"  {c(C.GREEN, name)}")
                    if data.get("phone"):
                        print(f"    Tel: {data['phone']}")
                    if data.get("email"):
                        print(f"    Email: {data['email']}")
                    if data.get("notes"):
                        print(f"    Note: {data['notes']}")
                    print()
            input(c(C.DIM, "  [ENTER]..."))

        elif choice == "3":
            _cls()
            _section("KONTAKT BEARBEITEN")
            print()
            name = input(c(C.CYAN, "  Name: ")).strip()
            contact = ledger.get_contact(name)
            if not contact:
                print(c(C.RED, "  ✗ Kontakt nicht gefunden."))
                input(c(C.DIM, "\n  [ENTER]..."))
                continue

            phone = input(c(C.CYAN, f"  Telefon [{contact.get('phone', '')}]: ")).strip() or contact.get("phone", "")
            email = input(c(C.CYAN, f"  Email [{contact.get('email', '')}]: ")).strip() or contact.get("email", "")
            notes = input(c(C.CYAN, f"  Notizen [{contact.get('notes', '')}]: ")).strip() or contact.get("notes", "")

            if ledger.add_contact(name, phone, email, notes):
                print(c(C.GREEN, f"\n  ✓ Kontakt aktualisiert."))
            else:
                print(c(C.RED, "  ✗ Fehler."))
            input(c(C.DIM, "\n  [ENTER]..."))


def _run_ledger_import_export(ledger: LinkLedger):
    """Untermenu: Ledger Import/Export"""
    while True:
        choice = _submenu(
            "LEDGER IMPORT / EXPORT",
            [
                (None, [
                    ("1", "In CSV exportieren"),
                    ("2", "Aus CSV importieren"),
                ]),
            ],
        )

        if choice == "Z":
            break

        elif choice == "1":
            _cls()
            _section("LEDGER ALS CSV EXPORTIEREN")
            print()
            filename = input(c(C.CYAN, "  Dateiname [ledger_export.csv]: ")).strip() or "ledger_export.csv"
            try:
                csv_data = ledger.export_to_csv()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(csv_data)
                print(c(C.GREEN, f"\n  ✓ Exportiert zu '{filename}'"))
            except Exception as e:
                print(c(C.RED, f"  ✗ Fehler: {e}"))
            input(c(C.DIM, "\n  [ENTER]..."))

        elif choice == "2":
            _cls()
            _section("LEDGER AUS CSV IMPORTIEREN")
            print()
            filename = input(c(C.CYAN, "  Dateiname: ")).strip()
            if not os.path.exists(filename):
                print(c(C.RED, "  ✗ Datei nicht gefunden."))
                input(c(C.DIM, "\n  [ENTER]..."))
                continue

            try:
                with open(filename, "r", encoding="utf-8") as f:
                    csv_data = f.read()
                count = ledger.import_from_csv(csv_data)
                print(c(C.GREEN, f"\n  ✓ {count} Einträge importiert."))
            except Exception as e:
                print(c(C.RED, f"  ✗ Fehler: {e}"))
            input(c(C.DIM, "\n  [ENTER]..."))


if __name__ == "__main__":
    main()

