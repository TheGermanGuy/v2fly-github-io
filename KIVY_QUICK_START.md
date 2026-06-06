# 🚀 m3uScan v21.5 Kivy GUI - Quick Start

**Grafische Oberfläche für Android (QPython 3) + Desktop (Windows/macOS/Linux)**

---

## ✨ Neue Features

Die **Kivy-basierte GUI** ist die Antwort auf deine Anforderung für eine Android-kompatible Oberfläche!

### 🎯 Was ist neu?

| Feature | Tkinter GUI | Kivy GUI |
|---------|------------|----------|
| **Android Support** | ❌ Nein | ✅ Ja! |
| **Desktop** | ✅ Ja | ✅ Ja |
| **QPython 3** | ❌ Nein | ✅ Ja! |
| **Touch-optimiert** | ❌ Nein | ✅ Ja! |
| **Offline-Mode** | ❌ Nein | ✅ Ja! |
| **Dark Mode** | ⚠️ Optional | ✅ Standard |
| **Responsive Layout** | ❌ Fix | ✅ Adaptiv |
| **Async Status-Checks** | ❌ Blockierend | ✅ Non-blocking |

---

## 📥 Installation (3 Minuten)

### Desktop (macOS/Linux/Windows)

```bash
# 1. Entpacke Kivy GUI
unzip m3uScan_v21_5_KIVY_GUI.zip

# 2. Stellen Sie sicher m3uScan_v21_5.py im gleichen Verzeichnis ist

# 3. Abhängigkeiten
pip install kivy aiohttp tqdm

# 4. Starten
python kivy_launcher.py
```

### Android (QPython 3)

```bash
# 1. QPython Editor öffnen

# 2. Kopiere kivy_launcher.py Content oder importiere Datei

# 3. Run Button (▶️) drücken
```

### Android (Pydroid 3)

```bash
# 1. Terminal öffnen

# 2. pip install kivy aiohttp tqdm

# 3. python kivy_launcher.py
```

### Android (Buildozer - APK erstellen)

```bash
# 1. Install Buildozer
pip install buildozer cython

# 2. Build APK
buildozer android debug

# 3. Install
adb install -r bin/m3uscan-21.5-debug.apk
```

---

## 🎮 Verwendung

### Startbildschirm
```
┌──────────────────────────────┐
│ m3uScan v21.5                │
│ v21.5-kivy                   │
│                              │
│ [📋 Konten-Manager]          │
│ [📊 Status-Überwachung]      │
│ [⚙️ Einstellungen]            │
└──────────────────────────────┘
```

### Konten-Manager
- [➕ Add] - Neues Konto hinzufügen
- [🔄 Refresh] - Liste aktualisieren
- Tap auf Konto - Details anzeigen
- Host:Port + User:Pass eingeben

### Status-Monitor
- [✓ Check All] - Starte Batch-Check
- Progress Bar zeigt Fortschritt
- Status-Icons: 🟢 OK, 🔴 Error, 🟡 Warning
- Live-Updates während Check

### Einstellungen
- 🌙 Dark Mode Toggle
- App-Info + Version
- About Dialog

---

## 🏗️ Architektur

```
kivy_gui/
├── utils/               # Platform, Theme, Responsive
├── services/            # LinkLedger Adapter, Offline
├── main.py             # Main App (300 Zeilen)
└── screens/            # (Integriert in main.py)

kivy_launcher.py        # Entry Point
buildozer.spec          # Android Build Config
```

**Größe:** 
- ZIP: 19 KB
- Unkomprimiert: ~60 KB
- Python-Dateien: 6 Modules, ~1800 Zeilen

---

## 🔌 Anforderungen

### Allgemein
- Python 3.7+
- m3uScan_v21_5.py (im gleichen Verzeichnis)

### Abhängigkeiten
```bash
pip install kivy aiohttp tqdm
```

### Für Android APK (optional)
```bash
pip install buildozer cython
```

---

## ⚡ Key Features

### 🤖 Plattform-Spezifisch
- ✅ Android erkennt automatisch (Pydroid, QPython, Buildozer)
- ✅ Desktop erkennt automatisch (Windows, macOS, Linux)
- ✅ Responsive Layout basierend auf Bildschirmegrößße
- ✅ Touch-optimierte Button-Größen (min 48dp)

### 🌐 Netzwerk
- ✅ Async Status-Checks (non-blocking UI)
- ✅ Batch-Checks mit Progress Bar
- ✅ Offline-Mode mit lokalem Cache
- ✅ Automatische Netzwerk-Erkennung

### 🎨 Design
- ✅ Dark Mode Standard (schont Augen auf Handy)
- ✅ Material Design inspiriert
- ✅ Status-Farben: 🟢 OK, 🔴 Error, 🟡 Warning
- ✅ Responsive für Phone/Tablet/Desktop

### 💾 Daten
- ✅ Nutzt bestehende link_ledger.json
- ✅ Kompatibel mit CLI-Version
- ✅ Import/Export (CSV, JSON)
- ✅ Lokale Backups

---

## 📱 Android vs Desktop

| Aspekt | Android | Desktop |
|--------|---------|---------|
| **Installation** | QPython Editor | `pip install kivy` |
| **Start** | ▶️ Button | `python kivy_launcher.py` |
| **Dateien** | `~/.m3uscan/` | `~/.m3uscan/` |
| **Netzwerk** | Wifi/Mobile | Wifi/Ethernet |
| **Offline-Mode** | ✅ Ja | ✅ Ja |
| **File Dialogs** | Begrenzt | ✅ Vollständig |

