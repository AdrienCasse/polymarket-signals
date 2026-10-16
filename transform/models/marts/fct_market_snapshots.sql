-- Série temporelle construite par nos propres ingestions (une ligne par passage).
-- Complète l'historique CLOB avec la liquidité et l'écart, que l'historique ne fournit pas.
select
    market_id,
    snapshot_at,
    implied_probability,
    yes_price,
    best_bid,
    best_ask,
    spread,
    liquidity_usd,
    volume_24h_usd
from {{ ref('int_market_snapshots_priced') }}
