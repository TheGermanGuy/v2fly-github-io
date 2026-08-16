#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xtream DE Scanner — DESIGN-VORSCHAU / THEME PREVIEW
====================================================
Standalone (keine Abhaengigkeiten). Auf Pydroid 3 starten, um die
3 Theme-Vorschlaege live auf dem echten Display zu vergleichen.

    python3 theme_preview.py

Zeigt fuer jedes Theme: Titel-Box, Hauptmenue, Statuszeilen.
So kannst du Farbtiefe (Truecolor vs. 256) und Lesbarkeit auf
deinem Geraet pruefen, bevor wir es ins Hauptprogramm uebernehmen.
"""

import os
import sys
import shutil

# ──────────────────────────────────────────────────────────────
# FARB-ENGINE — Truecolor mit automatischem Fallback
# ──────────────────────────────────────────────────────────────
def _supports_truecolor() -> bool:
    """Heuristik: COLORTERM=truecolor/24bit ⇒ Truecolor erlaubt."""
    return os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit")

TRUECOLOR = _supports_truecolor()
RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"

def _hex(h: str):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def _fg(hexcode: str) -> str:
    """Vordergrundfarbe als ANSI — Truecolor oder 256-Fallback."""
    r, g, b = _hex(hexcode)
    if TRUECOLOR:
        return f"\033[38;2;{r};{g};{b}m"
    # 256-Color-Fallback (6x6x6 Wuerfel)
    idx = 16 + 36 * (r * 5 // 255) + 6 * (g * 5 // 255) + (b * 5 // 255)
    return f"\033[38;5;{idx}m"

def paint(hexcode: str, text: str, bold: bool = False) -> str:
    b = BOLD if bold else ""
    return f"{b}{_fg(hexcode)}{text}{RESET}"


# ──────────────────────────────────────────────────────────────
# SEMANTISCHE THEMES — Bedeutung statt roher Farbe
# Jede Rolle (PRIMARY, ACCENT, …) wird auf einen Hex-Wert gemappt.
# Im Hauptprogramm wuerde NUR diese Tabelle getauscht.
# ──────────────────────────────────────────────────────────────
THEMES = {
    # 1) NEON — futuristisch, hoher Kontrast, "Cyber"-Look
    "NEON": {
        "PRIMARY": "#22d3ee",  # Rahmen, Titel  (Neon-Cyan)
        "ACCENT":  "#e879f9",  # Tasten [X]      (Magenta)
        "SUCCESS": "#4ade80",  # DE-Treffer      (Spring-Green)
        "WARN":    "#fbbf24",  # Endet bald      (Amber)
        "DANGER":  "#fb7185",  # Fehler          (Rose)
        "INFO":    "#38bdf8",  # Hinweise        (Sky)
        "SPECIAL": "#c084fc",  # VPN/CF          (Violet)
        "MUTED":   "#64748b",  # Sekundaer       (Slate)
        "TEXT":    "#e5e7eb",  # Fliesstext      (Hellgrau)
    },
    # 2) AURORA — professionell-dezent, Indigo/Sky, ruhiger Look
    "AURORA": {
        "PRIMARY": "#818cf8",  # Indigo
        "ACCENT":  "#38bdf8",  # Sky
        "SUCCESS": "#34d399",  # Emerald
        "WARN":    "#fbbf24",  # Amber
        "DANGER":  "#f87171",  # Red
        "INFO":    "#60a5fa",  # Blue
        "SPECIAL": "#a78bfa",  # Violet
        "MUTED":   "#6b7280",  # Gray
        "TEXT":    "#e5e7eb",
    },
    # 3) MATRIX — monochrom-gruen, minimalistisch-futuristisch
    "MATRIX": {
        "PRIMARY": "#00ff9c",
        "ACCENT":  "#7CFC00",
        "SUCCESS": "#00ff9c",
        "WARN":    "#d7ff00",
        "DANGER":  "#ff5555",
        "INFO":    "#43d9ad",
        "SPECIAL": "#39e6a8",
        "MUTED":   "#2f7d5b",
        "TEXT":    "#c8facc",
    },
}

# ──────────────────────────────────────────────────────────────
# MODERNE RAHMEN-ZEICHEN (gerundete Unicode-Box)
# Fallback auf ASCII, falls Terminal kein UTF-8 kann.
# ──────────────────────────────────────────────────────────────
UTF8 = (sys.stdout.encoding or "").lower().startswith("utf")
if UTF8:
    BX = dict(tl="╭", tr="╮", bl="╰", br="╯", h="─", v="│",
              ml="├", mr="┤", dot="·", tick="●", warn="▲",
              err="✕", time="⧗", arrow="▸", bullet="◆")
else:
    BX = dict(tl="+", tr="+", bl="+", br="+", h="-", v="|",
              ml="+", mr="+", dot=".", tick="*", warn="!",
              err="x", time="~", arrow=">", bullet="*")


def _width() -> int:
    cols, _ = shutil.get_terminal_size(fallback=(64, 24))
    return max(40, min(cols, 64))


def _render_theme(name: str, T: dict):
    W = _width()
    iw = W - 2

    def frame_top():
        return paint(T["PRIMARY"], BX["tl"] + BX["h"] * iw + BX["tr"], bold=True)
    def frame_mid():
        return paint(T["PRIMARY"], BX["ml"] + BX["h"] * iw + BX["mr"], bold=True)
    def frame_bot():
        return paint(T["PRIMARY"], BX["bl"] + BX["h"] * iw + BX["br"], bold=True)
    def vbar():
        return paint(T["PRIMARY"], BX["v"], bold=True)

    def boxrow(plain_left: str, painted: str):
        """Zeile in der Box, rechtsbuendig aufgefuellt."""
        pad = iw - len(plain_left)
        return f"{vbar()}{painted}{' ' * max(pad, 0)}{vbar()}"

    print()
    print(paint(T["MUTED"], f"  ┄┄ THEME: {name} ┄┄"))
    print()

    # ── Titel-Box ─────────────────────────────────────────────
    print(frame_top())
    title = "  XTREAM · DE SCANNER"
    print(boxrow(title, paint(T["PRIMARY"], title, bold=True)))
    sub = "  v30.1 · Pydroid Edition · 2026"
    print(boxrow(sub, paint(T["MUTED"], sub)))
    print(frame_mid())

    # ── Datei-Aufschluesselung ────────────────────────────────
    files = [
        ("SUCCESS", "Alle Kategorien", "2 299"),
        ("INFO",    "Nur Live-TV",     "879"),
        ("SPECIAL", "VPN benötigt",    "12"),
        ("WARN",    "Läuft bald ab",   "25"),
        ("SPECIAL", "Cloudflare",      "135"),
    ]
    for role, label, val in files:
        left = f"  {BX['tick']}  {label:<18}{val:>8}"
        painted = (f"  {paint(T[role], BX['tick'])}  "
                   f"{paint(T['TEXT'], f'{label:<18}')}"
                   f"{paint(T[role], f'{val:>8}')}")
        print(boxrow(left, painted))
    print(frame_bot())

    # ── Menue ─────────────────────────────────────────────────
    print()
    print(paint(T["PRIMARY"], f"  {BX['arrow']} SCAN-MODUS WÄHLEN", bold=True))
    print(paint(T["MUTED"], "  " + BX["h"] * (W - 4)))

    def menurow(key, label, desc, role="TEXT"):
        k = paint(T["ACCENT"], f"[{key}]", bold=True)
        n = paint(T[role], f"{label:<10}")
        d = paint(T["MUTED"], desc)
        return f"  {k}  {n} {d}"

    print(menurow("A", "Auto", "Adaptiv · empfohlen", "SUCCESS"))
    print(menurow("1", "Schnell", "API + DE + Adult"))
    print(menurow("2", "Normal", "+ VPN-Prüfung"))
    print(menurow("3", "Genau", "+ Stream-Stichprobe"))
    print(menurow("5", "Manuell", "Frei konfigurierbar", "MUTED"))
    print(paint(T["MUTED"], "  " + BX["h"] * (W - 4)))

    # Werkzeug-Zeile
    tools = "  ".join(
        paint(T["ACCENT"], f"[{k}]") + " " + paint(T["TEXT"], v)
        for k, v in [("D", "Bereinigen"), ("S", "Sortieren"),
                     ("E", "Exportieren"), ("V", "Verwaltung")]
    )
    print(f"  {tools}")
    print()

    # ── Statuszeilen (Treffer-Ausgabe) ────────────────────────
    print(paint(T["PRIMARY"], f"  {BX['arrow']} LIVE-TREFFER", bold=True))
    print(paint(T["MUTED"], "  " + BX["h"] * (W - 4)))
    print(f"  {paint(T['SUCCESS'], BX['tick'])} "
          f"{paint(T['TEXT'], 'cobra01.online:80')}  "
          f"{paint(T['MUTED'], '105 T')}  {paint(T['SUCCESS'], '[ DE · LIVE ]')}")
    print(f"  {paint(T['WARN'], BX['warn'])} "
          f"{paint(T['TEXT'], 'ctriple16.top:80')}  "
          f"{paint(T['WARN'], '6 T')}    {paint(T['WARN'], '[ ENDET BALD ]')}")
    print(f"  {paint(T['SPECIAL'], BX['bullet'])} "
          f"{paint(T['TEXT'], 'uaetv.org:80')}      "
          f"{paint(T['MUTED'], ' -- ')}   {paint(T['SPECIAL'], '[ CLOUDFLARE ]')}")
    print(f"  {paint(T['DANGER'], BX['err'])} "
          f"{paint(T['TEXT'], 'deadhost.tv:8080')}  "
          f"{paint(T['MUTED'], ' -- ')}   {paint(T['DANGER'], '[ FEHLER 401 ]')}")
    print()


def main():
    print("\033[2J\033[H", end="")
    print(paint("#e5e7eb", "  XTREAM SCANNER — DESIGN-VORSCHAU", bold=True))
    print(paint("#64748b",
                f"  Truecolor: {'JA' if TRUECOLOR else 'NEIN (256-Fallback)'}"
                f"  ·  UTF-8: {'JA' if UTF8 else 'NEIN (ASCII-Fallback)'}"
                f"  ·  Breite: {_width()}"))
    print(paint("#64748b",
                "  Tipp: COLORTERM=truecolor setzen fuer volle Farbtiefe."))

    for name, T in THEMES.items():
        _render_theme(name, T)
        try:
            input(paint("#64748b", "  [ENTER] naechstes Theme …"))
        except (EOFError, KeyboardInterrupt):
            break

    print(paint("#34d399", "\n  Fertig. Welches Theme gefaellt dir? (NEON / AURORA / MATRIX)\n"))


if __name__ == "__main__":
    main()
