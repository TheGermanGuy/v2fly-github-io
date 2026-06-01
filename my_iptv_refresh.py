#!/usr/bin/env python3
"""
my_iptv_refresh.py  –  Persönlicher Playlist-Auffrischer
=========================================================
Zweck: EIN eigenes, legal bezahltes Xtream-/M3U-Abo pflegen, wenn der
Anbieter gelegentlich die Domain wechselt.

Es werden NUR die eigenen Zugangsdaten gegen eine kurze Liste von
Domains geprüft, die der Anbieter offiziell bekanntgegeben hat
(Kundenportal, App, E-Mail). Kein Scannen fremder Listen, keine
Umgehung von Schutzmechanismen.

Nur Standardbibliothek -> läuft direkt in Pydroid 3 (Python 3.7+).

Konfiguration:
  1) USERNAME / PASSWORD unten eintragen (deine eigenen).
  2) candidates.txt anlegen: eine Anbieter-Basis-URL pro Zeile, z.B.
        http://mein-anbieter.example:8080
        http://backup.mein-anbieter.example:8080
     (Diese URLs gibt dir dein Anbieter.)
  3) Ausführen. Bei der ersten erreichbaren, gültigen URL wird deine
     persönliche M3U+ Playlist gespeichert und die funktionierende
     Basis-URL in last_working.txt gemerkt.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

# ── DEINE EIGENEN ZUGANGSDATEN ────────────────────────────────
USERNAME = "DEIN_BENUTZERNAME"
PASSWORD = "DEIN_PASSWORT"

# ── DATEIEN ───────────────────────────────────────────────────
CANDIDATES_FILE  = "candidates.txt"     # vom Anbieter genannte Basis-URLs
LAST_WORKING     = "last_working.txt"   # zuletzt funktionierende Basis-URL
OUTPUT_M3U       = "meine_playlist.m3u" # Ergebnis: deine Playlist
PREFERRED_TYPE   = "m3u_plus"           # m3u_plus liefert group-title/logos

TIMEOUT          = 12                   # Sekunden pro Anfrage
USER_AGENT       = "VLC/3.0.20 LibVLC/3.0.20"   # gängiger Player-UA


def load_candidates() -> list:
    """Liest Basis-URLs aus CANDIDATES_FILE; zuletzt funktionierende zuerst."""
    urls = []
    try:
        with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                u = line.strip().rstrip("/")
                if u and not u.startswith("#"):
                    urls.append(u)
    except FileNotFoundError:
        print(f"[!] {CANDIDATES_FILE} fehlt. Lege die Datei an und trage die")
        print("    vom Anbieter genannten Basis-URLs ein (eine pro Zeile).")
        sys.exit(1)

    # Zuletzt funktionierende URL nach vorne sortieren -> schneller Treffer
    try:
        with open(LAST_WORKING, "r", encoding="utf-8") as f:
            last = f.read().strip().rstrip("/")
        if last in urls:
            urls.remove(last)
            urls.insert(0, last)
    except FileNotFoundError:
        pass

    # Reihenfolge erhalten, Duplikate entfernen
    return list(dict.fromkeys(urls))


def _get(url: str, want_json: bool) -> tuple:
    """Einfache GET-Anfrage. Rückgabe (ok, payload). payload=dict|str|None."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if resp.status != 200:
                return False, None
            raw = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError,
            TimeoutError, OSError) as e:
        print(f"      Netzwerkfehler: {e}")
        return False, None

    if want_json:
        try:
            return True, json.loads(raw)
        except json.JSONDecodeError:
            return False, None
    return True, raw


def check_account(base_url: str) -> dict:
    """Prüft, ob die eigenen Zugangsdaten auf base_url aktiv sind."""
    api = (f"{base_url}/player_api.php?"
           + urllib.parse.urlencode({"username": USERNAME,
                                     "password": PASSWORD}))
    ok, data = _get(api, want_json=True)
    if not ok or not isinstance(data, dict):
        return {}
    info = data.get("user_info", {})
    if str(info.get("auth", "")) != "1":
        return {}
    if info.get("status") not in ("Active", "1"):
        return {}
    return info


def fmt_expiry(info: dict) -> str:
    """Macht das Ablaufdatum lesbar."""
    exp = info.get("exp_date")
    if not exp:
        return "unbegrenzt"
    try:
        return time.strftime("%d.%m.%Y", time.localtime(int(exp)))
    except (ValueError, OSError):
        return "unbekannt"


def download_playlist(base_url: str) -> bool:
    """Lädt die persönliche M3U+ Playlist und speichert sie."""
    m3u = (f"{base_url}/get.php?"
           + urllib.parse.urlencode({"username": USERNAME,
                                     "password": PASSWORD,
                                     "type":     PREFERRED_TYPE}))
    ok, body = _get(m3u, want_json=False)
    if not ok or not body or "#EXTM3U" not in body:
        print("[!] Playlist konnte nicht geladen werden.")
        return False
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.write(body)
    channels = body.count("#EXTINF")
    print(f"[+] Playlist gespeichert: {OUTPUT_M3U}  ({channels} Einträge)")
    return True


def main():
    if USERNAME.startswith("DEIN_") or PASSWORD.startswith("DEIN_"):
        print("[!] Bitte zuerst USERNAME und PASSWORD im Script eintragen.")
        sys.exit(1)

    candidates = load_candidates()
    print(f"[*] Prüfe {len(candidates)} Anbieter-URL(s) für deinen Account ...\n")

    for base in candidates:
        print(f"  -> {base}")
        info = check_account(base)
        if not info:
            print("     nicht erreichbar / nicht aktiv\n")
            continue

        print(f"     OK | aktiv bis {fmt_expiry(info)} | "
              f"Verbindungen {info.get('active_cons', '?')}/"
              f"{info.get('max_connections', '?')}")

        if download_playlist(base):
            with open(LAST_WORKING, "w", encoding="utf-8") as f:
                f.write(base + "\n")
            print(f"\n[+] Aktive Basis-URL gemerkt in {LAST_WORKING}")
            return

    print("\n[!] Keine der angegebenen URLs hat funktioniert.")
    print("    Frage deinen Anbieter nach der aktuellen Domain und trage")
    print(f"    sie in {CANDIDATES_FILE} ein.")


if __name__ == "__main__":
    main()
