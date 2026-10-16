import "server-only";

import { readFileSync } from "node:fs";
import path from "node:path";

/**
 * Contrat avec le pipeline : `web/data/gold.json`, produit par `polysignals export` (schema_version 1)
 * uniquement après un `dbt build` réussi. Lu au BUILD : le site publié ne fait aucun appel réseau.
 */

export type SignalQuality = "solide" | "fragile" | "inexploitable";

export interface Market {
  market_id: string;
  theme_id: string;
  theme_label: string;
  event_title: string;
  question: string;
  market_slug: string;
  implied_probability: number;
  change_7d: number | null;
  change_30d: number | null;
  min_90d: number | null;
  max_90d: number | null;
  best_bid: number | null;
  best_ask: number | null;
  spread: number | null;
  last_trade_price: number | null;
  liquidity_usd: number | null;
  volume_24h_usd: number | null;
  end_at: string | null;
  days_to_resolution: number | null;
  signal_quality: SignalQuality;
  quality_reasons: string[];
  resolution_source: string | null;
  why_it_matters: string;
  academy_lesson: string;
  as_of: string;
  series: [string, number][];
}

export interface Theme {
  theme_id: string;
  theme_label: string;
  why_it_matters: string;
  academy_lesson: string;
}

export interface Run {
  run_id: string;
  mode: "live" | "fixtures";
  status: "success" | "failed" | "running";
  started_at: string;
  finished_at: string | null;
  written: number;
  skipped: number;
}

export interface TestSummary {
  generated_at: string | null;
  tests: number;
  nodes: number;
  pass: number;
  warn: number;
  error: number;
  fail: number;
  skipped: number;
}

export interface Gold {
  schema_version: 1;
  generated_at: string;
  source_mode: "live" | "fixtures" | null;
  runs: Run[];
  tests: TestSummary | null;
  themes: Theme[];
  markets: Market[];
}

let cache: Gold | null = null;

export function getGold(): Gold {
  if (cache) return cache;
  const file = path.join(process.cwd(), "data", "gold.json");
  let raw: string;
  try {
    raw = readFileSync(file, "utf8");
  } catch {
    throw new Error(`${file} introuvable : lance \`make web-data\` (ou \`make demo\` puis \`polysignals export\`).`);
  }
  const gold = JSON.parse(raw) as Gold;
  if (gold.schema_version !== 1) {
    throw new Error(`schema_version ${String(gold.schema_version)} non supportée (attendu : 1)`);
  }
  cache = gold;
  return gold;
}

export function getMarket(slug: string): Market | undefined {
  return getGold().markets.find((m) => m.market_slug === slug);
}

export interface EventHeadline {
  event_title: string;
  /** Issue la plus probable parmi les marchés lisibles de l'événement (sinon, parmi tous). */
  lead: Market;
  outcomes: number;
  liquidity_usd: number;
}

export interface ThemeView {
  theme: Theme;
  headlines: EventHeadline[];
  markets: Market[];
}

/**
 * Vue « à la une » : un événement = une carte, montrant son issue la plus probable.
 * Pourquoi pas les marchés les plus liquides ? Sur les données réelles, la liquidité se
 * concentre sur des issues très improbables (0,2 %) : on afficherait surtout ce qui n'arrivera pas.
 */
export function themeViews(maxEvents = 6): ThemeView[] {
  const gold = getGold();
  return gold.themes
    .map((theme) => {
      const markets = gold.markets.filter((m) => m.theme_id === theme.theme_id);
      const byEvent = new Map<string, Market[]>();
      for (const m of markets) byEvent.set(m.event_title, [...(byEvent.get(m.event_title) ?? []), m]);
      const headlines = [...byEvent.entries()]
        .map(([event_title, ms]) => {
          const readable = ms.filter((m) => m.signal_quality !== "inexploitable");
          const pool = readable.length ? readable : ms;
          const lead = pool.reduce((a, b) => (b.implied_probability > a.implied_probability ? b : a));
          return {
            event_title,
            lead,
            outcomes: ms.length,
            liquidity_usd: ms.reduce((sum, m) => sum + (m.liquidity_usd ?? 0), 0),
          };
        })
        .sort((a, b) => b.liquidity_usd - a.liquidity_usd)
        .slice(0, maxEvents);
      return { theme, headlines, markets };
    })
    .filter((v) => v.markets.length > 0);
}
