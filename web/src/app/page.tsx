import Link from "next/link";

import { Change } from "@/components/Change";
import { Freshness } from "@/components/Freshness";
import { QualityBadge } from "@/components/QualityBadge";
import { Sparkline } from "@/components/Sparkline";
import { type EventHeadline, getGold, type Market, themeViews } from "@/lib/data";
import { pct } from "@/lib/format";

export default function Dashboard() {
  const gold = getGold();
  const lastSuccess = gold.runs.find((r) => r.status === "success")?.finished_at ?? null;

  return (
    <>
      <section className="max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight text-text-1 sm:text-4xl">Ce que le monde anticipe</h1>
        <p className="mt-3 text-[15px] leading-relaxed text-text-2">
          Les probabilités que les marchés prédictifs attribuent aux grands événements macro, avec, pour
          chacune, <strong className="text-text-1">ce qu&apos;elle vaut vraiment</strong>. Pour comprendre le
          contexte de ton épargne, jamais pour parier.
        </p>
        <div className="mt-4"><Freshness lastSuccessAt={lastSuccess} /></div>
      </section>

      <aside className="mt-8 grid gap-3 rounded-[var(--radius-card)] border border-line bg-card p-4 text-sm text-text-2 sm:grid-cols-3">
        <p><strong className="text-text-1">62 %</strong> = une part « Oui » s&apos;échange 0,62 $ et paie 1 $ si l&apos;événement arrive.{" "}
          <Link href="/academie/01-prix-probabilite/" className="text-gold underline underline-offset-2">Leçon 01</Link></p>
        <p>Le badge dit si le chiffre est <strong className="text-text-1">fiable</strong> : écart achat/vente, liquidité, échéance.{" "}
          <Link href="/academie/02-carnet-ordres-liquidite/" className="text-gold underline underline-offset-2">Leçon 02</Link></p>
        <p>Une variation <strong className="text-text-1">grisée</strong> fait moins de 3 points : souvent du bruit, pas une information.</p>
      </aside>

      {themeViews().map(({ theme, headlines, markets }) => (
        <section key={theme.theme_id} className="mt-12" aria-labelledby={`t-${theme.theme_id}`}>
          <h2 id={`t-${theme.theme_id}`} className="text-lg font-semibold text-text-1">{theme.theme_label}</h2>
          <p className="mt-1 max-w-3xl text-sm text-text-3">{theme.why_it_matters}</p>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {headlines.map((h) => <HeadlineCard key={h.event_title} h={h} />)}
          </ul>
          <details className="mt-3 text-sm">
            <summary className="cursor-pointer text-text-3 hover:text-text-1">
              Tous les marchés du thème ({markets.length})
            </summary>
            <ul className="mt-3 divide-y divide-line rounded-[var(--radius-card)] border border-line">
              {[...markets].sort((a, b) => (b.liquidity_usd ?? 0) - (a.liquidity_usd ?? 0)).map((m) => (
                <MarketRow key={m.market_id} m={m} />
              ))}
            </ul>
          </details>
        </section>
      ))}

      {gold.markets.length === 0 && (
        <p className="mt-12 text-text-2">Aucun marché ouvert dans la watchlist pour le moment.</p>
      )}
    </>
  );
}

function HeadlineCard({ h }: { h: EventHeadline }) {
  const m = h.lead;
  const dim = m.signal_quality === "inexploitable";
  return (
    <li>
      <Link
        href={`/marches/${m.market_slug}/`}
        className="group flex h-full flex-col rounded-[var(--radius-card)] border border-line bg-card p-4 transition-colors hover:border-line-hi hover:bg-hover"
      >
        <p className="text-xs text-text-3">
          {h.event_title}
          {h.outcomes > 1 ? ` · issue la plus probable sur ${h.outcomes}` : ""}
        </p>
        <p className="mt-1 text-[15px] leading-snug text-text-1">{m.question}</p>
        <div className="mt-4 flex items-end justify-between gap-3">
          <div>
            <p className={`tabular text-3xl font-semibold ${dim ? "text-text-3 line-through decoration-1" : "text-gold"}`}>
              {pct(m.implied_probability)}
            </p>
            <Change value={m.change_7d} label="sur 7 j" />
          </div>
          <Sparkline values={m.series.map(([, p]) => p)} />
        </div>
        <div className="mt-4 flex items-center justify-between">
          <QualityBadge quality={m.signal_quality} />
          <span className="text-xs text-text-3 group-hover:text-gold">Comprendre →</span>
        </div>
      </Link>
    </li>
  );
}

function MarketRow({ m }: { m: Market }) {
  return (
    <li>
      <Link href={`/marches/${m.market_slug}/`} className="flex items-center justify-between gap-4 px-4 py-2.5 hover:bg-hover">
        <span className="text-text-2">{m.question}</span>
        <span className="flex shrink-0 items-center gap-3">
          <span className={`tabular ${m.signal_quality === "inexploitable" ? "text-text-3" : "text-text-1"}`}>
            {pct(m.implied_probability)}
          </span>
          <QualityBadge quality={m.signal_quality} />
        </span>
      </Link>
    </li>
  );
}
