# Académie polysignals

Sept leçons courtes pour **comprendre** les marchés prédictifs, et le pipeline qui les lit.
Chaque leçon se termine par « Dans le code » (où l'idée vit dans le projet) et « À retenir ».

| # | Leçon | Tu sauras… |
|---|---|---|
| 00 | [L'architecture data](00-architecture-data.md) | pourquoi bronze → silver → gold, idempotence, contrats |
| 01 | [Un prix est une probabilité](01-prix-probabilite.md) | lire 0,62 $ comme « 62 % » et d'où vient ce chiffre |
| 02 | [Carnet d'ordres et liquidité](02-carnet-ordres-liquidite.md) | distinguer un signal solide d'un chiffre vide |
| 03 | [La résolution et l'oracle](03-resolution-oracle.md) | qui décide qu'un événement s'est produit, et le risque associé |
| 04 | [Biais et limites](04-biais-et-limites.md) | pourquoi 5 % ne veut pas toujours dire 5 % |
| 05 | [Lire un signal macro sans spéculer](05-lire-un-signal-macro.md) | utiliser l'information sans toucher à ton DCA |
| 06 | [Le cadre légal en France](06-cadre-legal-france.md) | pourquoi le projet est en lecture seule |

Parcours conseillé : `make demo`, puis lis 01 → 02 en gardant `make explain M=ecb-cut-december-2026`
ouvert à côté : c'est l'exemple d'un signal inexploitable.

Les données de démonstration sont **synthétiques** (`tests/fixtures/`) : formes réelles de
l'API, valeurs inventées.
