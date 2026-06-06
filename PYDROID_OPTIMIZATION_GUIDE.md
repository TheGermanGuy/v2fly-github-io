# Pydroid 3 Optimization Guide

**Detaillierte Tuning-Parameter für m3uScan Kivy GUI auf Pydroid 3**

---

## 🎯 Optimierungsziele

Pydroid 3 läuft auf **ARM CPUs** mit **begrenztem RAM**. Diese Anleitung hilft, die beste Performance zu erreichen.

---

## 📊 Auto-Detected Profiles

Das System erkennt automatisch das optimale Profil:

### Low-Memory Device (<2GB RAM)

```
✓ Workers: 1
✓ Batch Size: 5
✓ Cache: 50 MB
✓ Timeout: 15 Sekunden (2.5x)
✓ UI Refresh: 20 FPS
✓ Animations: AUS
✓ GC Tuning: Aggressiv
```

**Geräte:**
- Ältere Android-Geräte
- Budget-Phones
- Tablets mit <2GB RAM

---

### Normal Device (2-4GB RAM)

```
✓ Workers: 2
✓ Batch Size: 10
✓ Cache: 100 MB
✓ Timeout: 15 Sekunden (1.5x)
✓ UI Refresh: 30 FPS
✓ Animations: AN
✓ GC Tuning: Normal
```

**Geräte:**
- Mittlere Smartphones
- Standard-Tablets
- Alte Flaggschiffe

---

### High-Performance Device (>4GB RAM)

```
✓ Workers: 4
✓ Batch Size: 25
✓ Cache: 300 MB
✓ Timeout: 10 Sekunden (1.5x)
✓ UI Refresh: 30 FPS
✓ Animations: AN
✓ GC Tuning: Normal
```

**Geräte:**
- Neue Smartphones
- Premium Tablets
- Multi-Core Devices

---

## ⚙️ Tuning-Parameter Erklärung

### Workers (parallele Verarbeitung)

```
Definition: Anzahl der gleichzeitigen Netzwerk-Requests

- Workers=1: 1 Konto zur Zeit (sicher, langsam)
- Workers=2: 2 Konten gleichzeitig (balanced)
- Workers=4: 4 Konten gleichzeitig (schnell, braucht RAM)

Pydroid ARM: max 2 Worker empfohlen
ARMv7 (alte Chips): max 1-2
ARM64 (neue Chips): max 2-4
```

**Empfehlung ändern:**
```
Einstellungen → Performance → Max Workers: [1-4]
```

---

### Batch Size (Chunks pro Durchgang)

```
Definition: Wieviele Konten pro Batch verarbeitet

- 5: Klein-Geräte, sicher
- 10: Normal, balanced
- 25: Große Geräte, schnell

Speicher pro Item: ~100KB
Also: Batch-Size × 100KB = RAM benötigt
```

**Beispiel:**
- Batch Size 5 → 500 KB pro Batch
- Batch Size 25 → 2.5 MB pro Batch

**Empfehlung ändern:**
```
Einstellungen → Performance → Batch Size: [5-25]
```

---

### Cache Size (lokale Zwischenspeicherung)

```
Definition: Größe des lokalen Caches für Status-Daten

- 50 MB: Low-Memory Devices
- 100 MB: Normal Devices
- 300 MB: High-Performance Devices

Cache TTL: 1 Stunde (standard)
Speicherort: ~/.m3uscan/.cache/
```

**Cache leeren:**
```
Einstellungen → Storage → [Clear Cache Button]

Oder manuell:
rm -rf ~/.m3uscan/.cache/*
```

---

### Network Timeout

```
Definition: Sekunden zu warten auf Server-Antwort

Standard: 10 Sekunden (Desktop)
Pydroid: 15 Sekunden (1.5x langsamer)
ARMv7: 25 Sekunden (2.5x langsamer)

Je nach Netzwerk:
- WiFi: 10-15s
- Mobile 4G: 15-20s
- Mobile 3G/2G: 20-30s
```

**Empfehlung ändern:**
```
Einstellungen → Network → Timeout: [5-60 Sekunden]
```

