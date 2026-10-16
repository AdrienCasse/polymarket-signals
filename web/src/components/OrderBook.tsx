import { MIDPOINT_MAX_SPREAD, pct, price } from "@/lib/format";

/**
 * Le carnet d'ordres résumé sur une règle de 0 à 1 $ : meilleur acheteur, meilleur vendeur,
 * l'écart entre les deux, et le prix retenu comme probabilité.
 */
export function OrderBook({
  bid, ask, last, implied,
}: { bid: number | null; ask: number | null; last: number | null; implied: number }) {
  const hasBook = bid != null && ask != null;
  const spread = hasBook ? ask - bid : null;
  const usesMid = spread != null && spread <= MIDPOINT_MAX_SPREAD;
  const at = (p: number) => `${(p * 100).toFixed(2)}%`;

  return (
    <div>
      <div className="relative h-12">
        <div className="absolute inset-x-0 top-6 h-px bg-line-hi" />
        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <span
            key={t}
            className={`absolute top-8 whitespace-nowrap text-[11px] text-text-3 ${t === 0 ? "" : t === 1 ? "-translate-x-full" : "-translate-x-1/2"}`}
            style={{ left: at(t) }}
          >
            {t.toLocaleString("fr-FR")} $
          </span>
        ))}
        {hasBook && (
          <div
            className={`absolute top-[18px] h-3 rounded-sm ${usesMid ? "bg-teal/25" : "bg-red/25"}`}
            style={{ left: at(bid), width: at(ask - bid) }}
            title={`Écart : ${(ask - bid) * 100} pts`}
          />
        )}
        {hasBook && <Tick at={at(bid)} label="achat" tone="text-text-2" />}
        {hasBook && <Tick at={at(ask)} label="vente" tone="text-text-2" />}
        <div className="absolute top-3.5 size-5 -translate-x-1/2 rounded-full border-2 border-bg bg-gold" style={{ left: at(implied) }} />
      </div>
      <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
        <Fact label="Meilleur acheteur" value={price(bid)} />
        <Fact label="Meilleur vendeur" value={price(ask)} />
        <Fact label="Écart" value={spread == null ? "carnet vide" : `${(spread * 100).toLocaleString("fr-FR", { maximumFractionDigits: 1 })} pts`} />
        <Fact label="Dernier échange" value={price(last)} />
      </dl>
      <p className="mt-4 text-sm text-text-2">
        <span className="mr-1.5 inline-block size-2.5 rounded-full bg-gold align-middle" />
        Probabilité retenue : <strong className="text-text-1">{pct(implied)}</strong>
        {" — "}
        {usesMid
          ? "écart serré, on prend le point milieu entre acheteur et vendeur."
          : "écart trop large (ou carnet vide) : le point milieu ne veut rien dire, on prend le dernier prix échangé."}
      </p>
    </div>
  );
}

function Tick({ at, label, tone }: { at: string; label: string; tone: string }) {
  return (
    <span className={`absolute -top-1 -translate-x-1/2 text-[11px] ${tone}`} style={{ left: at }}>
      {label}
    </span>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-text-3">{label}</dt>
      <dd className="tabular text-text-1">{value}</dd>
    </div>
  );
}
