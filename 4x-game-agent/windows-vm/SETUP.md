# Einrichtung in der isolierten Windows-VM (Evony)

Diese Anleitung bringt alle Komponenten **innerhalb der Windows-VM** zum Laufen.
Der Code selbst ist plattformneutral; ADB/Gemini/Cloud-Vision/Telegram werden
hier real ausgeführt.

## 1. VM bereitstellen
- Isolierte Windows-VM (Hyper-V / VirtualBox / VMware), nur für diesen Zweck.
- Kein Zugriff auf andere Netzwerke nötig außer ausgehendem HTTPS (Gemini/Vision/Telegram).

## 2. Android-Emulator
- Emulator installieren (BlueStacks, LDPlayer oder Android-Studio-AVD).
- **Evony: The King's Return** im Emulator installieren und einloggen.
- ADB-Debugging im Emulator aktivieren; ADB-Adresse notieren (z. B. `127.0.0.1:5555`).
- Feste Auflösung einstellen (z. B. 1280×720), damit die `menu_paths`-Koordinaten stabil sind.

## 3. Provisionierung
In einer **Administrator-PowerShell** im Projektordner:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows-vm\setup.ps1 -EmulatorAddress 127.0.0.1:5555
```

Das Skript installiert Python + Platform-Tools (ADB), die Abhängigkeiten, legt
`.env` an und prüft `adb devices`.

## 4. Konfiguration
- `.env` mit `GEMINI_API_KEY` (und/oder Google-Cloud-Credentials) sowie
  `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` befüllen.
- Für **Cloud Vision**: `GOOGLE_APPLICATION_CREDENTIALS` auf die Service-Account-JSON setzen.
- `config/game_profile.evony.json` kalibrieren:
  - **Truppen-Basiswerte** je nach deiner Truppenstufe (T1…T15+) aus dem Evony-Wiki/In-Game.
  - **menu_paths** durch echte Tap-Koordinaten deiner Emulator-Auflösung ersetzen.

## 5. Lauf
```powershell
# Gemini-Backend:
python -m src.agent.main --profile config\game_profile.evony.json --serial 127.0.0.1:5555 --screen keep

# Composio / Google Cloud Vision als Backend:
python -m src.agent.main --profile config\game_profile.evony.json --serial 127.0.0.1:5555 --backend cloud_vision
```

`--no-send` gibt die Strategie nur in der Konsole aus (kein Telegram-Versand).

## Komponentenzuordnung zur Vorgabe
| Vorgabe | Realisierung |
|---|---|
| Spielsteuerung/Screenshots via ADB | `adb_controller.py` (`exec-out screencap`, `input tap/swipe`) |
| Composio-Plugin → Google Cloud Vision | `vision_cloud.py` + `composio_tool.py` |
| Gemini-Analyse | `gemini_analyzer.py` |
| Lokale Stats-Speicherung | `storage.py` (SQLite in der VM) |
| Mathematisch exakte Verteidigungsstrategie | `strategy.py` (getestet) |
| Ausgabe über Messenger | `messenger.py` (Telegram) |

> Hinweis: „OpenClaw" aus der Originalvorgabe ist ein 2D-Jump'n'Run und kein
> Automatisierungs-Framework; die Spielsteuerung erfolgt daher korrekt über ADB.
