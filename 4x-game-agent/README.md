# 4x-game-agent

Automatisierter Verteidigungsstrategie-Agent für **Evony: The King's Return**
(und generische 4X-Mobile-Strategiespiele).

Spielprofil: `config/game_profile.evony.json` (vier Truppentypen: ground, mounted,
ranged, siege). Generisches Profil: `config/game_profile.example.json`.

> **Wichtig:** Dieses Repository enthält **nur den Code**. ADB, Gemini und
> Telegram werden in deiner eigenen **Windows-VM mit Android-Emulator**
> ausgeführt — nicht in der Umgebung, in der der Code erstellt wurde. Verifiziert
> sind hier der Strategie-Rechner, die lokale Speicherung sowie die Parsing-/
> Formatierungslogik (siehe `tests/`).
>
> Die automatisierte Steuerung von (Multiplayer-)Spielen verstößt häufig gegen
> deren Nutzungsbedingungen. Einsatz auf eigene Verantwortung.

## Pipeline

```
Android-Emulator (Windows-VM)
   │  ADB MEHRSCHIRM-ERFASSUNG je relevantem Screen   (adb_controller.py)
   │  (monarch_profile, troops, buffs): navigate -> screencap
   ▼
Bildanalyse je Screen ─┬─ Gemini (REST, stdlib – Default)  (gemini_analyzer.py: GeminiRestAnalyzer)
                       ├─ Gemini (SDK)                     (gemini_analyzer.py: GeminiAnalyzer)
                       └─ Composio → Google Cloud Vision   (vision_cloud.py + composio_tool.py)
   ▼
Merge + Vollständigkeitsprüfung ALLER Stats            (aggregate.py)
   │  (bricht ab, falls relevante Felder fehlen)
   ▼
Lokale Speicherung (SQLite)                            (storage.py)
   ▼
Verteidigungsstrategie (deterministisch, exakt)       (strategy.py)
   ▼
Telegram-Ausgabe                                       (messenger.py)
```

Orchestriert von `pipeline.py` (`Agent.capture_all_stats` erfasst zuerst alle
relevanten Stats per ADB über mehrere Screens und prüft Vollständigkeit, bevor
gerechnet wird), CLI in `main.py`. Backend wählbar per `--backend gemini|cloud_vision`.
Welche Screens erfasst werden, steht im Profil unter `capture_screens`.
VM-Einrichtung: `windows-vm/SETUP.md` + `setup.ps1`.

## Architekturkorrekturen ggü. der Ursprungsvorgabe

| Ursprungsvorgabe | Ersetzt durch | Grund |
|---|---|---|
| OpenClaw (Automatisierung) | reines **ADB** | OpenClaw ist ein 2D-Jump'n'Run, kein Automatisierungs-Framework |
| Composio → Google Cloud Vision | als **wählbares Backend** integriert (`--backend cloud_vision`) neben Gemini | beide nutzbar; Gemini deckt OCR+Semantik in einem Schritt ab, Cloud Vision liefert reines OCR |
| Windows-VM **+** ADB | Windows-VM **hostet Android-Emulator**, ADB spricht mit Emulator (Provisionierung: `windows-vm/setup.ps1`) | ADB ist Android-Tooling |

## Der "mathematisch exakte" Strategie-Rechner

Effektive Verteidigung pro Einheit eines Typs *t*:

```
eff_def(t) = base_def(t) · (1 + Σ Buffs) · Σ_a  enemy_fraction(a) · counter(t, a)
```

Die optimale Zuteilung (Anzahl je Typ) unter den Schranken
`0 ≤ x_t ≤ available(t)` und `Σ x_t ≤ capacity` ist ein **kontinuierliches
Rucksackproblem**. Die Greedy-Zuteilung nach absteigendem `eff_def(t)` ist dafür
beweisbar optimal — `tests/test_strategy.py` prüft das gegen eine erschöpfende
Referenzsuche.

## Einrichtung (Windows-VM)

1. **Android-Emulator** installieren (z. B. BlueStacks/LDPlayer/Android-Studio-AVD),
   ADB-Debugging aktivieren.
2. **Android Platform-Tools** installieren, `adb` muss im PATH liegen.
   Verbindung prüfen: `adb devices`.
3. **Python 3.11+**, dann `pip install -r requirements.txt`.
4. `.env.example` → `.env` kopieren und Schlüssel eintragen (oder echte Umgebungsvariablen setzen).
5. `config/game_profile.example.json` zu deinem Spiel anpassen:
   - `troops`: Basis-Atk/Def/HP aus dem Spiel-Wiki,
   - `counter`: Truppen-Konter-Werte,
   - `menu_paths`: tatsächliche (x, y)-Tap-Koordinaten deiner Auflösung.

## Ausführen

```bash
python -m src.agent.main \
  --profile config/game_profile.json \
  --serial 127.0.0.1:5555 \
  --screen profile
```

Mit `--no-send` wird die Strategie nur in der Konsole ausgegeben (kein Telegram-Versand).

## Tests

```bash
pip install pytest
python -m pytest tests/ -q
```

## Live-Verifikation (Gemini)

Der Gemini-REST-Pfad wurde mit einem echten API-Schlüssel live verifiziert: aus
einem Evony-Stats-Screenshot extrahierte `gemini-2.5-flash` korrekt Power,
alle vier Truppentypen, Verstärkungskapazität und Buffs (Defense +45 % → 0.45,
Ground Defense +20 % → 0.2). Die komplette Kette Gemini → SQLite → Strategie →
Messenger-Text lief fehlerfrei durch.

> Der Default-Pfad benötigt **nur die Standardbibliothek** (REST). Hinter einem
> TLS-intercepting Proxy `SSL_CERT_FILE` auf das CA-Bündel setzen.
