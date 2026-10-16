import Link from "next/link";

import { dateTime } from "@/lib/format";
import { REPO_URL } from "@/lib/site";

const NAV = [
  { href: "/", label: "Tableau de bord" },
  { href: "/academie/", label: "Académie" },
  { href: "/sous-le-capot/", label: "Sous le capot" },
];

export function Header() {
  return (
    <header className="border-b border-line">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="text-base font-semibold tracking-tight text-text-1">polysignals</span>
          <span className="hidden text-xs text-text-3 sm:inline">comprendre ce que le monde anticipe</span>
        </Link>
        <nav aria-label="Navigation principale">
          <ul className="flex gap-1 text-sm">
            {NAV.map((n) => (
              <li key={n.href}>
                <Link href={n.href} className="rounded-md px-2.5 py-1.5 text-text-2 transition-colors hover:bg-hover hover:text-text-1">
                  {n.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}

export function Footer({ generatedAt }: { generatedAt: string }) {
  return (
    <footer className="mt-20 border-t border-line">
      <div className="mx-auto max-w-5xl space-y-2 px-4 py-8 text-xs leading-relaxed text-text-3 sm:px-6">
        <p>
          Site pédagogique en lecture seule. Données publiques des marchés prédictifs Polymarket, présentées
          à titre d&apos;information : <strong className="text-text-2">ni conseil financier, ni incitation à parier</strong>.
          Les paris sur Polymarket ne sont pas autorisés en France (ANJ).
        </p>
        <p>
          Données générées le {dateTime(generatedAt)} ·{" "}
          <a href={REPO_URL} className="underline underline-offset-2 hover:text-text-2" rel="noopener noreferrer" target="_blank">
            code source
          </a>
        </p>
      </div>
    </footer>
  );
}

export function DemoBanner() {
  return (
    <div className="border-b border-amber/20 bg-amber/10">
      <p className="mx-auto max-w-5xl px-4 py-2 text-xs text-amber sm:px-6">
        Démonstration : ces marchés sont <strong>synthétiques</strong> (formes réelles de l&apos;API, valeurs inventées).
      </p>
    </div>
  );
}
