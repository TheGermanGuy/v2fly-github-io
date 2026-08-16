# m3uScan v21.5 - Installationsanleitung

## 📦 Download-Optionen

### Option 1: **Komplettes Paket** (empfohlen)
- **Datei:** `m3uScan_v21_5_COMPLETE.zip` (112 KB)
- **Inhalt:** Alles (Code + GUI + Docs)
- **Für:** Schnelle Einrichtung mit GUI

### Option 2: **Nur Hauptdatei**
- **Datei:** `m3uScan_v21_5.py`
- **Für:** CLI-only Betrieb (z.B. Pydroid 3)

### Option 3: **CLI + GUI Launcher**
- **Dateien:** `m3uScan_v21_5.py` + `gui_launcher.py`
- **Für:** CLI + optionale GUI auf Desktop

### Option 4: **GUI Modul separat**
- **Datei:** `gui_module_only.zip`
- **Für:** In bestehende Installation integrieren

---

## 🚀 Installation

### Desktop (Windows/macOS/Linux)

#### Variante A: Komplettes Paket
```bash
# 1. Entpacke m3uScan_v21_5_COMPLETE.zip
unzip m3uScan_v21_5_COMPLETE.zip

# 2. Starte GUI
python3 gui_launcher.py

# oder CLI
python3 m3uScan_v21_5.py
```

#### Variante B: Nur CLI
```bash
# 1. Datei: m3uScan_v21_5.py speichern
# 2. Abhängigkeiten installieren (falls nötig)
pip install aiohttp tqdm

# 3. Starten
python3 m3uScan_v21_5.py
```

#### Variante C: CLI + GUI
```bash
# 1. Beide Dateien speichern:
#    - m3uScan_v21_5.py
#    - gui_launcher.py
# 2. In gleicher Ordner

# 3. GUI starten
python3 gui_launcher.py

# oder CLI
python3 m3uScan_v21_5.py
```

---

### Pydroid 3 (Android)

⚠️ **GUI funktioniert nicht auf Pydroid 3 (kein Tkinter)**

```bash
# 1. m3uScan_v21_5.py in Pydroid speichern
# 2. Mit Pydroid ausführen

python3 m3uScan_v21_5.py

# Wähle dann:
# [A] Auto oder [1-5] Presets
# [V] Link-Verwaltung (neu!)
#   [1] Status-Check
#   [2] Alle Links prüfen
#   [3] Zuweisen
#   etc.
```

---

## 📋 Abhängigkeiten

### Erforderlich (immer)
```bash
pip install aiohttp tqdm
```

### Optional (nur für GUI)
```bash
pip install tkinter
# oder
apt-get install python3-tk          # Linux
brew install python-tk              # macOS
# Windows: bereits in Python enthalten
```

### Optional (für erweiterte Features)
```bash
pip install requests[socks]          # SOCKS5 Proxy
pip install pillow                   # Image Processing
```

---

## 🔍 Erste Schritte

### CLI-Betrieb

1. **Starten:**
   ```bash
   python3 m3uScan_v21_5.py
   ```

2. **Hauptmenü:**
   ```
   [S] Scan-Modi
   [T] Tools (Dedup, Sort, Export, Link-Management)
   [I] Info (Help, Resume, Quit)
   ```

3. **Link-Verwaltung [V]:**
   ```
   [1] Link-Status abfragen
   [2] Alle Links prüfen
   [3] Link zuweisen
   [4] Zuweisungen entfernen
   [5] Alle anzeigen
   [6] Kontakte verwalten
   [7] Ledger Im/Export
   ```

### GUI-Betrieb

1. **Starten:**
   ```bash
   python3 gui_launcher.py
   ```

2. **Fenster öffnet sich mit 3 Tabs:**
   - **Konten-Manager:** Hinzufügen, Bearbeiten, Löschen
   - **Status-Überwachung:** Live-Status mit Farben
   - **Import/Export:** CSV, Textdateien, Backups