**Signale für Timeout zu kurz:**
- "Connection timeout" Fehler
- Viele fehlgeschlagene Checks
- Viele Timeouts im Log

**Lösung:** Erhöhe auf +5 Sekunden und versuche erneut

---

### UI Refresh Rate (FPS)

```
Definition: Wie oft pro Sekunde die UI aktualisiert wird

Desktop: 60 FPS (16 ms pro Frame)
Pydroid Normal: 30 FPS (33 ms pro Frame)
Pydroid Low-Memory: 20 FPS (50 ms pro Frame)

Auswirkung auf Batterie:
- Weniger FPS = Weniger CPU = Weniger Batterie
```

**Automatisch erkannt**, aber manuell anpassbar in advanced settings.

---

### Garbage Collection (GC)

```
Definition: Automatisches Speicheraufräumen

Low-Memory Mode:
- gc_threshold0: 500 (sofort)
- gc_threshold1: 10 (aggressiv)
- gc_threshold2: 10 (aggressiv)

Normal Mode:
- gc_threshold0: 2000 (normal)
- gc_threshold1: 10 (normal)
- gc_threshold2: 10 (normal)

Zu aggressiv = mehr CPU-Last
Zu schwach = Memory Leaks
```

**Automatisch erkannt**, keine manuelle Anpassung nötig.

---

## 🔧 Manuelle Optimierungen

### 1. Memory Leak Prevention

```bash
# Starte App regelmäßig neu
# Oder nutze Auto-Restart nach N Stunden

# Überprüfe RAM-Nutzung:
cd ~/.m3uscan
free -m  # Zeigt verfügbaren RAM
```

### 2. Batch Check Strategie

```
Bei 100 Konten:
- Batch Size 5 → 20 Batches (lange)
- Batch Size 10 → 10 Batches (okay)
- Batch Size 25 → 4 Batches (schnell, mehr RAM)

Recommendation: Start with 10, adjust based on performance
```

### 3. Network Optimization

```bash
# WiFi ist schneller als Mobile
# 4G > 3G > 2G

# Falls Mobile nur: erhöhe Timeout
# Falls WiFi: kann Timeout reduziert werden

# Prüfe Signalstärke:
adb shell dumpsys telephony.registry | grep signalLevel
```

### 4. Auto-Cleanup

```
Einstellungen → Storage → Auto Cleanup: AN

Automatisches Löschen von:
- Backups älter als 7 Tage
- Logs älter als 7 Tage
- Temp-Dateien
```

### 5. Offline Mode

```
Einstellungen → App → Offline Mode: AN

Nutzt gecachte Daten wenn netzwerk offline
Schneller und batterieschonend
```

---

## 📈 Performance Monitoring

### Log-Datei analysieren

```bash
# Öffne Log in Terminal
cat ~/.m3uscan/logs/m3uscan_YYYYMMDD.log | tail -50

# Suche nach Performance-Hinweisen:
grep "SLOW\|TIMEOUT\|ERROR" ~/.m3uscan/logs/*.log

# Anzahl der Fehler zählen:
grep "ERROR\|TIMEOUT" ~/.m3uscan/logs/*.log | wc -l
```

### Wichtige Metriken

```
✓ Average Check Time: 2-5 Sekunden pro Konto
✓ Success Rate: >90%
✓ Memory Usage: <50% des verfügbaren RAM
✓ Battery: <5% pro Stunde

Wenn nicht:
→ Erhöhe Timeout
→ Reduziere Batch Size
→ Aktiviere Low-Memory Mode
```

---

## 🎯 Optimierungs-Szenarien

### Scenario 1: App ist sehr langsam

```
Symptome: 30+ Sekunden für 10 Konten

Lösungen (der Reihe nach):
1. Prüfe Netzwerk: ping 8.8.8.8
2. Erhöhe Timeout: Einstellungen → 20s
3. Reduziere Batch Size: 5 statt 10
4. Reduziere Workers: 1 statt 2
5. Aktiviere Offline-Mode (nutzt Cache)
```

### Scenario 2: App friert ein / crasht

