# 04 · Biais et limites : pourquoi 5 % ne veut pas toujours dire 5 %

## 1. Le biais favori/outsider

Documenté depuis des décennies dans les paris hippiques : les **outsiders sont surpayés** et les
**favoris sous-payés**. Un cheval coté « 5 % » gagne en réalité moins souvent que 5 % des fois.
Des travaux récents trouvent le même schéma sur Polymarket : les prix seraient « tassés » vers
50 %, avec une ampleur qui varie selon le domaine (sport, politique, économie).
*Pistes à vérifier et à mesurer nous-mêmes : voir la feuille de route, étape « calibration ».*

Pourquoi ? Goût pour les gros gains improbables (effet loterie), coût d'immobilisation (leçon
02), et peu de vendeurs prêts à bloquer 0,95 $ pour gagner 0,05 $.

## 2. Qui parie ?

Les participants ne sont pas un échantillon représentatif : population crypto, majoritairement
anglophone, avec des opinions parfois corrélées. Sur un sujet politique, leur préférence peut
déborder sur leur estimation.

## 3. Marchés minces et manipulation

Sur un petit marché, quelques milliers de dollars suffisent à afficher la probabilité de son
choix, et la fausse impression qu'un « marché » la valide. D'où le filtre de qualité (leçon 02).

## 4. Un prix n'est pas une croyance moyenne

Même dans un marché idéal, le prix est le niveau où acheteurs et vendeurs **marginaux**
s'équilibrent, pondéré par l'argent qu'ils engagent. Ce n'est pas l'avis moyen des
participants.

## 5. Bien calibré ≠ toujours juste

Un marché bien calibré se trompe **régulièrement** : sur 100 événements cotés 70 %, environ 30
ne se produisent pas. Juger un marché sur un seul résultat est une erreur (biais de résultat).

## Comment mesurer tout ça : la calibration

On regroupe les marchés **résolus** par tranche de prix (0–10 %, 10–20 %…) et on compare la
probabilité affichée à la fréquence réelle. Le **score de Brier** résume l'écart :
`moyenne((probabilité − résultat)²)`, où 0 est parfait et 0,25 équivaut à répondre toujours
50 %. C'est la prochaine grande étape du projet.

## Références classiques

- Wolfers & Zitzewitz (2004), *Prediction Markets*, Journal of Economic Perspectives
- Manski (2006), *Interpreting the predictions of prediction markets*, Economics Letters
- Snowberg & Wolfers (2010), *Explaining the Favorite–Long Shot Bias*, Journal of Political Economy

## À retenir

> Une probabilité de marché est une **estimation informée et biaisée**. Elle se trompe le plus
> aux extrêmes (sous 10 % ou au-dessus de 90 %) et sur les échéances lointaines.
