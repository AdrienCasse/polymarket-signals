import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import type { ReactNode } from "react";

import { Change } from "@/components/Change";
import { OrderBook } from "@/components/OrderBook";
import { PriceChart } from "@/components/PriceChart";
import { QualityBadge } from "@/components/QualityBadge";
import { getGold, getMarket } from "@/lib/data";
import { date, isNoise, PASSIVE_INVESTOR_NOTE, pct, price, usd } from "@/lib/format";

export const dynamicParams = false;

export function generateStaticParams() {
  return getGold().markets.map((m) => ({ slug: m.market_slug }));
}

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const m = getMarket((await params).slug);
  return { title: m?.question ?? "Marché" };
}

const VERDICT = {
  solide: "Carnet profond et écart serré : le prix est difficile à déplacer. On peut le lire comme une estimation sérieuse.",
  fragile: "Le chiffre a un sens, mais il est fragile : à lire avec prudence et sans tirer de conclusion d'une petite variation.",
  inexploitable: "Le prix affiché ne mesure pas grand-chose : trop peu d'argent en jeu ou acheteurs et vendeurs trop éloignés.",
} as const;

export default async function MarketPage({ params }: Props) {
  const m = getMarket((await params).slug);
  if (!m) notFound();
  const p = m.implied_probability;

  return (
    <article className="max-w-3xl">
      <Link href="/" className="text-sm text-text-3 hover:text-text-1">← Tableau de bord</Link>
      <p className="mt-6 text-xs font-medium uppercase tracking-wider text-gold">{m.theme_label}</p>
      <h1 className="mt-2 text-2xl font-semibold leading-tight tracking-tight text-text-1 sm:text-3xl">{m.question}</h1>
      <p className="mt-2 text-sm text-text-3">{m.event_title}</p>

      <Step n={1} title="Ce que dit le marché">
        <p className="tabular text-5xl font-semibold text-gold">{pct(p)}</p>
        <p className="mt-3 text-text-2">
          Les participants estiment à <strong className="text-text-1">{pct(p)}</strong> la probabilité que la réponse soit
          « Oui ». Concrètement, une part « Oui » coûte {price(p)} et rapporte 1 $ si l&apos;événement se produit, 0 $
          sinon : <strong className="text-text-1">le prix est la probabilité implicite</strong>.
        </p>
        <div className="mt-6"><OrderBook bid={m.best_bid} ask={m.best_ask} last={m.last_trade_price} implied={p} /></div>
      </Step>

      <Step n={2} title="Comment ça a bougé">
        <div className="flex flex-wrap gap-x-6 gap-y-1">
          <Change value={m.change_7d} label="sur 7 jours" />
          <Change value={m.change_30d} label="sur 30 jours" />
          {m.min_90d != null && m.max_90d != null && (
            <span className="text-sm text-text-3">fourchette 90 j : {pct(m.min_90d)} → {pct(m.max_90d)}</span>
          )}
        </div>
        <div className="mt-4"><PriceChart series={m.series} /></div>
        {isNoise(m.change_7d) && (
          <p className="mt-3 text-sm text-text-3">Moins de 3 points en une semaine : cela relève souvent du bruit, pas d&apos;une information nouvelle.</p>
        )}
      </Step>

      <Step n={3} title="Peut-on s'y fier ?">
        <QualityBadge quality={m.signal_quality} />
        <p className="mt-3 text-text-2">{VERDICT[m.signal_quality]}</p>
        {m.quality_reasons.length > 0 && (
          <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-text-2">
            {m.quality_reasons.map((r) => <li key={r}>{r}</li>)}
          </ul>
        )}
        <dl className="mt-5 grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <Fact label="Liquidité" value={usd(m.liquidity_usd)} />
          <Fact label="Volume 24 h" value={usd(m.volume_24h_usd)} />
          <Fact label="Résolution" value={m.days_to_resolution != null ? `${date(m.end_at)} (J-${m.days_to_resolution})` : "n/d"} />
        </dl>
        {m.resolution_source && (
          <p className="mt-4 break-words text-sm text-text-3">
            Source de résolution : <span className="text-text-2">{m.resolution_source}</span>
          </p>
        )}
        <p className="mt-4 text-sm text-text-3">
          Rappel : un marché prédictif agrège des paris, pas des prévisions d&apos;experts. Il peut se tromper, et ses
          biais sont connus (<Link href="/academie/04-biais-et-limites/" className="text-gold underline underline-offset-2">leçon 04</Link>).
        </p>
      </Step>

      <Step n={4} title="Et pour toi ?">
        <p className="text-text-2">{m.why_it_matters}</p>
        <p className="mt-3 rounded-[10px] border border-line bg-sunken p-4 text-sm text-text-2">{PASSIVE_INVESTOR_NOTE}</p>
        <Link href={`/academie/${m.academy_lesson}/`} className="mt-4 inline-block text-sm text-gold underline underline-offset-2">
          Aller plus loin : lire un signal macro sans spéculer →
        </Link>
      </Step>
    </article>
  );
}

function Step({ n, title, children }: { n: number; title: string; children: ReactNode }) {
  return (
    <section className="mt-10 border-t border-line pt-8">
      <h2 className="mb-4 flex items-baseline gap-3 text-lg font-semibold text-text-1">
        <span className="tabular text-sm text-gold">{n}.</span>
        {title}
      </h2>
      {children}
    </section>
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
