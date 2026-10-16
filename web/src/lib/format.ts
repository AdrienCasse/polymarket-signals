// Mise en forme FR. Les fonctions ne lèvent jamais : une donnée absente s'affiche « n/d ».

const nf0 = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 });
const nf2 = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export const pct = (p: number | null | undefined) => (p == null ? "n/d" : `${nf0.format(p * 100)} %`);

export const pts = (d: number | null | undefined) => {
  if (d == null) return "n/d";
  const v = d * 100;
  const sign = v > 0 ? "+" : v < 0 ? "−" : "±";
  return `${sign}${Math.abs(v).toLocaleString("fr-FR", { maximumFractionDigits: 1 })} pts`;
};

export const usd = (x: number | null | undefined) => (x == null ? "n/d" : `${nf0.format(x)} $`);

export const price = (x: number | null | undefined) => (x == null ? "n/d" : `${nf2.format(x)} $`);

export const date = (iso: string | null | undefined) =>
  iso == null
    ? "n/d"
    : new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

export const dateTime = (iso: string | null | undefined) =>
  iso == null
    ? "n/d"
    : `${new Date(iso).toLocaleString("fr-FR", {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
      })} UTC`;

/** Écart de moins de 3 points : relève souvent du bruit (cf. leçon 02). */
export const isNoise = (d: number | null | undefined) => d != null && Math.abs(d) < 0.03;

export const MIDPOINT_MAX_SPREAD = 0.1;

export const PASSIVE_INVESTOR_NOTE =
  "Ce signal n'appelle aucune action sur ton épargne : une stratégie passive (épargne de précaution, " +
  "livrets, PEA en DCA) ne se pilote pas sur des probabilités de court terme. Il sert à comprendre le " +
  "contexte, par exemple pourquoi les marchés bougent ou pourquoi le taux du Livret A pourrait changer.";

export function hoursSince(iso: string | null | undefined, now: Date): number | null {
  if (!iso) return null;
  return (now.getTime() - new Date(iso).getTime()) / 3_600_000;
}
