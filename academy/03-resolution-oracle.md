# 03 · La résolution : qui décide de la réponse ?

## Le problème

Pour payer les gagnants, il faut établir ce qui s'est passé. Sur une blockchain, il faut un
mécanisme pour faire entrer un fait du monde réel : c'est le rôle d'un **oracle**.

## Comment ça marche sur Polymarket

Polymarket s'appuie sur l'**oracle optimiste d'UMA** :

1. quelqu'un **propose** une réponse en déposant une caution ;
2. une **période de contestation** s'ouvre ; sans contestation, la réponse est acceptée ;
3. en cas de contestation, les détenteurs du jeton UMA **votent**.

C'est « optimiste » car on suppose la proposition honnête, sauf contestation.

## Le risque que le prix ne montre pas

Le prix mesure la croyance « l'événement va se produire **et** sera résolu comme tel ». Une
règle mal rédigée (« baisse de taux » : de combien ? annoncée quand ?) ou un vote contesté peut
résoudre un marché à l'inverse de ce que le bon sens attendait. Des litiges médiatisés ont
existé.

Réflexes :

- lire la **règle de résolution** et la **source officielle** citée (champ `resolution_source`) ;
- se méfier des questions vagues ou subjectives ;
- pour un usage macro, préférer les questions adossées à une source **officielle et datée**
  (communiqué de la Fed, chiffre du CPI publié par le BLS).

## Dans le code

- `resolution_source` est remonté jusqu'au mart et affiché par `polysignals explain`

## À retenir

> Une probabilité Polymarket inclut toujours un risque de résolution. Il est faible sur
> « la Fed baisse-t-elle de 25 pb le 16/12 », et élevé sur une question floue.
