# 06 · Le cadre légal en France

## Les faits

- En France, les jeux d'argent en ligne sont soumis à un **agrément de l'ANJ** (Autorité
  nationale des jeux). Polymarket n'en a pas.
- Depuis fin 2024, l'ANJ fait **bloquer** l'accès à Polymarket. Concrètement, les fournisseurs
  d'accès redirigent les noms `*.polymarket.com` vers une page de l'ANJ.
- Polymarket restreint lui-même l'accès au trading depuis certains pays, dont la France.

## Ce que tu as constaté en lançant le projet

```
$ make doctor
KO gamma-api.polymarket.com  145.239.225.117
   Hostname mismatch … → certificat présenté pour *.anj.fr
```

Le DNS de ton fournisseur renvoie l'adresse d'un serveur de l'ANJ. Ce serveur présente un
certificat `*.anj.fr`, et le client HTTP **refuse** la connexion, car le certificat ne
correspond pas au nom demandé. C'est exactement le rôle de TLS : garantir qu'on parle au bon
serveur. On ne désactive jamais cette vérification (`verify=True` est forcé dans
`src/polysignals/http.py`).

## Pourquoi le projet est en lecture seule

1. **Cohérence** : l'objectif est de comprendre, pas de parier (décision du 2026-10-13).
2. **Légalité** : participer depuis la France contourne une interdiction ; le projet ne le fait
   pas et ne l'outille pas.
3. **Sécurité** : aucune clé privée, aucun wallet, aucune signature. Le pire scénario d'une
   fuite du dépôt est… rien.

L'accès aux **données publiques** (lecture) pose une autre question, distincte du pari : voir
`docs/runbook.md`, § « Accès aux données live ».

## À retenir

> Le blocage ANJ est visible jusque dans ta stack réseau. Le projet le détecte et l'explique
> (`make doctor`), mais ne le contourne pas.
