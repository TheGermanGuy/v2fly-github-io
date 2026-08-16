# m3uScan v21.5 - Kivy GUI Documentation

**Cross-platform GUI für Android (QPython 3) + Desktop**

## 🎯 Überblick

Die Kivy-basierte GUI von m3uScan v21.5 läuft auf:
- ✅ **Android** (QPython 3, Pydroid 3, Buildozer)
- ✅ **Desktop** (Windows, macOS, Linux)
- ✅ **iOS** (theoretisch möglich)

## 📦 Installation

### Desktop (Windows/macOS/Linux)

```bash
# 1. Abhängigkeiten
pip install kivy aiohttp tqdm

# 2. Starten
python kivy_launcher.py
```

### Android (QPython 3)

```bash
# 1. In QPython Editor öffnen:
kivy_launcher.py

# 2. Run Button drücken (▶️)
# oder
python kivy_launcher.py
```

### Android (Buildozer - APK erstellen)

```bash
# 1. Install Buildozer
pip install buildozer cython

# 2. Build APK
buildozer android debug

# 3. Install auf Device
adb install -r bin/m3uscan-21.5-debug.apk
```

## 🎮 GUI Screens

### 1. **Main Screen** - Startbildschirm
```
╔══════════════════════════════════╗
║   m3uScan v21.5                  ║
║   v21.5-kivy                     ║
║                                  ║
║  [📋 Konten-Manager]             ║
║  [📊 Status-Überwachung]         ║
║  [⚙️ Einstellungen]               ║
║                                  ║
║  🟢 Online - Netzwerk verfügbar  ║
╚══════════════════════════════════╝
```

**Funktionen:**
- Navigation zu anderen Screens
- Offline-Status Indikator
- App-Info + Version

### 2. **Konten-Manager Screen**
```
╔══════════════════════════════════╗
║ [➕ Add] [🔄 Refresh] [← Back]   ║
║ ┌──────────────────────────────┐ ║
║ │ user1 | 2 Zuweisungen        │ ║
║ │ user2 | 1 Zuweisungen        │ ║
║ │ user3 | 3 Zuweisungen        │ ║
║ │ user4 | 1 Zuweisungen        │ ║
║ └──────────────────────────────┘ ║
╚══════════════════════════════════╝
```

**Funktionen:**
- [➕ Add] - Neues Konto hinzufügen
- [🔄 Refresh] - Liste aktualisieren
- Accounts auflisten mit Zuordnungszahl
- Tap auf Account zeigt Details
- Swipe zum Löschen (geplant)

**Add Account Dialog:**
```
Host:Port: [________________]
Username:  [________________]
Password:  [________________]
Person:    [________________]

[Cancel] [Add]
```

### 3. **Status-Überwachung Screen**
```
╔══════════════════════════════════╗
║ [✓ Check All] [← Back]           ║
║ Progress: ████████░░ 75%        ║
║ ┌──────────────────────────────┐ ║
║ │ 🟢 user1 | 31.12.2026        │ ║
║ │ 🔴 user2 | ERROR             │ ║
║ │ 🟡 user3 | ABGELAUFEN        │ ║
║ │ 🟢 user4 | 45 Tage           │ ║
║ └──────────────────────────────┘ ║
╚══════════════════════════════════╝
```

**Funktionen:**
- [✓ Check All] - Starte Batch-Status-Check
- Progress Bar zeigt Fortschritt
- Status-Icons: 🟢 OK, 🔴 Error, 🟡 Warning
- Ablaufdatum anzeigen
- Live-Updates während Check

### 4. **Einstellungen Screen**
```
╔══════════════════════════════════╗
║ 🌙 Dark Mode        [Toggle]     ║
║                                  ║
║ ℹ️ About                          ║
║ ─────────────────────────────── ║
║ m3uScan v21.5                    ║
║ v21.5-kivy                       ║
║                                  ║
║ © TheGermanGuy™                  ║
║ Android + Desktop GUI            ║
║                                  ║
║ [← Back]                         ║
╚══════════════════════════════════╝
```

**Funktionen:**
- 🌙 Dark Mode Toggle (default: aktiv)
- App-Info + Version
- About Dialog

## 🏗️ Architektur

```
kivy_gui/
├── __init__.py
├── main.py                      # Main App + Screens
├── utils/
│   ├── __init__.py
│   ├── constants.py            # Farben, Pfade, etc.
│   ├── platform_detect.py      # Android/Desktop Detection
│   ├── theme.py                # Dark Mode + Farben
│   └── responsive.py           # Touch-optimierte Layout
├── services/
│   ├── __init__.py
│   ├── link_ledger_adapter.py  # Wrapper um m3uScan
│   └── offline_manager.py      # Netzwerk-Status
└── screens/
    ├── __init__.py
    ├── main_screen.py          # Startbildschirm
    ├── accounts_screen.py      # (integriert in main.py)
    ├── status_screen.py        # (integriert in main.py)
    └── settings_screen.py      # (integriert in main.py)
```

## 🔌 API Integration

### LinkLedgerAdapter

```python
from kivy_gui.services import LinkLedgerAdapter

adapter = LinkLedgerAdapter()

# Get Accounts
accounts = adapter.get_all_accounts()

# Add Assignment
adapter.add_assignment("user:pass", "Person", device="TV1", notes="")

# Check Status (Sync)
status = adapter.check_account_sync("user:pass")

# Check Status (Async)
result = await adapter.check_account_async("user:pass")

# Batch Check with Progress
results = await adapter.check_all_async(on_progress=lambda c, t: print(f"{c}/{t}"))
```