3. **Menü-Leiste:**
   - Datei → Laden, Speichern, Beenden
   - Ansicht → Tab wechseln
   - Werkzeuge → Status prüfen, Bereinigen, Backup
   - Hilfe → Dokumentation

---

## 📁 Verzeichnisstruktur

### Nach Installation:
```
project-folder/
├── m3uScan_v21_5.py              # Hauptdatei (4800+ Zeilen)
├── gui_launcher.py                # GUI Starter
├── gui_module/                    # GUI Modul-Paket
│   ├── __init__.py
│   ├── main_window.py
│   ├── account_manager.py
│   ├── status_monitor.py
│   ├── import_export.py
│   └── styles.py
├── link_ledger.json               # Konto-Verwaltung (wird erstellt)
├── backups/                       # Auto-Backups (wird erstellt)
│   └── link_ledger_backup_*.json
├── free_links.txt                 # Scan-Ergebnisse
├── vpn_links.txt
├── adult_links.txt
└── ... (weitere Output-Dateien)
```

---

## ⚙️ Konfiguration

### Datei: m3uScan_v21_5.py

**Wichtige Parameter (Zeilen 147-225):**

```python
WORKERS = 8                    # Parallel-Worker (4 auf Mobile)
TIMEOUT = 10                   # Request-Timeout (Sekunden)
PRECHECK_TIMEOUT = 3.5         # TCP-Test vor API
CF_JITTER_BASE = 3.0           # CloudFlare Retry-Rate
TASK_TIMEOUT_MULT = 2.5        # Hard-Timeout Multiplikator
CHECKPOINT_EVERY = 50          # Speicher nach N Accounts
DEAD_LINK_WARN_PCT = 60        # Warnung bei % Fehlern
```

**Anpassen für dein System:**
- Desktop: `WORKERS=8-12` für mehr Speed
- Mobile (Pydroid3): `WORKERS=4` (auto-detected)
- Langsame Verbindung: `TIMEOUT=15` erhöhen
- CloudFlare-Probleme: `CF_JITTER_BASE=5.0` erhöhen

---

## 🐛 Häufige Probleme

### Problem 1: "ModuleNotFoundError: No module named 'aiohttp'"

**Lösung:**
```bash
pip install aiohttp
# oder
pip3 install aiohttp
```

### Problem 2: "No module named 'tkinter'" (GUI)

**Lösung:**
```bash
# Linux (Ubuntu/Debian)
sudo apt-get install python3-tk

# macOS
brew install python-tk

# Windows
# Bei Python-Installation "tcl/tk" ankreuzen oder:
# python -m pip install tk
```

### Problem 3: "link_ledger.json: Permission denied"

**Lösung:**
```bash
chmod 644 link_ledger.json
# oder Ordner wechseln:
cd ~/Downloads && python3 m3uScan_v21_5.py
```

### Problem 4: GUI startet nicht

**Lösung:**
```bash
# 1. Teste Python direkt
python3 -c "import tkinter; print('OK')"

# 2. Starten mit Debug
python3 gui_launcher.py

# 3. Fallback zu CLI
python3 m3uScan_v21_5.py
```

---

## 📊 Update-Weg (v21.4 → v21.5)

### Sicher:
```bash
# 1. Backup machen
cp link_ledger.json link_ledger.json.backup

# 2. Alte Datei speichern
mv m3uScan_v21_4.py m3uScan_v21_4.py.old

# 3. Neue Version einspielen
# Entpacke m3uScan_v21_5_COMPLETE.zip

# 4. GUI testen (optional)
python3 gui_launcher.py

# 5. CLI testen
python3 m3uScan_v21_5.py
```

**Daten-Migration:**
- ✅ Alte `link_ledger.json` (v1.0) wird auto-migriert zu v2.0
- ✅ Alle bisherigen Scan-Ergebnisse bleiben erhalten
- ✅ Keine Breaking Changes

---

## ✅ Verifikation

