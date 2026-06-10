# v28.1 Update: Aktive Verbindungen [X/Y] im Live-Monitor

## 🎯 Neue Feature

Während des Scans wird nun **live** die Anzahl der aktiven Verbindungen angezeigt:

### Vorher (v28.0):
```
● host:port | user | 45T 3h | [ DE* ALLE KATEGORIEN ]
```

### Nachher (v28.1):
```
● host:port | user | 45T 3h | [2/8] | [ DE* ALLE KATEGORIEN ]
                              ^^^^^^
                        Aktive / Maximale Worker
```

---

## 📊 Was bedeutet [2/8]?

- **2** = Aktuelle Anzahl **aktiver Verbindungen**
- **8** = **Maximale Anzahl Worker** (konfigurierbar via Scan-Modus)

### Beispiele:
```
[0/8]  → Keine Worker aktiv (Server antwortet langsam oder Pause)
[8/8]  → Alle Worker beschäftigt! (Maximum ausgelastet)
[4/8]  → 4 von 8 Worker in Nutzung (50% Auslastung)
[1/4]  → Mobile-Gerät mit 4 max Worker, nur 1 aktiv
```

---

## 🔧 Technische Implementierung

### Wie funktioniert es?

**Counter-Tracking mit asyncio.Lock:**

```python
# In scan_accounts_main():
active_count = {"value": 0}          # Shared Counter
active_lock = asyncio.Lock()          # Thread-Safety

async def bound(url_str):
    async with sem:
        # Worker startet
        async with active_lock:
            active_count["value"] += 1     # +1
        try:
            # Scan-Arbeit hier...
            return await worker(...)
        finally:
            # Worker beendet
            async with active_lock:
                active_count["value"] -= 1  # -1

# Bei Treffer-Ausgabe:
hit_str = _format_hit_oneline(res,
                              active_workers=active_count["value"],
                              max_workers=cfg.workers)
```

### Warum ist das nützlich?

1. **Performance-Debugging:** Sieht man ob Worker ausgelastet sind
2. **Netzwerk-Monitoring:** [0/8] zeigt Netzwerkprobleme schnell
3. **Live-Feedback:** Benutzer sieht dass Scan aktiv läuft
4. **Optimal-Tuning:** Kann man Worker-Anzahl anpassen wenn zu viel/wenig genutzt

---

## 📈 Beispiel aus echtem Scan

```
[00:15<01:30, 2.5 acc/s] | DE=45 VPN=3 CF=8 ⧗=2
● 192.168.1.100:8080 | user123 | 45T 3h | [8/8] | [ DE* ALLE KATEGORIEN ]
● portal.tv:25461 | admin   | 30T 5h | [7/8] | [ DE~ NUR LIVE ]
● stream.io:80     | pass   | 2T 1d  | [8/8] | [ VPN GESPERRT ]
```

**Interpretation:**
- Alle 8 Worker sind aktiv (voll belastet)
- Scan läuft mit voller Geschwindigkeit
- 2.5 Accounts pro Sekunde (guter Durchsatz)

---

## ⚙️ Worker-Anzahl konfigurieren

### Im Scan-Modus wählen:

```
[A] Auto       ← Berechnet optimal (basierend auf CPU/RAM)
[1] Schnell    ← 8 Worker (Desktop) / 4 (Mobile)
[2] Normal     ← 8 Worker
[3] Gründlich  ← 8 Worker (aber mit Timeouts)
[5] Manuell    ← Benutzer wählt selbst
```

### Im manuellen Modus:

```
Anzahl Workers [0=Standard/8]: 16  ← Setzt 16 max Worker
```

### Adaptive Konfiguration:

Bei Modus [A] Auto wird berechnet:
- **Desktop:** Anzahl Unique Hosts ÷ 3 (min 4, max 20)
- **Mobile:** Anzahl Unique Hosts ÷ 3 (min 1, max 4)

---

## 🚨 Was wenn [0/8] immer angezeigt wird?

Das bedeutet: **Server antwortet langsam oder ist offline**

```
[00:15<01:30] Worker=0/8 - Netzwerkprobleme möglich!
[00:15<01:30] Worker=0/8 - Server antwortet nicht!
```

**Lösungen:**
1. Server-Verbindung prüfen: `ping host:port`
2. Timeout erhöhen: Modus [5] Manuell → höhere Timeouts
3. VPN-Status prüfen (wenn VPN nötig)
4. Firewall-Regeln prüfen

---

## 📊 Live-Monitoring Beispiele

### Szenario 1: Optimale Auslastung
```
[4/8] [4/8] [4/8] [4/8] [4/8]  ← Konsistent 50% Auslastung
→ Server ist nicht zu überfordert, kann aber schneller gehen
→ Vorschlag: Worker auf 12 erhöhen
```

### Szenario 2: Server überlastet
```
[8/8] [8/8] [8/8] [8/8] [8/8]  ← Immer 100% Auslastung
⧗=50 Timeout-Fehler
→ Server kann nicht mithalten
→ Vorschlag: Worker reduzieren auf 4
```

### Szenario 3: Zu wenig Worker
```
[2/8] [2/8] [1/8] [2/8] [3/8]  ← Durchschnitt 2/8 (25%)
→ Viel ungenutztes Potential
→ Vorschlag: Worker erhöhen auf 16 (wenn Netzwerk OK)
```

---

## 📝 Zusammenfassung

| Punkt | Details |
|-------|---------|
| **Was** | [aktiv/max] Worker-Status im Terminal |
| **Wo** | Zwischen Restlaufzeit und Label-Info |
| **Wann** | Live während Scan läuft |
| **Wie** | Async Counter mit Lock |
| **Nutzen** | Performance-Debugging & Monitoring |

---

**v28.1 bietet damit vollständige Live-Transparenz beim Scan!** 👍

Benutzer können jetzt:
- ✅ DE-Treffer sehen (Ticker: DE=45)
- ✅ VPN-Treffer sehen (Ticker: VPN=3)
- ✅ Worker-Auslastung monitoren ([2/8])
- ✅ Restlaufzeit pro Account sehen (45T 3h)
- ✅ HTTP-Status Icons (●, ✕, ◓, ▲, ⧗)
