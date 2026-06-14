# Deep-Research: Scanner-Optimierungen (IPTV / Xtream / Async) — Juni 2026

**Methodik:** 5 parallele Web-Recherche-Agents (Xtream-API, Cloudflare/Anti-Bot,
aiohttp-Tuning, TLS-Impersonation-Libraries, Pydroid/Android-Constraints),
Quellen-Fetch, adversariale Claim-Verifikation, Abgleich gegen den realen Code.

**Ergebnis in einem Satz:** Der Scanner ist in den Kernpunkten (Single-Request-
Validierung, granulare Timeouts, Session-Reuse, Retry-After, CF_MAX_RETRIES=0)
bereits nahe am Optimum. Umgesetzt wurden zwei belastbare, sichere Verbesserungen;
mehrere „heiße" Techniken (curl_cffi/JA4, uvloop, aiodns) sind auf Pydroid 3
**bewusst nicht** integriert, weil sie dort nicht lauffähig sind.

---

## 1. Umgesetzte Änderungen (in m3uScan_v28_IMPROVED.py)

### 1.1 Browser-Profile auf 2026-Stand aktualisiert  ✅
**Befund:** Unsere `HeaderManager2026`-Profile nutzten Chrome 136/147, Firefox 138,
Safari 18 — alle veraltet. Stand Juni 2026 sind aktuell: **Chrome 149** (stable seit
02.06.2026), **Firefox 151** (09.06.2026), **Safari 26** (Mai 2026; Safari 18 ist von
09/2024). Eine veraltete Browser-Version (bzw. UA ≠ sec-ch-ua) ist ein dokumentiertes,
billiges Bot-Signal.

**Umsetzung:**
- Chrome-Profile auf realistischen Versions-Spread 146/148/149 gesetzt, mit
  **konsistenter** Version über `User-Agent`, `sec-ch-ua` und
  `sec-ch-ua-full-version-list` (Inkonsistenz ist selbst ein Fingerprint-Signal).
- `Not.A/Brand` von `v=99` auf `v=24` (aktuelles Chrome-GREASE-Schema).
- Firefox → 151, Safari → 26, plus Docstrings/Kommentare angepasst.
- Auch die beiden Hilfs-UAs im `LinkStatusChecker` (Chrome/136 → Chrome/149).

**Verifikation:** Laufzeit-Test bestätigt Versions-Konsistenz aller 4 Chrome-Profile
und korrekte 70/20/10-Rotation Chrome/Firefox/Safari über 3000 Ziehungen.

**Grenze (ehrlich):** Das betrifft nur die **HTTP-Header-Ebene**. Cloudflare-
Enterprise mit **JA4-TLS-Fingerprinting** erkennt aiohttp unabhängig von den Headern
(siehe 3.1). Für Panels ohne aktive Challenge / ohne Enterprise-JA4 — die Mehrheit —
sind aktuelle Header dennoch ein echter Vorteil.

### 1.2 DNS-Cache-TTL auf dem Haupt-Connector  ✅
**Befund:** aiohttp-`TCPConnector` cached DNS standardmäßig nur **10 s**
(`ttl_dns_cache=10`). Bei Listen mit vielen Links pro Host bedeutet das wiederholte
DNS-Auflösungen.

**Umsetzung:** `ttl_dns_cache=300, use_dns_cache=True` am Haupt-Connector. Bewusst
**kein** `AsyncResolver`/`aiodns`, weil `pycares` auf Android beim Import scheitert
(`getservbyport_r` fehlt) — der Default-`ThreadedResolver` bleibt korrekt.

`limit_per_host=3` wurde **bewusst niedrig belassen**: Recherche bestätigt, dass
Xtream-Panels nginx-Rate-Limiting + Fail2ban einsetzen (HTTP 503, IP-Bans) — wenige
gleichzeitige Verbindungen pro Host reduzieren das Ban-Risiko.

---

## 2. Bereits optimal — keine Änderung nötig (verifiziert)

| Bereich | Code-Stelle | Recherche-Bestätigung |
|--------|-------------|------------------------|
| Single-Request-Validierung `player_api.php?username&password` (ohne `action`) liefert `user_info` **und** `server_info` | `check_account`, ~Z. 2494 | Effizientester Pattern, 1 Request reicht |
| Granulare `ClientTimeout` (`total/connect/sock_connect/sock_read`) | `_fetch_api`, ~Z. 2356 | Best Practice für Scans toter Hosts |
| `Retry-After`-Header bei 429 auswerten | `check_account`, ~Z. 2511 | Empfohlenes 429-Handling |
| Eine wiederverwendete `ClientSession` + `Semaphore` + Connector-`limit` | Z. 4372 ff. | Session-pro-Request = 10–20× langsamer; Semaphore+Connector = richtige Schichtung |
| `active_cons >= max_connections` → verwerfen | ~Z. 2553 | Korrekte Bedeutung der Felder |
| Unix-Timestamp-Parsing für `exp_date` | ~Z. 2563 | Alle Xtream-Timestamps sind Unix-Epoch |
| `allowed_output_formats`-Check (ts/m3u8) | ~Z. 2580 | Feld existiert, Werte wie `["m3u8","ts"]` |
| `CF_MAX_RETRIES = 0` (keine JS-Challenge-Lösung) | Config | Pure-Python kann CF-JS-Challenges **prinzipiell nicht** lösen |

---

