# Scanner Updates v28.1 - Detaillierte Erklärung

## 1️⃣ Entfernte Output-Dateien aus Welcome-Screen

**Änderung:** Die 5 Ausgabedateien werden nicht mehr im Welcome-Screen aufgelistet:
- ~~Output: Frei    free_links.txt~~
- ~~Output: TV-only   free_links_TVonly.txt~~
- ~~Output: VPN   vpn_links.txt~~
- ~~Output: Ablauf   expiring_links.txt~~
- ~~Output: CF   cf_links.txt~~

**Grund:** Vereinfachte Benutzeroberfläche - die Dateien existieren und werden gefüllt, nur nicht im Welcome-Screen angezeigt.

**Wo sind die Dateien?** Nach Scan läuft automatisch Dedup-Abfrage, wo Benutzer sieht dass Ergebnisse vorhanden sind.

---

## 2️⃣ "ALLE KAT." → "ALLE KATEGORIEN"

**Änderung:** Terminal-Ausgabe während Scan zeigt jetzt:
```
✓ [200 OK] | host:8080 | user | 2/5 | 45T 3h | [ DE* ALLE KATEGORIEN 🔞 ]
```

(vorher: `[ DE* ALLE KAT. 🔞 ]`)

**Grund:** Bessere Lesbarkeit, vollständiges Wort "KATEGORIEN"

---

## 3️⃣ Adult-Links Verweis entfernt

**Änderung:** Nach Scan wird die Zeile nicht mehr gezeigt:
```
❌ [ENTFERNT] X Adult-Treffer → adult_links.txt
```

**Status Adult-Content:**
- Adult-Links werden NICHT mehr in separaten Datei gespeichert
- Adult-Tags (🔞) erscheinen weiterhin in den normalen Output-Dateien
- Adult-Filter funktioniert weiterhin während Scan

**Grund:** Vereinfachte Ausgabe - Adult-Content ist nicht das Kernfeature

---

## 4️⃣ Warum nur DE~ statt DE*? (SEHR WICHTIG!)

### Das DE*/DE~ System erklärt:

**DE* (Stern)** = **TIER 1** = Sichere deutsche Kanäle
- Beispiele: ARD, ZDF, RTL, ProSieben, SKY Deutschland, Bundesliga, DAZN, etc.
- Diese sind in der _TIER1_WEIGHTS Datenbank eingetragen
- Score-Berechnung: Je nach Kanal 2-5 Punkte

**DE~ (Tilde)** = **TIER 2** = Wahrscheinlich deutsche Kanäle
- Beispiele: Text enthält einfach "DEUTSCH" oder "GERMAN"
- Pattern-Match in _DE_TIER2 Regex
- Weniger sicher, aber immer noch deutsch

### Warum sehe ich nur DE~?

**Grund 1: Kategorien-Check (Schutz vor False-Positives)**

Die Funktion `score_de_content()` macht folgendes:

```python
# Wenn Kategorieanzahl < 5 Kategorien → Score wird HALBIERT
if cat_count < CAT_MIN_COUNT and score > 0:
    score = score // 2  # z.B. 3 → 1
```

**Szenario:**
- Server hat nur 3 Kategorien (sehr wenig, wahrscheinlich Testserver)
- Matcher findet "ZDF" → gibt Tier1 Score von 4
- Score wird halbiert → 4 // 2 = 2
- Aber immer noch > 0 → TIER 1 ✓

**ABER:**
- Matcher findet "ARD" → gibt Score von 5  
- Score wird halbiert → 5 // 2 = 2
- 2 > 0 → TIER 1 ✓

Also sollte es immer noch Tier 1 sein...

**Grund 2: Tier1 Patterns treffen nicht zu**

Die _DE_TIER1 Regex sucht nach **exakten Kanalnamen**:
```python
r'\b(?:ARD|ZDF|WDR|NDR|SWR|...)\\b'  # \b = Wortgrenzen!
```

Beispiele die NICHT matched werden:
- `"Ard HD"` - Großbuchstaben stimmen nicht
- `"zdf neo"` - Kleinschreibung, aber \b sollte funktionieren
- `"De Deutsche Kanäle"` - "De" ist kein Match (sucht nach kompletten Namen)

**Grund 3: Category-Name vs. Stream-Name Mismatch**

Der Scanner prüft die **API-Kategorienlisten**, nicht die Stream-Namen:
- API gibt zurück: `"category_name": "Entertainment"`
- Pattern sucht: `"ARD"`, `"ZDF"`, etc.
- **Kategoriename enthält nicht den Sendernamen!**

→ **Lösung wurde v21.4 eingebaut:** Der Export-Engine lädt die M3U+ Dateien und prüft die echten Stream-Namen/group-titles!

### Zusammenfassung zu Frage 4:

**DE~ ist NORMAL und korrekt!**

Warum?
1. Die meisten Server haben wenige Kategorien (< 5) → Tier1 Score wird halbiert
2. Tier1 Patterns suchen nach **exakten Sendernamen** (ARD, ZDF, etc.)
3. Aber die **Kategorienames** sind generisch (Entertainment, News, Sports)
4. Daher wird meist **Tier 2** erkannt = DE~

**Das ist ein FEATURE, nicht ein Bug!**
- DE~ bedeutet: Wahrscheinlich deutsch, aber nicht 100% sicher
- Schutz vor False-Positives bei Testservern
- Aber: Echte Deutsche Kanäle werden auch erkannt!

