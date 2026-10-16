"use client";

import { useId, useState } from "react";

import { MIDPOINT_MAX_SPREAD, pct } from "@/lib/format";

/** Bac à sable : bouge acheteur, vendeur et dernier échange, et regarde quelle probabilité s'affiche. */
export function SpreadSimulator() {
  const [bid, setBid] = useState(0.58);
  const [ask, setAsk] = useState(0.62);
  const [last, setLast] = useState(0.55);
  const spread = Math.max(0, ask - bid);
  const usesMid = spread <= MIDPOINT_MAX_SPREAD;
  const shown = usesMid ? (bid + ask) / 2 : last;

  return (
    <section className="rounded-[var(--radius-card)] border border-gold/25 bg-gold-glow p-5">
      <p className="text-xs font-medium uppercase tracking-wider text-gold">À toi de jouer</p>
      <h2 className="mt-1 text-lg font-semibold text-text-1">Quelle probabilité s&apos;affiche ?</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        <Slider label="Meilleur acheteur" value={bid} onChange={(v) => setBid(Math.min(v, ask))} />
        <Slider label="Meilleur vendeur" value={ask} onChange={(v) => setAsk(Math.max(v, bid))} />
        <Slider label="Dernier échange" value={last} onChange={setLast} />
      </div>
      <div className="mt-5 flex flex-wrap items-baseline gap-x-4 gap-y-1">
        <span className="tabular text-4xl font-semibold text-gold">{pct(shown)}</span>
        <span className={`text-sm ${usesMid ? "text-teal" : "text-red"}`}>
          écart {(spread * 100).toFixed(0)} pts →{" "}
          {usesMid ? "point milieu" : "dernier échange (écart > 10 pts)"}
        </span>
      </div>
      <p className="mt-2 text-sm text-text-2">
        Écarte acheteur et vendeur au-delà de 10 points : le chiffre affiché saute sur le dernier échange.
        C&apos;est pourquoi un marché peu liquide peut afficher une probabilité qui ne mesure pas grand-chose.
      </p>
    </section>
  );
}

function Slider({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  const id = useId();
  return (
    <div>
      <label htmlFor={id} className="flex justify-between text-sm text-text-2">
        {label}
        <span className="tabular text-text-1">{value.toFixed(2)} $</span>
      </label>
      <input
        id={id}
        type="range"
        min={0.01}
        max={0.99}
        step={0.01}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="mt-2 w-full accent-[var(--color-gold)]"
      />
    </div>
  );
}