```
Symptome: Black screen, muss Neustart

Lösungen:
1. Aktiviere Low-Memory Mode
2. Reduziere Batch Size zu 5
3. Reduziere Workers zu 1
4. Reduziere Cache Size zu 50 MB
5. Deaktiviere Animations
6. Starte Pydroid neu (Force Quit)
```

### Scenario 3: Status-Checks fehlen oft

```
Symptome: "Connection Timeout" Fehler

Lösungen:
1. Prüfe WiFi-Verbindung
2. Erhöhe Timeout: 15s → 20s
3. Prüfe Firewall (Port 8080 offen?)
4. Prüfe ob Server online: curl http://host:port
5. Nutze andere WiFi / Mobile Network
```

### Scenario 4: Batterie wird schnell leer

```
Symptome: >10% pro Stunde

Lösungen:
1. Deaktiviere Animations
2. Reduziere UI Refresh Rate zu 20 FPS
3. Deaktiviere Auto-Check
4. Nutze WiFi statt Mobile Data
5. Lösche große Log-Dateien (Auto-Cleanup)
```

### Scenario 5: Speicher voll

```
Symptome: "Storage Low" Benachrichtigung

Lösungen:
1. Aktiviere Auto-Cleanup
2. Lösche alte Backups:
   rm ~/.m3uscan/backups/*_old
3. Lösche alte Logs:
   rm ~/.m3uscan/logs/*.log
4. Exportiere & lösche selten benutzte Konten
```

---

## 📋 Tuning Checklist

### Vor Start

- [ ] Pydroid 3 Terminal öffnet
- [ ] `python3 kivy_launcher.py` funktioniert
- [ ] GUI startet in <10 Sekunden
- [ ] Konto kann hinzugefügt werden

### Während Benutzung

- [ ] Checks dauern <5s pro Konto
- [ ] Erfolgsquote >90%
- [ ] Keine Freezes/Crashes
- [ ] Batterie-Nutzung normal

### Performance-Check

```bash
# Tue alle 2 Wochen:
1. Überprüfe Memory:
   free -m
2. Überprüfe Speicher:
   du -sh ~/.m3uscan/
3. Schaue Logs an auf Fehler
4. Räume alte Dateien auf
```

---

## 🔍 Advanced Debugging

### CPU Profile

```
ARMv7 (alt): 1-2 GHz, Langsamer
ARM64 (neu): 2-3 GHz, Schneller
Quadcore: 4 cores, besser parallelisieren
```

**Prüfe CPU-Architektur:**
```bash
python3 -c "from kivy_gui.utils.pydroid_detector import pydroid_detector; print(pydroid_detector.get_cpu_arch())"
```

### Memory Profile

```bash
# Detaillierte Memory-Info
python3 -c "from kivy_gui.utils.pydroid_detector import pydroid_detector; print(pydroid_detector.get_memory_info())"

# Output Beispiel:
# {
#   'total_mb': 2048,          ← Gesamter RAM
#   'available_mb': 1024,      ← Verfügbar
#   'percent_used': 50         ← Prozent genutzt
# }
```

---

## 💾 Backup Strategy

```
Auto-Backup jede Stunde wenn Änderung
Max 5 Backups, älteste löschen

Manuelle Backups:
1. Einstellungen → [Backup Now Button]
2. oder: cp ~/.m3uscan/data/link_ledger.json ~/.m3uscan/backups/manual_backup.json
```

---

## 🎓 Learning Resources

```
Phase 1-3 (Basics):
- PYDROID_INSTALLATION_GUIDE.md ← Du bist hier

Phase 4-6 (Intermediate):
- PYDROID_OPTIMIZATION_GUIDE.md ← Du bist hier
- KIVY_GUI_DOCUMENTATION.md

Phase 7+ (Advanced):
- PYDROID_TROUBLESHOOTING.md
- Log files in ~/.m3uscan/logs/
```

---

**Status:** ✅ Production Ready  
**Version:** 21.5-kivy-pydroid  
**Letztes Update:** 2026-06-06  
**Autor:** TheGermanGuy™
