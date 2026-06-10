# v28.1 Update: Xtream-Account Verbindungen [A/M] im Live-Monitor

## 🎯 Neue Feature: Xtream Verbindungs-Status

Während des Scans wird nun **live** die Anzahl der aktiven/maximalen Verbindungen des **Xtream-Accounts** angezeigt:

### Vorher (v28.0):
```
● host:port | user | 45T 3h | [ DE* ALLE KATEGORIEN ]
```

### Nachher (v28.1):
```
● host:port | user | 45T 3h | [1/2] | [ DE* ALLE KATEGORIEN ]
                              ^^^^^
                    Xtream-Account Verbindungen
```

---

## 📊 Was bedeutet [1/2]?

- **1** = Aktuell **1 aktive Verbindung** des Accounts
- **2** = **Maximale Verbindungen** die der Account erlaubt

Diese Informationen kommen direkt vom Xtream-Server im `user_info` API-Response:
```json
{
  "user_info": {
    "active_cons": 1,           // Aktuelle Verbindungen
    "max_connections": 2,       // Maximum erlaubt
    ...
  }
}
```

### Beispiele:
```
[0/1]  → Account nutzt 0 von 1 erlaubten Stream (frei)
[1/1]  → Account voll belastet (1 von 1 Stream)
[2/3]  → 2 von 3 erlaubten Streams aktiv (67%)
[3/2]  → Fehler! Mehr aktiv als erlaubt (Serverfehlkonfiguration)
```

---

## 🎨 Farbcodierung

Je nach Auslastung färbt sich die Anzeige:

```python
# Grün: Nicht belastet
[1/4]  # ✓ 25% Auslastung

# Gelb: Warnung (>75% Auslastung)
[3/4]  # ⚠ 75% Auslastung

# Rot: Kritisch (100% oder über Maximum)
[4/4]  # ✗ 100% Auslastung
[5/4]  # ✗ ÜBERLASTET!
```

---

## 📈 Praktische Beispiele

### Scan mit verschiedenen Account-Limits:

```
● premium.tv:8080    | user1 | 30T 5h | [2/5] | [ DE* ALLE KATEGORIEN ]
  ↑ Premium-Account mit 5 erlaubten Streams, 2 aktiv (40%)

● budget.io:443      | user2 | 60T 2h | [1/2] | [ DE~ NUR LIVE ]
  ↑ Budget-Account mit 2 erlaubten Streams, 1 aktiv (50%)

● shared.org:25461   | user3 | 10T 3h | [4/4] | [ VPN GESPERRT ]
  ↑ Shared-Account vollständig belastet (100%)

● family.net:80      | user4 | -- --  | [0/3] | [ DE* ALLE KATEGORIEN ]
  ↑ Family-Account mit 3 erlaubten Streams, aber kein Stream aktiv
```

---

## 🔧 Technische Details

### Datenherkunft

Die Verbindungs-Info kommt aus der Xtream-API:

```python
# Im worker() werden diese Werte extrahiert:
active = int(user_info.get("active_cons", 0))
max_c  = int(user_info.get("max_connections", 0))

# Und übergeben an die Ausgabe-Funktion
return {
    "active": active,   # z.B. 1
    "max_c": max_c,     # z.B. 2
    ...
}
```

### Filter: Max erreicht?

Wenn `active >= max_connections`, wird der Account **verworfen**:

```python
if max_c != 0 and active >= max_c:
    return None, "max_erreicht", ...
```

Das bedeutet: Accounts die bereits ihre Verbindungs-Limit erreicht haben, werden **nicht** in den Export aufgenommen (gute Accounts nur).

---

## ✨ Nutzen dieser Feature

1. **Account-Qualität bewerten**: [2/5] ist besser als [4/4]
2. **Verfügbarkeit prüfen**: [0/3] könnte ein Problem sein
3. **Live-Monitoring**: Sieht ob Accounts belastet sind
4. **Debugging**: Xtream-Server-Konfiguration überprüfen
5. **User-Experience**: Benutzer sieht gerade noch verfügbare Slots

---

## 📝 Häufige Fragen

### F: Was ist der Unterschied zu den Worker-[X/Y]?
**A:** Das sind zwei völlig unterschiedliche Dinge:
- **Worker [2/8]**: Xtream-Scanner nutzt 2 von 8 parallelen Prozessen (VERALTET, wurde entfernt)
- **Account [1/2]**: Xtream-Account selbst hat 1 von 2 Streams aktiv (NEU!)

### F: Warum zeigt [1/2] wenn der Server nur 1 Stream erlaubt?
**A:** Der Xtream-Panel Betreiber hat `max_connections = 2` gesetzt.
Das bedeutet, dass Account-Inhaber kann bis zu 2 simultane Streams haben.

### F: Was bedeutet [5/4]?
**A:** Fehlerfall! Der Server hat Fehler:
- Account hat Max von 4
- Aber 5 Streams sind aktiv
Das passiert selten und deutet auf eine Server-Fehlerkonfi hin.

### F: Werden Accounts mit [4/4] exportiert?
**A:** **Nein!** Die Funktion `check_account()` verwirft sie:
```python
if max_c != 0 and active >= max_c:
    return None, "max_erreicht", ...
```
Das ist gut - vollausgelastete Accounts sind nicht hilfreich.

---

## 📊 Zusammenfassung

| Komponente | Bedeutung | Quelle |
|-----------|-----------|--------|
| **[A/M]** | Xtream-Account Verbindungen | `user_info.active_cons / max_connections` |
| **Farbe** | Auslastungs-Indikator | Berechnet: A/M Verhältnis |
| **Filter** | Max erreicht? → Verworfen | `if A >= M: skip` |
| **Nutzen** | Account-Qualität bewerten | Live-Monitoring während Scan |

---

**v28.1 bietet damit vollständige Transparenz zum Account-Status!** 🎯

Benutzer können jetzt:
- ✅ DE-Treffer sehen (Ticker: DE=45)
- ✅ VPN-Treffer sehen (Ticker: VPN=3)
- ✅ **Verbindungs-Status sehen ([1/2])**
- ✅ Restlaufzeit pro Account sehen (45T 3h)
- ✅ HTTP-Status Icons (●, ✕, ◓, ▲, ⧗)
