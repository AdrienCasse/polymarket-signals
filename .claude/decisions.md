# Décisions — polymarket-signals

### 2026-10-14 — Stack data : bronze en fichiers + DuckDB + dbt
**Contexte :** Besoin d'un pipeline personnel propre, testable hors ligne, à coût nul, qui serve aussi de support pédagogique.
**Décision :** Bronze = JSONL gzip partitionné Hive (immuable, empreinte sha256) ; DuckDB fichier comme entrepôt jetable ; dbt-duckdb pour silver/gold avec tests et contrat sur le mart de sortie.
**Raison :** Le brut rejouable est la seule source de vérité, et tout le reste se reconstruit en quelques secondes. dbt apporte tests, lignage et docs. Supabase/Postgres écarté pour l'instant : pas de multi-utilisateur, l'export vers fintrack se fera depuis gold.

### 2026-10-14 — Lecture seule par construction
**Contexte :** Polymarket est interdit en France (ANJ) ; décision fintrack du 2026-10-13 : pas de spéculation.
**Décision :** Un seul client HTTP (`ReadOnlyClient`, GET uniquement, liste blanche, TLS vérifié, sans redirection). Aucune clé, aucun wallet, aucune bibliothèque de trading, aucun MCP tiers transactionnel.
**Raison :** Le pire scénario de fuite est « rien ». La contrainte est testée (`test_only_get_is_exposed`).

### 2026-10-14 — Watchlist = seed dbt unique
**Contexte :** L'ingestion et dbt ont besoin tous les deux de la liste des thèmes et sélecteurs.
**Décision :** `transform/seeds/watchlist_selectors.csv` (+ `themes.csv`) est lu par Python ET chargé par dbt.
**Raison :** Une seule source de vérité, éditable, versionnée et testée (`assert_watchlist_themes_exist`).

### 2026-10-14 — Probabilité implicite = règle d'affichage de Polymarket
**Décision :** Point milieu si écart ≤ 0,10, sinon dernier prix échangé (macro `implied_probability`, test unitaire dbt). Qualité du signal en 3 niveaux, avec seuils en variables dbt et raisons explicites.
**Raison :** Reproduire ce que voit l'utilisateur, et rendre visible pourquoi un chiffre est fiable ou non.

### 2026-10-14 — Agents : mesurer les biais, pas conseiller des paris
**Contexte :** Idée d'agents « best tips pour bet » et de profilage des biais Polymarket.
**Décision :** Agents en lecture seule sur la couche gold : `macro-tutor` (pédagogie) et `bias-analyst` (calibration, Brier, biais favori/outsider mesurés sur les marchés résolus). Pas d'agent de pari. MCP maison lecture seule (roadmap v0.4) plutôt qu'un MCP communautaire.
**Raison :** Cohérent avec le cadre légal et la stratégie passive. La calibration mesurée est plus solide (et plus formatrice) qu'un biais supposé.

### 2026-10-15 — Site statique GitHub Pages + bronze sur branche git `data`
**Contexte :** Web app voulue, coût zéro, fiable et sécurisée, 80/20 ; ingestion impossible depuis la France (DNS ANJ).
**Décision :** Next.js en export statique sur GitHub Pages (OIDC, aucun secret) ; ingestion quotidienne en GitHub Actions ; bronze versionné sur une branche orpheline `data` ; export gold → JSON seulement si tous les tests dbt passent.
**Raison :** Aucun serveur ni base exposés, 0 €, zéro compte tiers. Le site garde toujours la dernière version saine. Vercel écarté (token de déploiement nécessaire), stockage objet écarté (compte + secret).
