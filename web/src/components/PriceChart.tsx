import { pct } from "@/lib/format";

/**
 * Probabilité de clôture quotidienne (SVG statique, aucune bibliothèque).
 * L'axe vertical est zoomé sur la plage observée, avec des repères lisibles.
 */
export function PriceChart({ series }: { series: [string, number][] }) {
  if (series.length < 2) {
    return <p className="text-sm text-text-3">Historique insuffisant pour tracer une courbe.</p>;
  }
  const W = 640;
  const H = 220;
  const pad = { l: 44, r: 12, t: 12, b: 28 };
  const values = series.map(([, p]) => p);
  const lo = Math.max(0, Math.min(...values) - 0.03);
  const hi = Math.min(1, Math.max(...values) + 0.03);
  const x = (i: number) => pad.l + (i / (series.length - 1)) * (W - pad.l - pad.r);
  const y = (p: number) => pad.t + (1 - (p - lo) / (hi - lo || 1)) * (H - pad.t - pad.b);
  const line = series.map(([, p], i) => `${x(i).toFixed(1)},${y(p).toFixed(1)}`).join(" ");
  const area = `${pad.l},${H - pad.b} ${line} ${x(series.length - 1)},${H - pad.b}`;
  const ticks = [lo, (lo + hi) / 2, hi];
  const fmtDay = (d: string) => new Date(d).toLocaleDateString("fr-FR", { day: "numeric", month: "short", timeZone: "UTC" });
  const first = series[0]!;
  const last = series[series.length - 1]!;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="h-auto w-full" role="img"
      aria-label={`Probabilité du ${fmtDay(first[0])} (${pct(first[1])}) au ${fmtDay(last[0])} (${pct(last[1])})`}>
      <defs>
        <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="var(--color-gold)" stopOpacity="0.18" />
          <stop offset="100%" stopColor="var(--color-gold)" stopOpacity="0" />
        </linearGradient>
      </defs>
      {ticks.map((t) => (
        <g key={t}>
          <line x1={pad.l} x2={W - pad.r} y1={y(t)} y2={y(t)} stroke="var(--color-line)" />
          <text x={pad.l - 8} y={y(t) + 4} textAnchor="end" fontSize="11" fill="var(--color-text-3)">{pct(t)}</text>
        </g>
      ))}
      <polygon points={area} fill="url(#area)" />
      <polyline points={line} fill="none" stroke="var(--color-gold)" strokeWidth="2" strokeLinejoin="round" />
      <circle cx={x(series.length - 1)} cy={y(last[1])} r="3.5" fill="var(--color-gold)" />
      <text x={pad.l} y={H - 8} fontSize="11" fill="var(--color-text-3)">{fmtDay(first[0])}</text>
      <text x={W - pad.r} y={H - 8} textAnchor="end" fontSize="11" fill="var(--color-text-3)">{fmtDay(last[0])}</text>
    </svg>
  );
}
