# Feuille de route

## ✅ v0.1 : socle (2026-10-14)

- Ingestion lecture seule (Gamma + CLOB), bronze idempotent, manifestes de run
- dbt silver/gold, 60 tests (génériques, singuliers, unitaire, contrat appliqué)
- CLI pédagogique : `watchlist`, `explain`, `doctor`, `tags`, `runs`, `contracts`
- Académie : 7 leçons ; documentation ; CI = `make check`

## ✅ v0.2 : site web et pipeline quotidien (2026-10-15)

- Site statique Next.js (tableau de bord, page marché en 4 temps, Académie avec simulateur,
  « Sous le capot ») publié sur GitHub Pages
- Pipeline GitHub Actions quotidien : ingestion live → branche `data` → dbt build → export → déploiement
- Reste : premier run réel, confirmer les slugs de tags, ajuster les contrats si l'API diffère

## v0.3 : calibration et biais (cœur data science)

L'objectif est de **mesurer** les biais de Polymarket au lieu de les supposer.

- Ingestion des marchés **résolus** (`closed=true`) avec leur issue gagnante
- Modèles gold :
  - `fct_resolved_markets` : prix à J-30, J-7, J-1 avant résolution, résultat (0/1), domaine
  - `mart_calibration` : par tranche de prix × domaine × horizon, probabilité moyenne affichée
    contre fréquence observée, effectif, intervalle de confiance (Wilson)
  - score de Brier et sa décomposition (fiabilité, résolution, incertitude)
- Leçon 07 : « Polymarket est-il bien calibré ? », avec **nos** chiffres (courbe de
  calibration)
- Utilisation : corriger l'affichage (« 5 % affiché ≈ x % observé historiquement ») et
  pondérer `signal_quality`

## v0.4 : agents, en lecture seule

Principe : les agents raisonnent **sur la couche gold testée**, jamais sur des données brutes,
et n'ont **aucun outil d'écriture**.

| Agent | Rôle | Sources | Ne fait jamais |
|---|---|---|---|
| `macro-tutor` | expliquer un marché, répondre « pourquoi ça bouge ? » | `mart_macro_watchlist`, `academy/` | recommander une action |
| `bias-analyst` | profiler les biais : calibration, marchés minces, horizon, domaine | `mart_calibration`, `fct_*` | conseiller un pari |
| (fintrack) `behavior-coach` | repérer **tes** biais de comportement (dépenses impulsives, réaction aux baisses, procrastination de l'épargne) | marts fintrack | toucher aux comptes |

Les définitions de `macro-tutor` et `bias-analyst` sont dans `.claude/agents/`.

- **Serveur MCP maison, lecture seule** (`polysignals mcp`) : outils `watchlist`,
  `explain_market`, `calibration`, branché sur DuckDB en `read_only`. Préféré aux MCP
  communautaires, dont plusieurs manipulent des clés privées et passent des ordres.

## v0.5 : intégration fintrack

- Export du contrat `mart_macro_watchlist` vers Supabase (table en lecture seule, RLS), ou
  lecture d'un fichier Parquet publié
- Encart « contexte macro » dans le cockpit fintrack, lié à la leçon 05
- Le lien avec l'Académie fintrack : biais de marché (ici) ↔ biais personnels (fintrack)

## Hors périmètre, définitivement

Passer des ordres, conseiller des paris, gérer un wallet. Voir `security.md` et
`academy/06-cadre-legal-france.md`.
