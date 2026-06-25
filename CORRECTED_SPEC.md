# Korrigierte Spezifikation – 4x-game-agent

> Status: UMGESETZT (lokal, nicht committet). Ersetzt die ursprüngliche
> Zielbeschreibung, deren benannte Komponenten teils widersprüchlich/falsch waren.
> Code liegt unter `4x-game-agent/`. Verifizierbare Teile sind getestet (10/10 grün).

## 1. Aufgelöste Widersprüche der Original-Spec

| Original | Problem | Korrektur |
|---|---|---|
| OpenClaw als Automatisierungs-Framework | OpenClaw ist ein 2D-Jump'n'Run (Captain-Claw-Remake), kein Framework | **Reines ADB** (screencap + input tap/swipe) |
| Composio → Google Cloud Vision **und** Gemini | Doppelte Bildanalyse | **Beide als wählbares Backend** umgesetzt: Gemini (Default) + Composio/Cloud-Vision (`--backend cloud_vision`) |
| "Windows-VM" + ADB | ADB ist Android-Tooling | Windows-VM hostet einen **Android-Emulator**; ADB spricht mit dem Emulator |

## 2. Festgelegte Entscheidungen

- **Spiel:** Evony: The King's Return (Profil `config/game_profile.evony.json`, Typen ground/mounted/ranged/siege)
- **Steuerung/Capture:** reines ADB
- **Bildanalyse:** Gemini (Screenshot → strukturiertes JSON via Schema/Function-Calling)
- **Stats-Speicherung:** lokal (SQLite oder JSON)
- **Strategie-Rechner:** deterministisch, unit-getestet ("mathematisch exakt")
- **Ausgabe:** Telegram-Bot-API

## 3. Datenfluss

```
Android-Emulator (in Windows-VM)
   │  ADB: exec-out screencap -p  /  input tap|swipe
   ▼
capture/control layer (Python)
   │  PNG-Bytes
   ▼
Gemini-Analyse  ──►  strukturiertes Stats-JSON (festes Schema)
   │
   ▼
lokale Persistenz (SQLite/JSON)
   │
   ▼
Strategie-Rechner (reine Funktion, getestet)  ◄── erkannte Buffs
   │
   ▼
Telegram-Ausgabe an den Nutzer
```

## 4. Realitäts-/Umgebungshinweise

- Code wird hier (Linux-Container) geschrieben; ADB/Gemini/Telegram werden **nicht** hier
  ausgeführt, sondern vom Nutzer in eigener Windows-VM + Emulator. Nur der
  Strategie-Rechner ist hier mit Tests verifizierbar.
- Automatisierte Steuerung von (Multiplayer-)Spielen verstößt i. d. R. gegen deren AGB.
  Einsatz auf eigene Verantwortung.

## 5. Umsetzungsstand

Gebaut unter `4x-game-agent/`:
- `adb_controller.py` – Screenshot + Tap/Swipe + Menüführung (reines ADB)
- `gemini_analyzer.py` – Screenshot → Stats-JSON (Gemini, truppentyp-konfigurierbar)
- `vision_cloud.py` + `composio_tool.py` – Google-Cloud-Vision-OCR als Composio-Tool
- `storage.py` – lokale SQLite-Persistenz
- `strategy.py` – deterministischer, exakter Verteidigungsrechner
- `messenger.py` – Telegram-Ausgabe (stdlib urllib)
- `pipeline.py` / `main.py` – Orchestrierung + CLI (`--backend gemini|cloud_vision`)
- `config/game_profile.evony.json` – Evony-Profil (4 Truppentypen, Konter, OCR-Labels)
- `windows-vm/setup.ps1` + `SETUP.md` – VM-Provisionierung (Python, ADB, Deps)
- `tests/` – 15 Tests grün, inkl. Brute-Force-Optimalitätsbeweis des Rechners

Hier verifiziert: Strategie-Rechner, Speicherung, Gemini-/OCR-Parsing, Formatierung,
Evony-Profil-Laden, End-to-End-Verdrahtung (15/15 Tests).
**LIVE verifiziert** mit echtem API-Key: Gemini-REST-Pfad (`gemini-2.5-flash`)
extrahierte aus einem Evony-Screenshot korrekt Stats + Buffs; Kette
Gemini → SQLite → Strategie → Messenger-Text lief fehlerfrei durch.
Der Default-Gemini-Pfad braucht nur die Standardbibliothek (REST).
Nicht hier ausführbar (Hardware/Windows nötig): ADB-Gerät, Telegram-Versand,
Windows-VM-Lauf — laufen auf Nutzerseite in der VM. (Telegram braucht nur Bot-Token.)

## 6. Offen (nur Feinjustierung in der VM, blockiert den Code nicht)

- [ ] **Evony-Zahlen kalibrieren**: Truppen-Basiswerte je Truppenstufe (T1…T15+)
      und Konter-Werte gegen aktuelle In-Game-/Wiki-Daten in
      `config/game_profile.evony.json` verifizieren (aktuelle Werte sind
      repräsentative, klar markierte Platzhalter).
- [ ] **menu_paths** auf die Emulator-Auflösung kalibrieren (echte Tap-Koordinaten).
- [ ] API-Schlüssel/Credentials in der VM setzen (`.env`, `GOOGLE_APPLICATION_CREDENTIALS`).
```
