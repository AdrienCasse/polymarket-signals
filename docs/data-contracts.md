# Contrats de données

Trois niveaux de garantie, du plus en amont au plus en aval.

## 1. Contrat source (pydantic, à l'ingestion)

`src/polysignals/models.py`. Chaque enregistrement est validé **sans être rejeté** : la réponse
brute est toujours conservée, et le verdict voyage avec elle (`contract_ok`,
`contract_errors`).

| Flux | Modèle | Exigences principales |
|---|---|---|
| `gamma.events` | `GammaEvent` | `id`, `slug`, `title`, `active`, `closed` ; marchés valides |
| (imbriqué) | `GammaMarket` | `outcomes` et `outcomePrices` décodables, prix dans [0, 1] |
| `clob.prices_history` | `ClobPriceHistory` | `history[].t` > 0, `history[].p` dans [0, 1] |

Les champs inconnus sont **acceptés** (l'API peut s'enrichir). Un champ attendu manquant ou mal
typé est une violation. Le test dbt `assert_no_contract_violations` échoue alors, et
`make contracts` liste le détail.

## 2. Enveloppe bronze (schéma fixe)

Une ligne JSON par enregistrement, fichiers `bronze/<source>/<endpoint>/dt=YYYY-MM-DD/<run_id>.jsonl.gz`.

| Champ | Type | Rôle |
|---|---|---|
| `record_id` | sha256 hex | `sha256(source ␟ endpoint ␟ clé ␟ payload canonique)` : idempotence |
| `run_id` | texte | `AAAAMMJJTHHMMSSZ-xxxxxx` |
| `ingested_at` | ISO 8601 UTC | instant de l'ingestion (= instantané) |
| `source`, `endpoint` | texte | `gamma/events`, `clob/prices_history` |
| `record_key` | texte | clé métier (id d'événement, id de token) |
| `params` | objet | paramètres de la requête |
| `contract_ok`, `contract_errors` | booléen, liste | verdict du contrat source |
| `payload` | JSON | réponse brute, **jamais modifiée** |

Payload canonique = JSON trié par clés, sans espaces : la même donnée donne toujours la même
empreinte.

## 3. Contrat de sortie (dbt, `mart_macro_watchlist`)

`contract: {enforced: true}` dans `transform/models/marts/_marts.yml` : noms et types des
colonnes sont vérifiés à **chaque** build. Toute modification qui casse le schéma échoue avant
d'atteindre un consommateur (CLI, fintrack, MCP).

Tests de données associés : unicité du grain (`market_id`, `theme_id`), probabilité dans
[0, 1], `signal_quality` dans {solide, fragile, inexploitable}.

### Changer le contrat de sortie

1. Ajouter la colonne au modèle **et** au YAML (type explicite).
2. Si un consommateur existe, ajouter plutôt que renommer ; une suppression = nouvelle version
   du mart (`mart_macro_watchlist_v2`) et période de transition.