### Nach Installation prüfen:

```bash
# 1. Python-Version
python3 --version
# Sollte: 3.7+ sein

# 2. Abhängigkeiten
python3 -c "import aiohttp; print('aiohttp OK')"
python3 -c "import tqdm; print('tqdm OK')"

# 3. GUI (optional)
python3 -c "import tkinter; print('tkinter OK')"

# 4. Haupt-Datei Syntax
python3 -m py_compile m3uScan_v21_5.py
echo "Syntax OK"

# 5. GUI-Module Syntax
for f in gui_module/*.py; do python3 -m py_compile "$f"; done
echo "GUI Syntax OK"
```

---

## 📞 Support

### Dokumentation
- `GUI_FEATURES_v21_5.md` - Feature-Überblick
- `IMPLEMENTATION_SUMMARY.md` - Technische Details
- Header in `m3uScan_v21_5.py` - Scan-Engine Doku
- GUI Help-Dialog - Inline-Dokumentation

### Debug-Tipps
```bash
# Verbose Output
PYTHONUNBUFFERED=1 python3 m3uScan_v21_5.py

# GUI Debug
python3 gui_launcher.py 2>&1 | tee debug.log

# Import-Test
python3 -c "from m3uScan_v21_5 import LinkLedger, LinkStatusChecker; print('OK')"
```

---

## 🔄 Verwendungs-Szenarien

### Szenario 1: Nur CLI (Pydroid 3)
```
1. m3uScan_v21_5.py speichern
2. Aus Pydroid starten
3. [V] Link-Verwaltung nutzen
```

### Szenario 2: Desktop mit GUI
```
1. m3uScan_v21_5_COMPLETE.zip entpacken
2. python3 gui_launcher.py starten
3. Konten in GUI verwalten
4. Optional: CLI für Scans
```

### Szenario 3: Hybride Nutzung
```
1. Scan mit CLI: python3 m3uScan_v21_5.py [A]
2. Link-Verwaltung mit GUI: python3 gui_launcher.py
3. Status-Check mit CLI [V][1]
```

### Szenario 4: Automatisierung
```bash
#!/bin/bash
# Auto-Scan + Status-Report

python3 m3uScan_v21_5.py << EOF
A
1000
EOF

# Status-Check via Python-API
python3 - << 'PYTHON'
from m3uScan_v21_5 import LinkLedger, LinkStatusChecker

ledger = LinkLedger()
checker = LinkStatusChecker()

for key in list(ledger.data.keys())[:5]:
    status = checker.check_url_sync(f"https://dummy/{key}")
    print(f"{key}: {status}")
PYTHON
```

---

## 📝 Changelog v21.5

```
✅ Parameter-Optimierung (Timeouts, Thresholds)
✅ LinkLedger v2.0 mit Migration
✅ LinkStatusChecker mit async + Caching
✅ Erweiterte [V] CLI-Menü
✅ Vollständige Tkinter GUI
✅ CSV-Import/Export
✅ Kontakt-Management
✅ Backup/Restore-System
✅ Responsive Design
✅ Farbcodierung (grün/rot/orange)
```

---

## 🎓 Tips & Tricks

### CLI
```bash
# Schneller Modus
python3 m3uScan_v21_5.py
→ [1] Schnell

# Nur DE-Links
python3 m3uScan_v21_5.py
→ [2] Normal
→ Scan

# Link-Status prüfen
python3 m3uScan_v21_5.py
→ [V] Link-Management
→ [1] Status abfragen
```

### GUI
```bash
# Alle Konten exportieren
Datei → Speichern
Im/Export Tab → CSV Export → Alle

# Backup erstellen
Im/Export Tab → Backup → Backup erstellen

# Mass-Import
Im/Export Tab → Textdateien → Datei laden → Einlesen
```

---

**Version:** 21.5  
**Status:** ✅ Production Ready  
**Datum:** 2026-06-06  
**Support:** Siehe Dokumentation in Dateien
