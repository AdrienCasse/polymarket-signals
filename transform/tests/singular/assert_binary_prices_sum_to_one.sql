-- Sur un marché binaire, prix(Yes) + prix(No) ≈ 1. Un écart important signale une donnée
-- corrompue ou un changement de format de l'API (ou un marché sans liquidité).
{{ config(severity = 'warn') }}

select market_id, snapshot_at, outcome_prices_sum
from {{ ref('int_market_snapshots_priced') }}
where is_binary
  and is_active
  and abs(outcome_prices_sum - 1) > 0.02
