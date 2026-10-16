import type { Metadata } from "next";

import { ArchitectureDiagram } from "@/components/ArchitectureDiagram";
import { getGold } from "@/lib/data";
import { dateTime } from "@/lib/format";
import { REPO_URL } from "@/lib/site";

export const metadata: Metadata = { title: "Sous le capot" };

const PRINCIPLES = [
  ["Lecture seule par construction", "Un seul client HTTP, qui ne sait faire que des GET vers deux hôtes autorisés, TLS vérifié, sans redirection. Aucune clé, aucun wallet."],
  ["Le brut est sacré", "Chaque réponse d'API est stockée telle quelle, avec une empreinte qui rend l'ingestion idempotente. Tout le reste se reconstruit."],
  ["Rien n'est publié sans tests", "Contrats de données à l'arrivée, tests dbt sur chaque couche, contrat de schéma sur la table finale. Un test rouge = pas de mise à jour du site."],
  ["Coût zéro, surface minimale", "GitHub Actions planifié + pages statiques. Pas de serveur, pas de base exposée, pas de secret de déploiement (OIDC)."],
] as const;

export default function UnderTheHood() {
  const gold = getGold();
  const t = gold.tests;
  return (
    <div className="max-w-3xl">
      <h1 className="text-3xl font-semibold tracking-tight text-text-1">Sous le capot</h1>
      <p className="mt-3 text-[15px] leading-relaxed text-text-2">
        Comment les chiffres de ce site sont produits, vérifiés et publiés, chaque jour, automatiquement.
      </p>

      <ArchitectureDiagram />

      <section className="mt-10 grid gap-3 sm:grid-cols-3">
        <Stat label="Tests de données au dernier build" value={t ? `${t.pass}/${t.tests}` : "n/d"} tone={t && t.pass === t.tests ? "text-teal" : "text-amber"} />
        <Stat label="Avertissements" value={t ? String(t.warn) : "n/d"} tone={t?.warn ? "text-amber" : "text-text-1"} />
        <Stat label="Marchés suivis" value={String(gold.markets.length)} tone="text-gold" />
      </section>

      <section className="mt-12">
        <h2 className="text-lg font-semibold text-text-1">Derniers runs d&apos;ingestion</h2>
        <div className="mt-4 overflow-x-auto rounded-[var(--radius-card)] border border-line">
          <table className="w-full text-sm">
            <thead className="bg-card text-left text-text-3">
              <tr>
                <th className="px-4 py-2 font-medium">Début</th>
                <th className="px-4 py-2 font-medium">Mode</th>
                <th className="px-4 py-2 font-medium">Statut</th>
                <th className="px-4 py-2 text-right font-medium">Nouveaux</th>
                <th className="px-4 py-2 text-right font-medium">Déjà vus</th>
              </tr>
            </thead>
            <tbody>
              {gold.runs.slice(0, 10).map((r) => (
                <tr key={r.run_id} className="border-t border-line">
                  <td className="px-4 py-2 text-text-2">{dateTime(r.started_at)}</td>
                  <td className="px-4 py-2 text-text-2">{r.mode}</td>
                  <td className={`px-4 py-2 ${r.status === "success" ? "text-teal" : "text-red"}`}>{r.status}</td>
                  <td className="tabular px-4 py-2 text-right text-text-1">{r.written}</td>
                  <td className="tabular px-4 py-2 text-right text-text-3">{r.skipped}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-xs text-text-3">« Déjà vus » : enregistrements identiques à un run précédent, non réécrits (idempotence).</p>
      </section>

      <section className="mt-12">
        <h2 className="text-lg font-semibold text-text-1">Principes</h2>
        <dl className="mt-4 grid gap-3 sm:grid-cols-2">
          {PRINCIPLES.map(([title, body]) => (
            <div key={title} className="rounded-[var(--radius-card)] border border-line bg-card p-4">
              <dt className="font-medium text-text-1">{title}</dt>
              <dd className="mt-1 text-sm text-text-2">{body}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-6 text-sm text-text-3">
          Stack : Python 3.12, httpx, pydantic, DuckDB, dbt, Next.js (export statique), GitHub Actions, GitHub Pages ·{" "}
          <a href={REPO_URL} className="text-gold underline underline-offset-2" rel="noopener noreferrer" target="_blank">code source et documentation</a>
        </p>
      </section>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="rounded-[var(--radius-card)] border border-line bg-card p-4">
      <p className={`tabular text-3xl font-semibold ${tone}`}>{value}</p>
      <p className="mt-1 text-sm text-text-3">{label}</p>
    </div>
  );
}
