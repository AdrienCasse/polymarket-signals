# 01 · Un prix est une probabilité

## Le mécanisme

Sur Polymarket, chaque question binaire (« La Fed baisse-t-elle ses taux en décembre ? ») a deux
issues, **Oui** et **Non**. Une part d'issue gagnante vaut **1 $** à la résolution, une part
perdante **0 $**.

Si la part « Oui » s'échange à **0,62 $**, acheter revient à miser 0,62 $ pour en récupérer 1 $
si l'événement se produit. Ce pari est équitable quand la probabilité vaut 62 %. Le prix se lit
donc comme une **probabilité implicite** : ce que, collectivement et argent en jeu, les
participants estiment.

Conséquence : `prix(Oui) + prix(Non) ≈ 1`. Un écart notable est suspect (test dbt
`assert_binary_prices_sum_to_one`).

## Quel prix, exactement ?

Il n'y a pas « un » prix, mais un **carnet d'ordres** : des acheteurs (bid) et des vendeurs (ask).

- Meilleur acheteur 0,61 $, meilleur vendeur 0,63 $ → **point milieu** 0,62 $.
- Si l'écart dépasse **0,10 $**, le point milieu ne veut plus rien dire (un acheteur à 0,30 $ et
  un vendeur à 0,52 $ ne « pensent » pas 41 %). Polymarket affiche alors le **dernier prix
  échangé**. Le projet applique la même règle.

## Exemple (données synthétiques)

```
make explain M=fed-cut-25-dec-2026      → écart 2 pts  → point milieu 62 %
make explain M=ecb-cut-december-2026    → écart 22 pts → dernier échange 41 %
```

## Dans le code

- `transform/macros/implied_probability.sql` : la règle, en une macro
- `transform/models/intermediate/_intermediate.yml` : un **test unitaire dbt** vérifie les
  trois cas (écart serré, écart large, carnet vide)

## À retenir

> Prix = probabilité implicite, **à condition** que le carnet soit sérieux.
> La leçon 02 explique comment le vérifier.
