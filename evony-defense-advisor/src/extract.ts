// Schritt 1: Spielerstatistiken aus Screenshots auslesen.
//
//   npm run extract -- screenshots/*.png
//
// Schreibt stats.json. Diese Datei vor dem Strategie-Schritt prüfen und
// falsch erkannte Werte von Hand korrigieren – das ist der Bestätigungsschritt.

import fs from "fs";
import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { PlayerStatsSchema } from "./schema.js";
import { loadImageBlocks } from "./images.js";

const MODEL = "claude-fable-5";
const OUTPUT_FILE = "stats.json";

const EXTRACTION_PROMPT = `Du bist ein Datenextraktions-Assistent für das Strategiespiel "Evony: The King's Return".

Lies aus den folgenden Screenshots alle verteidigungsrelevanten Spielerstatistiken aus:
Truppen (Typ, Tier, Anzahl), Schloss- und Mauerstufe, Fallen, Verteidigungs-Buffs,
Mauergeneral mit Skills, Lazarettkapazität, Märsche, Ressourcen, Forschung,
Allianzkontext und Schildstatus.

Regeln:
- Trage nur Werte ein, die tatsächlich in den Screenshots sichtbar sind. Alles andere: null bzw. leeres Array.
- Evony kürzt Zahlen ab (z.B. "1.2M" = 1200000, "850K" = 850000) – rechne in volle Zahlen um.
- Liste jeden Wert, bei dem du dir unsicher bist (unscharf, abgeschnitten, mehrdeutig), in uncertainValues auf.
- Deutsche und englische Spiel-UI sind beide möglich.`;

async function main() {
  const imagePaths = process.argv.slice(2);
  if (imagePaths.length === 0) {
    console.error("Verwendung: npm run extract -- <screenshot1.png> [screenshot2.png ...]");
    process.exit(1);
  }

  console.log(`Lese ${imagePaths.length} Screenshot(s) mit ${MODEL} aus ...`);

  const client = new Anthropic();
  const response = await client.messages.parse({
    model: MODEL,
    max_tokens: 16000,
    messages: [
      {
        role: "user",
        content: [
          ...loadImageBlocks(imagePaths),
          { type: "text", text: EXTRACTION_PROMPT },
        ],
      },
    ],
    output_config: {
      format: zodOutputFormat(PlayerStatsSchema),
    },
  });

  const stats = response.parsed_output;
  if (!stats) {
    console.error("Die Antwort konnte nicht als Statistik geparst werden. Rohantwort:");
    console.error(JSON.stringify(response.content, null, 2));
    process.exit(1);
  }

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(stats, null, 2));

  console.log(`\nErkannte Werte gespeichert in ${OUTPUT_FILE}:\n`);
  console.log(JSON.stringify(stats, null, 2));

  if (stats.uncertainValues.length > 0) {
    console.log("\n⚠ Unsichere Werte – bitte manuell prüfen:");
    for (const v of stats.uncertainValues) console.log(`  - ${v}`);
  }

  console.log(
    `\nNächster Schritt: ${OUTPUT_FILE} prüfen/korrigieren, dann:\n  npm run advise -- ${OUTPUT_FILE} [scout-report.png ...]`,
  );
}

main().catch((err) => {
  if (err instanceof Anthropic.APIError) {
    console.error(`API-Fehler ${err.status}: ${err.message}`);
  } else {
    console.error(err instanceof Error ? err.message : err);
  }
  process.exit(1);
});
