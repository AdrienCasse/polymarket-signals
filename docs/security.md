# Sécurité

## Principe : rien à voler, rien à exécuter

Le projet est en **lecture seule par construction**, et le site est **statique** : pas de
serveur, pas de base, pas de compte, pas de cookie. Il ne contient, ne demande et ne manipule
**aucun secret** : pas de clé d'API, pas de clé privée, pas de wallet, pas de signature. Une
fuite complète du dépôt ou de la machine n'expose aucun fonds ni aucun compte.

## Garde-fous techniques

| Risque | Mesure | Où |
|---|---|---|
| Écrire sur la plateforme (ordre, transaction) | le client n'expose que `get_json` ; aucune bibliothèque de trading en dépendance | `http.py`, test `test_only_get_is_exposed` |
| Appeler un autre hôte (SSRF, fuite) | liste blanche dérivée de la config, HTTPS obligatoire | `http.py`, tests dédiés |
| Être redirigé ailleurs | `follow_redirects=False`, redirection = erreur | `http.py` |
| Interception / mauvais serveur | TLS **toujours** vérifié, jamais désactivable | `http.py`, `make doctor` |
| Réponse énorme (mémoire) | taille maximale (10 Mo par défaut), lecture en flux | `http.py` |
| Bannissement / surcharge de l'API | ≈ 4 requêtes/s max, backoff exponentiel + jitter, `Retry-After` respecté | `http.py` |
| Données malformées | contrats pydantic + tests dbt, brut conservé | `models.py`, `transform/tests/` |
| Dépendance vulnérable | `pip-audit` dans `make check` (CI), Dependabot hebdomadaire | `Makefile`, `.github/` |
| Fuite de données locales | `data/` et `.env*` gitignorés | `.gitignore` |
| CI compromise | `permissions: contents: read` par défaut, droits accordés **par job** (écriture limitée au job qui pousse `data`) | `.github/workflows/` |
| Secret de déploiement volé | aucun : GitHub Pages via OIDC (`id-token: write` sur le seul job de déploiement) | `pipeline.yml` |
| Publication d'une donnée fausse | l'export refuse si un test dbt a échoué ou si le site serait vide ; le site garde la dernière version saine | `export.py` |
| Script tiers / XSS sur le site | site statique, CSP stricte en `<meta>` (aucune ressource externe), Markdown sans HTML brut, aucun formulaire | `web/src/app/layout.tsx` |
| Paquet npm malveillant | versions exactes, `npm ci --ignore-scripts`, `npm audit` dans `make check` | `Makefile`, `web/package.json` |

## Textes de marché et LLM (pour la suite)

Les questions, descriptions et règles de résolution sont rédigées par des tiers. Si un agent
LLM les lit (MCP, conseiller), elles sont des **données non fiables** : risque d'injection de
prompt. Règles pour la suite :

- l'agent ne reçoit que des colonnes gold, jamais de HTML ni de payload brut ;
- aucun outil d'écriture n'est exposé à l'agent ;
- les textes sont balisés comme « contenu externe » dans le prompt.

## Ce qui ne sera jamais ajouté

- bibliothèque de trading (`py-clob-client` ou équivalent), clé privée, wallet ;
- désactivation de la vérification TLS ;
- serveur MCP tiers capable de passer des ordres.