---

## 🎯 Workflows

### Workflow 1: Desktop + Android Sync

```
Desktop (Kivy GUI)
    ↓ Link hinzufügen
    ↓ link_ledger.json
    ↓ (Cloud Sync / USB)
    ↓
Android (Kivy GUI)
    ↓ Status-Check
    ↓ link_ledger.json aktualisiert
```

### Workflow 2: CLI + GUI hybrid

```
CLI (m3uScan_v21_5.py)
    ↓ [V] Link-Management
    ↓ [3] Zuweisen
    ↓ link_ledger.json

GUI (kivy_launcher.py)
    ↓ Konten-Manager
    ↓ Konto-Details anzeigen
    ↓ Status-Check
```

---

## 🔧 Konfiguration

### Dark Mode Toggle
```
Einstellungen Screen → [🌙 Dark Mode] → [Toggle]
```

### Netzwerk-Timeout
```python
# In: kivy_gui/utils/constants.py
NETWORK_TIMEOUT = 5  # Sekunden
```

### Cache-Einstellungen
```python
# In: kivy_gui/utils/constants.py
CACHE_TTL = 3600  # 1 Stunde
```

---

## 🐛 Troubleshooting

### Problem: "No module named 'kivy'"
```bash
pip install kivy>=2.1
```

### Problem: "No module named 'm3uScan_v21_5'"
```
✓ Stellen Sie sicher: m3uScan_v21_5.py im gleichen Verzeichnis
oder: PYTHONPATH=$PWD python kivy_launcher.py
```

### Problem: GUI startet nicht auf Android
```
✓ QPython Editor mit ▶️ Button öffnen
✓ Oder: python -m kivy_gui.main
✓ Oder: buildozer android debug + adb install
```

### Problem: Status-Checks funktionieren nicht
```
✓ Prüfe Netzwerk-Status (🟢 Online Indicator)
✓ Prüfe Firewall (Port 8080 erlaubt?)
✓ Prüfe Timeout (erhöhe in constants.py)
```

---

## 📚 Dokumentation

| Datei | Inhalt |
|-------|--------|
| **KIVY_GUI_DOCUMENTATION.md** | Komplette Doku |
| **KIVY_QUICK_START.md** | Diese Datei |
| **kivy_launcher.py** | Kommentierter Quellcode |
| **kivy_gui/main.py** | App + Screens (gut dokumentiert) |

---

## 🚀 Next Steps

### Sofort (heute)
```bash
1. Entpacke m3uScan_v21_5_KIVY_GUI.zip
2. pip install kivy aiohttp tqdm
3. python kivy_launcher.py
```

### Kurz (diese Woche)
- Erstes Konto hinzufügen
- Status-Check durchführen
- Auf Android testen

### Länger (optional)
- Buildozer APK erstellen
- Im Google Play Store hochladen
- Mit CLI-Version synchronisieren

---

## 📊 Vergleich: Alle m3uScan GUIs

| Feature | CLI | Tkinter | Kivy |
|---------|-----|---------|------|
| Android | ❌ | ❌ | ✅ |
| Desktop | ✅ | ✅ | ✅ |
| QPython 3 | ✅ | ❌ | ✅ |
| Touch-Opt. | ❌ | ❌ | ✅ |
| Grafisch | ❌ | ✅ | ✅ |
| Offline | ✅ | ✅ | ✅ |
| Größe | 200 KB | 250 KB | 60 KB |

**Empfehlung:**
- Android → **Kivy GUI** ⭐
- Desktop nur → **Tkinter GUI** (größer, aber feiner)
- CLI only → **m3uScan_v21_5.py** (leichtgewichtig)
- Alle Plattformen → **Kivy GUI** ⭐⭐⭐

---

## ✅ Checkliste

Vor der Verwendung:
- [ ] m3uScan_v21_5.py im gleichen Verzeichnis
- [ ] Kivy installiert (`pip install kivy`)
- [ ] aiohttp installiert (`pip install aiohttp`)
- [ ] tqdm installiert (`pip install tqdm`)
- [ ] kivy_launcher.py oder `python -m kivy_gui.main`
- [ ] App startet ✅

---

## 💡 Pro Tips

1. **Für Pydroid 3:**
   - Nutze Terminal statt Editor für bessere Performance
   - Speichere Dateien in `/storage/emulated/0/`

2. **Für Buildozer APK:**
   - Braucht ~10 GB Speicher
   - Erste Build dauert 20-30 Minuten
   - Danach nur noch 1-2 Minuten

3. **Für Desktop:**
   - Nutze Tkinter GUI wenn möglich (größer, aber nativer)
   - Kivy GUI wenn Cross-Platform nötig

4. **Datensynchronisation:**
   - link_ledger.json mit Cloud-Sync (Google Drive, Dropbox)
   - dann auf Android zugreifen

---

## 🎉 Zusammenfassung

✅ **Du hast jetzt 3 GUI-Optionen:**

1. **Tkinter GUI** (Desktop only, feiner)
   - `python gui_launcher.py`

2. **Kivy GUI** (Android + Desktop, lightweight) ⭐⭐⭐
   - `python kivy_launcher.py`

3. **CLI** (Alle Plattformen, Terminal)
   - `python m3uScan_v21_5.py`

**Für Android: Nutze die Kivy GUI!** 🚀

---

**Status:** ✅ Production Ready  
**Version:** 21.5-kivy  
**Datum:** 2026-06-06  
**Autor:** TheGermanGuy™