### Platform Detection

```python
from kivy_gui.utils import platform

print(platform.get_platform())      # "android" oder "linux"
print(platform.is_mobile())         # True/False
print(platform.is_qpython())        # True/False
print(platform.get_system_info())   # Dict mit Details
```

### Theme Management

```python
from kivy_gui.utils import theme

theme.set_dark_mode(True)
color = theme.get_color('primary')  # '#1976D2'
rgb = theme.get_primary_color()     # (0.1, 0.46, 0.82, 1.0)
```

### Responsive Layout

```python
from kivy_gui.utils import responsive

responsive.button_height()          # dp(48)
responsive.is_tablet()              # True/False
responsive.get_screen_category()    # "small", "normal", "large", "xlarge"
responsive.padding()                # dp(16)
```

## 🎨 Theme & Colors

### Dark Mode (default)
```
Primary:       #1976D2 (Blau)
Accent:        #FF5722 (Orange)
Background:    #121212 (Sehr dunkel)
Surface:       #1E1E1E (Dunkel)
Text:          #FFFFFF (Weiß)
Success:       #4CAF50 (Grün)
Error:         #CF6679 (Rot)
Warning:       #FF9800 (Orange)
```

### Status Colors
```
🟢 OK/Active:       #4CAF50 (Grün)
🔴 Error/Expired:   #CF6679 (Rot)
🟡 Warning (3-7d):  #FF9800 (Orange)
⏳ Pending:         #29B6F6 (Blau)
⛔ Offline:         #CF6679 (Rot)
```

## ⚡ Performance Optimierungen

1. **RecycleView statt ListView**
   - Effizient für große Listen
   - Nur sichtbare Items werden rendered

2. **Async/Await für Netzwerk**
   - Status-Checks blocken nicht die UI
   - Progress Callbacks für Live-Updates

3. **Offline-Mode**
   - Cache für Daten lokal
   - Funktioniert auch ohne Netzwerk
   - Auto-Sync wenn online

4. **Touch-Optimierung**
   - Minimum 48dp Button-Größe
   - Responsive Layout für Phone/Tablet
   - Bottom Navigation (Android-Standard)

## 📱 Android-spezifische Features

### Permissions (buildozer.spec)
- `INTERNET` - Status-Checks
- `READ_EXTERNAL_STORAGE` - Import/Export
- `WRITE_EXTERNAL_STORAGE` - Backups
- `ACCESS_NETWORK_STATE` - Offline-Detection

### Orientation
- Portrait (Standard)
- Responsive für Landscape (automatisch)

### Daten-Speicherung
- `/data/data/org.thegeorguy.m3uscan/` - App-spezifische Daten
- `~/.m3uscan/` - Fallback für Desktop

## 🐛 Debugging

### Desktop Logging
```bash
PYTHONUNBUFFERED=1 python kivy_launcher.py 2>&1 | tee debug.log
```

### Android Logging
```bash
adb logcat | grep m3uscan
```

### Platform Info
```python
from kivy_gui.utils import platform
print(platform.get_system_info())
```

## 📋 Checkliste für QPython 3

- ✓ Kivy installieren
- ✓ aiohttp installieren
- ✓ tqdm installieren
- ✓ m3uScan_v21_5.py im gleichen Verzeichnis
- ✓ kivy_gui/ Verzeichnis vollständig
- ✓ kivy_launcher.py ausführen

## 🚀 Schnell-Start (3 Minuten)

```bash
# 1. Abhängigkeiten
pip install kivy aiohttp

# 2. Starten
python kivy_launcher.py

# 3. GUI öffnet sich -> Konten hinzufügen -> Status prüfen
```

## ⚠️ Bekannte Einschränkungen

1. **Kivy auf Android**
   - Muss über QPython 3 oder Buildozer installiert sein
   - Nicht im Standard-Android enthalten

2. **File Dialogs**
   - Begrenzte Unterstützung auf Android
   - Fallback zu Text-Input

3. **Native Integration**
   - Notifications über eigenes Toast-System
   - Share-Button erfordert zusätzliche Integration

## 📈 Zukünftige Verbesserungen

- [ ] Swipe-Gesten (Delete, Navigation)
- [ ] Lokale Benachrichtigungen
- [ ] Erweiterte Import/Export UI
- [ ] Grafische Status-Charts
- [ ] Multi-Language Support
- [ ] Backup in Cloud
- [ ] QR-Code-Scanner Integration

## 📞 Troubleshooting

### "No module named 'kivy'"
```bash
pip install kivy
```

### "No module named 'm3uScan_v21_5'"
```
- Stelle sicher: m3uScan_v21_5.py im gleichen Verzeichnis
- oder: pip install -e .
```

### GUI startet nicht auf Android
```
- Nutze QPython Editor mit ▶️ Button
- oder: python -m kivy_gui.main
- oder: buildozer android debug
```

### Status-Checks funktionieren nicht
```
- Prüfe Netzwerk: 🟢 Online Indicator
- Prüfe Firewall: Port 8080+ erlaubt?
- Prüfe Timeout: Erhöhe NETWORK_TIMEOUT in constants.py
```

## 📝 Lizenz & Credits

**m3uScan v21.5 - Kivy Edition**
- Author: TheGermanGuy™
- Version: 21.5-kivy
- Status: Production Ready ✅

---

**Weitere Dokumentation:**
- START_HERE.md - Einstieg
- QUICK_REFERENCE.txt - Übersicht
- GUI_FEATURES_v21_5.md - Tkinter-Version (veraltet)
