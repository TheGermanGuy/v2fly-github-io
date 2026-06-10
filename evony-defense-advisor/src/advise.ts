// Schritt 2: Verteidigungsstrategie aus den bestätigten Statistiken erzeugen.
//
//   npm run advise -- stats.json [scout-report1.png scout-report2.png ...]
//
// Optionale Screenshots: Scout-Reports oder Profile potenzieller Angreifer.
// Der Bericht wird gestreamt angezeigt und als strategie.md gespeichert.

import fs from "fs";
import Anthropic from "@anthropic-ai/sdk";
import { PlayerStatsSchema } from "./schema.js";
import { loadImageBlocks } from "./images.js";

const MODEL = "claude-fable-5";
const OUTPUT_FILE = "strategie.md";

const SYSTEM_PROMPT = `Du bist ein erfahrener Verteidigungsberater für das Strategiespiel "Evony: The King's Return".
Du erhältst die vom Spieler bestätigten Statistiken seines Accounts als JSON, optional ergänzt um
Screenshots von Scout-Reports oder Profilen potenzieller Angreifer.

Erstelle einen Verteidigungsbericht auf Deutsch, im Markdown-Format, mit genau dieser Struktur:

# Verteidigungsanalyse

## 1. Lagebewertung
Effektive Verteidigungsstärke einschätzen: Truppenmix nach Typ/Tier, Buffs, Mauergeneral,
Lazarettkapazität. Klar benennen, was die größte Schwachstelle ist (z.B. ungeschützte Ressourcen,
einseitiger Truppenmix, schwacher Mauergeneral, fehlende Buffs).

## 2. Bedrohungsanalyse
Falls Angreifer-Daten vorliegen: Kräfteverhältnis und Truppentyp-Matchup bewerten
(Bodentruppen/Berittene/Bogenschützen/Belagerung im Konter-Dreieck). Sonst: typische
Angreiferprofile für die Schlossstufe des Spielers annehmen und das wahrscheinlichste Szenario nennen.

## 3. Empfohlene Strategie
GENAU EINE Hauptstrategie wählen und begründen:
- Passiv (Schutzschild / Bubble)
- "Leeres Lager" (Truppen auslagern, Ressourcen unter Lagerschutz drücken)
- Harte Mauerverteidigung (Truppen in der Stadt, Angreifer ausbluten lassen)
- Aktive Verteidigung (Allianz-Verstärkungen, Buffs, Mauergeneral-Optimierung)
Danach: konkrete Schritte, die der Spieler MANUELL im Spiel umsetzt, als nummerierte Liste in
sinnvoller Reihenfolge. Jeder Schritt eine konkrete, sofort umsetzbare Aktion.

## 4. Ausbau-Roadmap
Die 5 wirksamsten nächsten Verbesserungen, priorisiert nach Verteidigungszuwachs pro Aufwand
(Forschung, Gebäude, Truppen-Tiers, General-Ausbau). Mit kurzer Begründung pro Punkt.

Regeln:
- Stütze dich nur auf die übergebenen Daten. Wo Werte fehlen (null), sage das ausdrücklich und
  nenne, welcher Screenshot die Lücke schließen würde – rate nicht.
- Keine Empfehlungen, die Automatisierung, Bots oder Drittsoftware erfordern. Alle Aktionen
  führt der Spieler selbst im Spiel aus.
- Konkret statt allgemein: Zahlen und Schwellenwerte nennen, wo die Daten es hergeben.`;

async function main() {
  const [statsFile, ...scoutImages] = process.argv.slice(2);
  if (!statsFile) {
    console.error("Verwendung: npm run advise -- stats.json [scout-report.png ...]");
    process.exit(1);
  }

  const stats = PlayerStatsSchema.parse(JSON.parse(fs.readFileSync(statsFile, "utf8")));

  const content: Anthropic.ContentBlockParam[] = [];
  if (scoutImages.length > 0) {
    content.push(
      { type: "text", text: "Screenshots potenzieller Angreifer (Scout-Reports/Profile):" },
      ...loadImageBlocks(scoutImages),
    );
  }
  content.push({
    type: "text",
    text: `Bestätigte Spielerstatistiken:\n\n${JSON.stringify(stats, null, 2)}`,
  });

  console.log(`Erzeuge Verteidigungsstrategie mit ${MODEL} ...\n`);

  const client = new Anthropic();
  const stream = client.messages.stream({
    model: MODEL,
    max_tokens: 32000,
    thinking: { type: "adaptive" },
    system: SYSTEM_PROMPT,
    messages: [{ role: "user", content }],
  });

  stream.on("text", (delta) => process.stdout.write(delta));

  const message = await stream.finalMessage();
  const report = message.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("");

  fs.writeFileSync(OUTPUT_FILE, report);
  console.log(`\n\nBericht gespeichert in ${OUTPUT_FILE}`);
}

main().catch((err) => {
  if (err instanceof Anthropic.APIError) {
    console.error(`API-Fehler ${err.status}: ${err.message}`);
  } else {
    console.error(err instanceof Error ? err.message : err);
  }
  process.exit(1);
});
