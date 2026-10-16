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

export function marketsByTheme(): { theme: Theme; markets: Market[] }[] {
  const gold = getGold();
  return gold.themes
    .map((theme) => ({ theme, markets: gold.markets.filter((m) => m.theme_id === theme.theme_id) }))
    .filter((group) => group.markets.length > 0);
}