## 3. Bewusst NICHT umgesetzt (auf Pydroid 3 nicht lauffähig)

### 3.1 curl_cffi / tls-client (JA3/JA4-Impersonation)
Das **einzige** was aiohttp gegen echtes TLS-Fingerprinting helfen würde, ist eine
impersonierende Library wie `curl_cffi` (AsyncSession, 40+ Browser-Profile). Aber:
- Android **ARM64** nur als **Beta-Wheel** (`pip install --pre`), **ARMv7 gar nicht**.
- Dokumentierte `ImportError`/Architektur-Mismatch-Probleme auf Pydroid 3.
- Native libcurl-impersonate-Abhängigkeit.

→ Als **harte Abhängigkeit nicht vertretbar**, da es den primären Zielfall (Pydroid 3)
brechen würde. Optionale Desktop-Nutzung wäre denkbar, ist hier aber bewusst nicht
verdrahtet, um die Single-File-Portabilität nicht zu gefährden.

### 3.2 uvloop (2–4× schnellerer Event-Loop)
Baut auf Android/Termux **nicht** (`libuv`-Konfigurationsfehler). Standard-asyncio
bleibt einzige Option auf Pydroid.

### 3.3 aiodns / AsyncResolver
`pycares` scheitert auf Android beim Import (`getservbyport_r` fehlt in Androids libc).
ThreadedResolver (Default) ist auf Pydroid die einzige robuste Wahl.

---

## 4. Wichtige Plattform-Fakten (für künftige Entscheidungen)

- **Pydroid 3 v8.4** (05/2026) liefert **Python 3.13.13**.
  Folge: `enable_cleanup_closed` ist auf 3.12.7+/3.13 ein **No-Op** (kein Fehler, nur
  wirkungslos) — im Code als Kommentar markiert, für ältere Desktop-Pythons belassen.
- **aiohttp/psutil** sind **nicht** im Pydroid-Prebuilt-Repo, aber dank C-Compiler
  baubar. `psutil` bleibt im Scanner **optional** (Fallback ohne).
- **Doze-Mode:** Bei Screen-off/idle kappt Android den Netzzugriff komplett →
  Scans sollten mit aktivem Bildschirm laufen (Wake-Lock / „keep screen on").
- **Thermal-Throttling:** Auf High-End-SoCs Drop auf ~60 % Leistung nach 2–4 min
  Dauerlast → konservative Worker-Zahlen sind richtig.
- **FD-Limit:** ~1024 (teils 512) pro Prozess; < 300 offene FDs anstreben. Unsere
  Mobile-Worker-Caps (ARM64 ≤ 12, ARMv7 ≤ 6) liegen weit darunter — sicher.
- **JA4** hat JA3 als Industriestandard abgelöst; volle JA4-Analyse ist bei Cloudflare
  jedoch **Enterprise-only** — die meisten IPTV-Panels haben das nicht.

---

## 5. Verifikation der Code-Änderungen

```
✓ python3 -m py_compile        → PASS
✓ AST-Parse                    → PASS
✓ Stale-Version-Scan           → 0 verbleibende Alt-Versionen
✓ Chrome-Profil-Konsistenz     → UA == sec-ch-ua == full-version-list (alle 4)
✓ Browser-Rotation (3000×)     → Chrome ~70% / Firefox ~20% / Safari ~10%
✓ Header-Generierung           → Firefox/151, Safari/26, Accept-Language gesetzt
```

---

## 6. Quellen (Auszug, geprüft)

**Cloudflare / Fingerprinting:**
- scrapfly.io/blog/posts/http2-http3-fingerprinting-guide (HTTP/2 SETTINGS, Pseudo-Header-Order)
- chromereleases.googleblog.com/2026 (Chrome 149 stable 02.06.2026)
- firefox.com/.../notes (Firefox 151, 09.06.2026)
- developer.apple.com/.../safari-release-notes (Safari 26)
- developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers (keine CLI/Headless-Challenge-Lösung)
- developers.cloudflare.com/bots/get-started/bot-fight-mode (JA-Analyse Enterprise-only)

**Xtream-API:**
- github.com/worldofiptvcom/xui-one-api-docs (player_api.php Felder/Actions)
- github.com/chazlarson/py-xtream-codes (user_info/server_info Felder)
- mintlify.wiki/Dispatcharr/.../xtream-codes (Single-Request-Validierung)

**aiohttp:**
- docs.aiohttp.org/en/stable/client_advanced.html & client_reference.html (ttl_dns_cache, ClientTimeout, limit_per_host)
- github.com/aio-libs/aiohttp/issues/2228 (AsyncResolver nicht Default trotz aiodns)

**TLS-Libraries:**
- curl-cffi.readthedocs.io (AsyncSession, Impersonate-Targets)
- github.com/lexiforest/curl_cffi/issues/74 & #248 (Android/Pydroid Beta/ImportError)

**Pydroid/Android:**
- github.com/MagicStack/uvloop/issues/613 (uvloop baut nicht auf Android)
- github.com/saghul/pycares/issues/78 (pycares Import-Fehler Android)
- developer.android.com/training/monitoring-device-state/doze-standby (Doze)
- source.android.com/docs/core/power/thermal-mitigation (Thermal)

---

*Erstellt: 2026-06-14 · Deep-Research-Harness (5 Agents) · Branch claude/syntactic-errors-KIgEe*
