# 02 · Carnet d'ordres et liquidité : solide, fragile ou inexploitable ?

## Pourquoi c'est la leçon la plus importante

Un pourcentage s'affiche toujours avec la même assurance, qu'il résulte de millions de dollars
échangés ou de trois ordres oubliés. La **qualité** du signal compte plus que sa valeur.

## Les trois indicateurs

| Indicateur | Question | Signal fort | Signal faible |
|---|---|---|---|
| **Écart** (ask − bid) | acheteurs et vendeurs sont-ils d'accord ? | ≤ 3 pts | > 10 pts |
| **Liquidité** | combien d'argent attend dans le carnet ? | ≥ 100 000 $ | < 1 000 $ |
| **Échéance** | dans combien de temps la réponse ? | < 1 an | > 1 an |

Une liquidité faible signifie qu'un seul participant peut **déplacer le prix** de plusieurs
points avec quelques centaines de dollars, par erreur ou volontairement.

L'échéance lointaine pose un problème plus subtil. Immobiliser 1 $ pendant deux ans sans
intérêts a un coût. Personne ne paie donc 0,99 $ pour un « Non » quasi certain à deux ans,
et les événements improbables à long terme paraissent **plus probables** qu'ils ne le sont.

## La classification du projet

- **inexploitable** : écart > 10 pts, liquidité < 1 000 $ ou carnet vide ;
- **fragile** : écart > 3 pts, liquidité < 100 000 $ ou échéance > 365 jours ;
- **solide** : sinon.

Les seuils sont des variables dbt (`transform/dbt_project.yml`, clé `quality`) : tu peux les
discuter et les changer, chaque raison est affichée en clair.

## Dans le code

- `transform/models/marts/mart_macro_watchlist.sql` : colonnes `signal_quality` et
  `quality_reasons`
- `polysignals explain` : section « 3. Peut-on s'y fier ? »

## À retenir

> Avant de lire « 41 % », lis l'écart et la liquidité. Un chiffre sans profondeur n'est pas
> une information.
