# Evony Verteidigungsberater

KI-gestützter Verteidigungsberater für **Evony: The King's Return** auf Basis der Claude API (Modell `claude-fable-5`).

**Wichtig – kein Bot:** Dieses Tool liest keine Daten automatisch aus dem Spiel aus und führt keine Spielaktionen aus. Du machst die Screenshots selbst, bestätigst die erkannten Werte und setzt alle Empfehlungen manuell im Spiel um. Damit verstößt das Tool nicht gegen die Evony-Nutzungsbedingungen.

## Ablauf

```
Du → Screenshots → extract (KI liest Werte) → stats.json prüfen/korrigieren → advise → Strategiebericht → Du setzt manuell um
```

## Voraussetzungen

- Node.js 20+
- Ein Anthropic-API-Key: <https://platform.claude.com>

```bash
cd evony-defense-advisor
npm install
export ANTHROPIC_API_KEY=sk-ant-...
```

## Schritt 1: Screenshots auswerten

Empfohlene Screenshots (je ein Bild pro Bildschirm, Zahlen gut lesbar):

1. **Truppenübersicht** – Menge und Tier pro Truppentyp
2. **Mauer → Verteidigungs-Stats** – Buffs gesamt (Defense/HP in %)
3. **Mauergeneral** – Level, Sterne, Skills
4. **Stadtübersicht** – Schloss- und Mauerstufe
5. Optional: Lazarett, Forschung (Verteidigungsbaum), Ressourcen, Fallen

```bash
npm run extract -- screenshots/truppen.png screenshots/mauer-stats.png screenshots/general.png
```

Das Ergebnis landet in `stats.json`. **Diese Datei vor Schritt 2 prüfen** – das Tool listet unsichere Werte explizit auf; korrigiere sie direkt in der Datei. Nicht sichtbare Werte stehen auf `null` und werden in der Strategie als unbekannt behandelt.

## Schritt 2: Strategie erzeugen

Optional kannst du Scout-Reports oder Profile potenzieller Angreifer mitgeben:

```bash
npm run advise -- stats.json
npm run advise -- stats.json scout-report.png
```

Der Bericht wird live angezeigt und als `strategie.md` gespeichert. Er enthält:

1. **Lagebewertung** – effektive Verteidigungsstärke und größte Schwachstelle
2. **Bedrohungsanalyse** – Kräfteverhältnis und Truppentyp-Matchup
3. **Empfohlene Strategie** – eine Hauptstrategie (Schild / leeres Lager / Mauerverteidigung / aktive Verteidigung) mit nummerierten, manuell umsetzbaren Schritten
4. **Ausbau-Roadmap** – die 5 wirksamsten nächsten Verbesserungen, priorisiert

## Kosten

`claude-fable-5` kostet 10 $/M Input- und 50 $/M Output-Token. Ein Durchlauf (3–5 Screenshots + Bericht) liegt typischerweise im Bereich weniger Cent bis ~0,50 $.
