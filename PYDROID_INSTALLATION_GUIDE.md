# Pydroid 3 Installation & Setup Guide

**m3uScan v21.5 Kivy GUI auf Pydroid 3**

---

## 📋 Voraussetzungen

- **Pydroid 3** installiert von [iiec.github.io](https://iiec.github.io/)
- **Android 6.0+** (API 21+)
- **100 MB** freier Speicher
- **WiFi oder Mobile Internet** für Status-Checks

---

## 🚀 Installation (5 Schritte)

### Schritt 1: Pydroid 3 Terminal öffnen

Öffne die **Pydroid 3** App → **Terminal** (unten)

```bash
# Du solltest einen $ Prompt sehen
# Verfügbar:
python3 --version  # Python 3.x.x
pip --version      # pip x.x.x
```

### Schritt 2: Abhängigkeiten installieren

```bash
# Installiere erforderliche Module
pip install kivy aiohttp tqdm

# Optional (für bessere Diagnostik)
pip install psutil  # Memory-Info
pip install jnius   # Android Native Features (nur auf Pydroid)
```

Erwartete Ausgabe:
```
Successfully installed kivy-2.1.0 aiohttp-3.8.0 tqdm-4.64.0 ...
```

### Schritt 3: m3uScan Dateien herunterladen

```bash
# Stelle sicher dass m3uScan_v21_5.py und kivy_gui/ im gleichen Verzeichnis sind
# Typischerweise: /storage/emulated/0/Documents/m3uScan/

# Überprüfe ob Dateien vorhanden sind:
ls -la m3uScan_v21_5.py
ls -la kivy_gui/
```

Sollte zeigen:
```
-rw-r--r-- 1 user user  152341 Jun  6 12:00 m3uScan_v21_5.py
drwxr-xr-x 2 user user    4096 Jun  6 12:00 kivy_gui
```

### Schritt 4: GUI starten

```bash
# Starte die Kivy GUI
python3 kivy_launcher.py

# ODER spezifisch als Modul
python3 -m kivy_gui.main
```

Die GUI sollte sich innerhalb von **5-10 Sekunden** öffnen.

### Schritt 5: Konto hinzufügen (Optional Test)

In der GUI:
1. Klicke **[📋 Konten-Manager]**
2. Klicke **[➕ Add]**
3. Gib ein Testkonto ein:
   - **Host:Port:** `192.168.1.1:8080`
   - **Username:** `testuser`
   - **Password:** `testpass`
4. Klicke **[Add]**

---

## ⚙️ Optimization für Pydroid 3

Das System erkennt Pydroid 3 automatisch und passt sich an:

```python
# Automatische Anpassung:
- Workers: 1-2 (ARM ist langsam)
- Batch Size: 5-10 Konten pro Batch
- Network Timeout: 15 Sekunden (statt 10)
- UI Refresh: 30 FPS (statt 60)
- Animations: Deaktiviert bei Low-Memory
```

### Memory-Management

Bei **Low-Memory Devices** (<2GB RAM):
- Cache: 50 MB (statt 300 MB)
- Batch Size: 5 (statt 25)
- Animations: Deaktiviert
- Garbage Collection: Aggressiv

---

## 📱 Orts-Spezifische Pfade

Pydroid 3 nutzt folgende Verzeichnisse:

```
/storage/emulated/0/
├── Documents/
│   └── m3uScan/           # ← Hauptverzeichnis
│       ├── data/          # App-Daten
│       ├── .cache/        # Temp Cache
│       ├── .tmp/          # Temporär
│       ├── backups/       # Auto-Backups
│       ├── exports/       # Exports (CSV, JSON)
│       └── logs/          # Logs
```

---

## 🔌 Berechtigungen

Pydroid 3 fordert folgende Berechtigungen (automatisch):

```
✓ INTERNET                  # Status-Checks
✓ ACCESS_NETWORK_STATE      # Online/Offline-Erkennung
✓ READ_EXTERNAL_STORAGE     # Import Dateien
✓ WRITE_EXTERNAL_STORAGE    # Export & Backups
✓ VIBRATE                   # Haptisches Feedback
```

**Bestätige alle Berechtigungen wenn gefragt!**

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'kivy'"

```bash
# Lösung: Installiere Kivy
pip install kivy>=2.1

# Wenn das fehlschlägt:
pip install --upgrade pip setuptools
pip install kivy --prefer-binary
```

### Problem: "ModuleNotFoundError: No module named 'm3uScan_v21_5'"

```bash
# Lösung 1: Stelle sicher Dateien sind im gleichen Verzeichnis
ls -la m3uScan_v21_5.py
ls -la kivy_gui/

# Lösung 2: Nutze absolute Pfade
cd /storage/emulated/0/Documents/m3uScan/
python3 kivy_launcher.py
```

### Problem: GUI startet nicht / schwarzer Bildschirm

```bash
# Versuche mit Debug-Output
KIVY_LOG_MODE=hybrid python3 kivy_launcher.py 2>&1 | tee debug.log

# Überprüfe die Log-Datei
cat ~/.m3uscan/logs/*.log

# Bei Crash: Error-Report anschauen
cat ~/.m3uscan/logs/error_*.txt
```

### Problem: Status-Checks funktionieren nicht

```bash
# Überprüfe Netzwerk
ping 8.8.8.8

# Überprüfe Firewall (Port 8080 sollte offen sein)
# Erhöhe Timeout in Einstellungen → Network Timeout: 15s

# Prüfe ob Konto erreichbar
curl http://192.168.1.1:8080/  # Ersetze mit deinem Host:Port
```

### Problem: App ist langsam / friert ein

```bash
# Mögliche Lösungen:

# 1. Aktiviere Low-Memory Mode in Einstellungen
#    (wird automatisch bei <2GB RAM aktiviert)

# 2. Reduziere Batch Size:
#    Einstellungen → Performance → Batch Size: 5

# 3. Reduziere Anzahl der Konten
#    oder teile in mehrere Dateien auf

# 4. Starte Pydroid neu:
#    Ganz schließen (Kill) und neu öffnen
```

### Problem: Speicher voll

```bash
# Lösche alte Backups/Logs
# In der GUI: Einstellungen → Auto Cleanup aktivieren

# Oder manuell im Terminal:
rm -rf ~/.m3uscan/backups/*_old
rm ~/.m3uscan/logs/m3uscan_*.log
```

---

## 📊 Performance-Optimierungen

### Default (Automatisch erkannt)

```
Device Type: Normal (2-4GB RAM)
Workers: 2
Batch Size: 10
Cache: 100 MB
Timeout: 15 Sekunden (Pydroid-angepasst)
UI Refresh: 30 FPS
```

### Für Low-Memory (<2GB):

```
Workers: 1
Batch Size: 5
Cache: 50 MB
Animations: Aus
GC: Aggressiv
```

### Für High-Performance (>4GB):

```
Workers: 4
Batch Size: 25
Cache: 300 MB
Animations: An
Alle Features: Aktiviert
```

---

## 🔋 Batterie-Sparen

Tipps für längere Batterielebensdauer:

1. **Animations ausschalten:** Einstellungen → Animations: Aus
2. **Auto-Check deaktivieren:** Einstellungen → Auto-Check: Aus
3. **Backups reduzieren:** Einstellungen → Backup Retention: 3 Tage
4. **WiFi-only:** Mobile Data für Status-Checks deaktivieren
5. **Bildschirm dimmen:** Android Einstellungen → Brightness

---

## 📚 Weitere Ressourcen

| Datei | Inhalt |
|-------|--------|
| **KIVY_QUICK_START.md** | Schnell-Start für Kivy GUI |
| **KIVY_GUI_DOCUMENTATION.md** | Vollständige Kivy-Dokumentation |
| **PYDROID_OPTIMIZATION_GUIDE.md** | Detaillierte Tuning-Parameter |
| **PYDROID_TROUBLESHOOTING.md** | Erweiterte Fehlerbehandlung |
| **m3uScan_v21_5.py** | CLI-Version (Terminal only) |

---

## 💡 Pro-Tipps für Pydroid 3

### 1. Terminal vs. Editor

```
✓ NUTZE TERMINAL für bessere Performance
✗ MEIDE Editor (zu langsam)
```

### 2. Speicher-Verwaltung

```bash
# Überprüfe verfügbaren Speicher
df -h /storage/emulated/0/

# Falls knapp: Lösche alte Backups
ls -la ~/.m3uscan/backups/
rm ~/.m3uscan/backups/*_old
```

### 3. Netzwerk-Optimierung

```bash
# Bei langsamen Checksi:
# Erhöhe Timeout in Einstellungen
# oder nutze WiFi statt Mobile Data
```

### 4. Daten-Backup

```bash
# Sicherung auf externen Speicher
cp ~/.m3uscan/data/link_ledger.json \
   /storage/emulated/0/Download/link_ledger_backup.json

# Wiederherstellung
cp /storage/emulated/0/Download/link_ledger_backup.json \
   ~/.m3uscan/data/link_ledger.json
```

### 5. Multi-Device-Sync

```
Desktop (Kivy GUI)
    ↓ link_ledger.json
    ↓ (Dropbox/Google Drive Sync)
    ↓
Android (Pydroid 3 - Kivy GUI)
    ↓ Status-Check
```

---

## ✅ Checkliste

Vor der Verwendung:

- [ ] Pydroid 3 installiert
- [ ] Terminal öffnen können
- [ ] `pip install kivy aiohttp tqdm` erfolgreich
- [ ] `m3uScan_v21_5.py` im gleichen Verzeichnis
- [ ] `kivy_gui/` Verzeichnis vorhanden
- [ ] `python3 kivy_launcher.py` startet GUI ✅
- [ ] Konto hinzufügen funktioniert
- [ ] Status-Check funktioniert

---

## 🆘 Support

Falls etwas nicht funktioniert:

1. **Überprüfe die Log-Datei:**
   ```bash
   cat ~/.m3uscan/logs/m3uscan_*.log
   ```

2. **Erstelle einen Error-Report:**
   ```bash
   # Bei Crash wird automatisch error_TIMESTAMP.txt erstellt
   cat ~/.m3uscan/logs/error_*.txt
   ```

3. **Prüfe Requirements:**
   ```bash
   python3 -m kivy_gui.setup.first_run
   ```

---

**Status:** ✅ Production Ready  
**Version:** 21.5-kivy-pydroid  
**Letztes Update:** 2026-06-06  
**Autor:** TheGermanGuy™
