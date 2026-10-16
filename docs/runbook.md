# Runbook

## Démarrage

```bash
make install     # uv sync
make demo        # pipeline complet hors ligne (données synthétiques, data-demo/) + tableau de bord
make web-demo    # le site sur ces données → http://localhost:3100
make explain M=ecb-cut-december-2026 DATA_DIR=data-demo
make docs        # lignage dbt sur http://localhost:8080
```

## Commandes du quotidien

| Besoin | Commande |
|---|---|
| Mettre à jour les données | automatique (pipeline quotidien) ; en local : `make pipeline` |
| Voir le tableau de bord | `make watchlist` |
| Comprendre un marché | `make explain M=<slug>` |
| État des derniers runs | `make runs` |
| Avant de pousser | `make check` (identique à la CI) |

## Production : pipeline quotidien (GitHub Actions → GitHub Pages)

`.github/workflows/pipeline.yml`, chaque jour à 05:17 UTC (et à la demande) :

1. monte la branche **`data`** (couche bronze versionnée, créée au premier run) ;
2. `polysignals ingest --source live` depuis le runner GitHub (hors de France : pas de blocage DNS) ;
3. commit + push de la couche bronze sur `data`, **même si l'ingestion échoue** (le manifeste le trace) ;
4. `dbt build` : un test en échec arrête tout ;
5. `polysignals export` : refusé si un test a échoué ou si aucun marché n'est présent ;
6. build Next.js statique → déploiement GitHub Pages par OIDC (aucun secret stocké).

Le site garde donc toujours la dernière version **saine**. Un push sur `main` qui touche le site,
dbt, l'Académie ou le code reconstruit le site à partir de la branche `data`, sans ingestion.

| Action | Où |
|---|---|
| Lancer un run maintenant | onglet Actions → « Pipeline quotidien » → *Run workflow* (ou `gh workflow run pipeline.yml`) |
| Voir pourquoi le site n'a pas bougé | dernier run du workflow : l'étape en rouge dit tout |
| Rejouer localement les données réelles | `git worktree add data-live origin/data` puis `make build web-dev DATA_DIR=$PWD/data-live` |

GitHub envoie un e-mail en cas d'échec d'un workflow planifié. La page « Sous le capot » et
l'indicateur de fraîcheur (orange au-delà de 48 h) rendent aussi une panne visible sur le site.

**Coût : 0 €.** Dépôt public, donc minutes Actions et Pages gratuites. Un run dure quelques
minutes et la branche `data` grossit d'environ 50 à 100 Mo par an. Si ça devient gênant, on
compactera en Parquet mensuel.

## Accès live depuis ce poste

Bloqué par le DNS du fournisseur d'accès (ANJ, `make doctor`). Ce n'est pas nécessaire : le
développement se fait sur `make demo` / `make web-demo`, et les données réelles se rejouent
depuis la branche `data` (voir ci-dessus).

## Premier run live : vérifications

Les slugs de tags de `transform/seeds/watchlist_selectors.csv` (`fed-rates`, `ecb`,
`inflation`, `recession`) sont **à confirmer** au premier run réel :

```bash
gh workflow run pipeline.yml   # puis lire les compteurs du run (étape « Ingestion live »)
```

Le premier run (lancé à la main depuis l'onglet Actions) le montre : si un tag ne renvoie rien,
le manifeste affiche 0 enregistrement pour ce flux. Si l'API a un autre format, c'est
`assert_no_contract_violations` qui échoue. Corriger la seed ou le contrat, pousser : le site se
reconstruit.

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| `Certificat TLS invalide … ANJ` | blocage DNS | `make doctor`, voir ci-dessus |
| `No files found that match the pattern` (dbt) | aucune ingestion encore faite | `make demo` ou `make ingest` |
| `assert_no_contract_violations` échoue | l'API a changé de format | `make contracts`, adapter `models.py` puis `stg_*` |
| `assert_last_ingestion_succeeded` échoue | dernier run en échec | `make runs`, relancer `make ingest` |
| Résultats incohérents après un changement de règle | entrepôt ancien | `make rebuild` |
| `Hôte non autorisé` | URL hors liste blanche | vérifier `POLYSIGNALS_*_BASE_URL` |
