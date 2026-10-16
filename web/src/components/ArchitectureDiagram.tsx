const STEPS = [
  { title: "Sources", body: "API publiques Gamma et CLOB", note: "GET seulement · liste blanche · TLS" },
  { title: "Bronze", body: "JSON brut, immuable", note: "empreinte sha256 · idempotent" },
  { title: "Silver", body: "typé, aplati, dédupliqué", note: "dbt · vues" },
  { title: "Gold", body: "probabilité, variations, qualité", note: "contrat de schéma · 60 tests" },
  { title: "Ce site", body: "pages statiques", note: "publié seulement si tout est vert" },
];

export function ArchitectureDiagram() {
  return (
    <ol className="not-prose my-6 grid gap-2 sm:grid-cols-5" aria-label="Chaîne de traitement des données">
      {STEPS.map((s, i) => (
        <li key={s.title} className="relative rounded-[10px] border border-line bg-card p-3">
          <p className="text-[11px] font-medium uppercase tracking-wider text-gold">
            {i + 1}. {s.title}
          </p>
          <p className="mt-1 text-sm text-text-1">{s.body}</p>
          <p className="mt-1 text-xs text-text-3">{s.note}</p>
        </li>
      ))}
    </ol>
  );
}
