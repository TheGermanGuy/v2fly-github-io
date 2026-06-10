import { z } from "zod";

// Alle verteidigungsrelevanten Spielerstatistiken aus Evony: The King's Return.
// Felder sind nullable, weil nicht jeder Screenshot-Satz alle Werte zeigt –
// fehlende Werte werden im Strategie-Schritt als "unbekannt" behandelt.

export const TroopGroupSchema = z.object({
  type: z
    .enum(["ground", "mounted", "ranged", "siege"])
    .describe("Truppentyp: Bodentruppen, Berittene, Bogenschützen, Belagerungswaffen"),
  tier: z.number().describe("Truppen-Tier, z.B. 12 für T12"),
  count: z.number().describe("Anzahl der Truppen dieses Typs und Tiers"),
});

export const PlayerStatsSchema = z.object({
  keepLevel: z.number().nullable().describe("Schlossstufe (Keep Level)"),
  wallLevel: z.number().nullable().describe("Mauerstufe (Wall Level)"),
  power: z.number().nullable().describe("Gesamtmacht des Spielers"),

  troops: z
    .array(TroopGroupSchema)
    .describe("Alle sichtbaren Truppengruppen nach Typ und Tier"),
  traps: z
    .array(
      z.object({
        name: z.string().describe("Fallentyp"),
        count: z.number().describe("Anzahl"),
      }),
    )
    .describe("Fallen auf der Mauer"),

  buffs: z
    .object({
      groundDefensePct: z.number().nullable(),
      groundHpPct: z.number().nullable(),
      mountedDefensePct: z.number().nullable(),
      mountedHpPct: z.number().nullable(),
      rangedDefensePct: z.number().nullable(),
      rangedHpPct: z.number().nullable(),
      siegeDefensePct: z.number().nullable(),
      siegeHpPct: z.number().nullable(),
      inCityTroopDefensePct: z
        .number()
        .nullable()
        .describe("Genereller In-City-/Verteidigungs-Buff, falls als Gesamtwert angezeigt"),
    })
    .describe("Verteidigungs-Buffs in Prozent, wie im Buff-/Stats-Bildschirm angezeigt"),

  wallGeneral: z
    .object({
      name: z.string().nullable(),
      level: z.number().nullable(),
      stars: z.number().nullable().describe("Sterne/Aufstiegsstufe"),
      relevantSkills: z
        .array(z.string())
        .describe("Skills und Spezialisierungen mit Verteidigungsbezug"),
    })
    .nullable()
    .describe("Der auf der Mauer eingesetzte Verteidigungsgeneral"),

  hospitalCapacity: z.number().nullable().describe("Lazarett-/Hospitalkapazität"),
  marchCount: z.number().nullable().describe("Anzahl gleichzeitiger Märsche"),
  marchSize: z.number().nullable().describe("Maximale Marschgröße"),

  resources: z
    .object({
      food: z.number().nullable(),
      wood: z.number().nullable(),
      stone: z.number().nullable(),
      ore: z.number().nullable(),
      gold: z.number().nullable(),
      warehouseProtection: z
        .number()
        .nullable()
        .describe("Vom Lager geschützte Menge pro Ressource, falls sichtbar"),
    })
    .describe("Aktuelle Ressourcenbestände"),

  research: z
    .array(z.string())
    .describe(
      "Sichtbare verteidigungsrelevante Forschungen mit Stufe, z.B. 'Verteidigung Lv. 8'",
    ),

  alliance: z
    .object({
      inAlliance: z.boolean().nullable(),
      notes: z
        .string()
        .nullable()
        .describe("Allianz-Boni, Verstärkungsoptionen oder Allianz-Forschung, falls sichtbar"),
    })
    .describe("Allianzkontext"),

  shieldActive: z.boolean().nullable().describe("Ist aktuell ein Schutzschild (Bubble) aktiv?"),

  uncertainValues: z
    .array(z.string())
    .describe(
      "Werte, die schwer lesbar waren oder geschätzt wurden – zur manuellen Prüfung durch den Spieler",
    ),
  notes: z
    .string()
    .describe("Sonstige verteidigungsrelevante Beobachtungen aus den Screenshots"),
});

export type PlayerStats = z.infer<typeof PlayerStatsSchema>;