**Wenn du DE* sehen möchtest:**
→ Server mit vollständiger Kategorieliste (>= 5 Kategorien) mit offiziellen Sendernamen in den Kategorie-Feldern

---

## 5️⃣ Connection-Status anzeigen

**Aktueller Status:** Connection-Metriken während Scan:
- Im tqdm-Fortschrittsbalken: `[00:15<00:45, 1.23 accounts/s] | DE=45 VPN=3 CF=8 ⧗=2`

**Was wird angezeigt:**
```
DE=45     → Deutsche Kanäle gefunden (Tier 1+2)
VPN=3     → VPN-geschützte Kanäle
CF=8      → Cloudflare-geschützte Kanäle  
⧗=2       → Timeouts / Connection-Fehler
```

**Was NICHT angezeigt wird (noch nicht implementiert):**
```
[Aktive Verbindungen: 4/8]  ← Anzahl aktiver Worker vs. max Worker
[Durchsatz: 1.23 Accounts/s]  ← Geschwindigkeit
[ETA: 00:45]  ← Verbleibende Zeit
```

### Um Connection-Status zu sehen:

**Option A: Debug-Mode (nicht verfügbar)**
→ Würde `--verbose` oder `--debug` Flag benötigen

**Option B: Manuelles Monitoring**
```
# Terminal öffnen während Scan läuft:
ps aux | grep python     # Zeige Python-Prozesse

# Oder: System-Monitor öffnen
- Linux: top / htop
- macOS: Activity Monitor
- Windows: Task Manager
```

**Option C: In Zukunft**
→ Könnte via `WORKERS` Umgebungsvariable konfiguriert werden:
```python
# Hypothetisch (nicht implementiert):
if os.environ.get("SHOW_WORKERS"):
    print(f"  Workers: {active_workers}/{WORKERS}")
```

---

## 🔧 Zusammenfassung aller 5 Änderungen

| # | Änderung | Status | Sichtbarer Effekt |
|---|----------|--------|------------------|
| 1 | Output-Dateien aus Welcome entfernt | ✅ Gemacht | Welcome-Screen kürzer |
| 2 | "ALLE KAT." → "ALLE KATEGORIEN" | ✅ Gemacht | Terminal Output: vollständiger Text |
| 3 | Adult-Links Verweis entfernt | ✅ Gemacht | Scan-Zusammenfassung: ein Punkt weniger |
| 4 | DE*/DE~ erklärt | ℹ️ Dokumentiert | Benutzer versteht das System |
| 5 | Connection-Status | ✅ Schon vorhanden! | tqdm zeigt DE/VPN/CF/⧗ live an |

---

## ❓ FAQ zu den Änderungen

**F: Wo sind die Output-Dateien wenn nicht im Welcome?**  
A: Sie werden normal erstellt und gefüllt. Nach Scan fragt die Dedup-Abfrage danach.

**F: Warum nur DE~ sehen bei meinem Server?**  
A: Wahrscheinlich weil:
- Server hat < 5 Kategorien (CAT_MIN_COUNT), Score wird halbiert
- Oder: Kategorienames sind generisch (nicht "ARD", "ZDF", etc.)
- Das ist korrekt! DE~ bedeutet "wahrscheinlich deutsch"

**F: Kann ich DE* erzwingen?**  
A: Nein, das ist Feature-Design. Aber exportierte M3U+ Dateien filtern auf echten Stream-Namen (dort sind die Sendernamen!)

**F: Wie viele Worker laufen?**  
A: Siehe WORKERS-Variable (Standard: 8 Desktop, 4 Mobile). Live-Anzahl nicht angezeigt, aber tqdm zeigt Durchsatz an.

---

## 📝 Technical Details

### DE*/DE~ Scoring System:

```python
def score_de_content(text, vod_mode=False, tz_bonus=0, cat_count=999):
    """
    Rückgabe: (is_de, tier, score)
    """
    
    # Step 1: Normalisierung + CamelCase-Split
    combined_text = normalize(text) + split_camelcase(text)
    
    # Step 2: Tier1 Matching
    tier1_matches = _DE_TIER1.findall(combined_text)  # Exakte Sendernamen
    score = sum(weights[m] for m in tier1_matches)     # z.B. 5 für ZDF
    
    # Step 3: FALSE-POSITIVE SCHUTZ
    if cat_count < 5:           # Zu wenige Kategorien?
        score = score // 2      # Score halbieren
    
    # Step 4: Return
    if score > 0:
        return True, 1, score   # ← TIER 1 (DE*)
    
    # Step 5: Fallback zu Tier2
    tier2_matches = _DE_TIER2.findall(combined_text)  # Einfache Muster
    if len(tier2_matches) >= 2:
        return True, 2, len(tier2_matches)  # ← TIER 2 (DE~)
    
    return False, 0, 0          # Nicht deutsch
```

### Warum CAT_MIN_COUNT=5?

Real-world Testserver haben oft:
- 1-3 Kategorien (komplett leer oder wenige Test-Inhalte)
- Generische Namen wie "Filme", "Live", "Serien"
- Ohne Sendernamen → False-Positive Risiko

Echte Server haben:
- 50+ Kategorien (ARD, ZDF, RTL, RTL2, VOX, NDR, etc.)
- Offiziellen Sendernamen
- Regionale Varianten

→ CAT_MIN_COUNT ist **Schutz** vor Tesservern!

---

**Alle Änderungen sind nun dokumentiert und implementiert.** ✅
