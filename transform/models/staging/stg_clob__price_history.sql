-- Historique de prix d'une issue (token), dédupliqué. Grain : token × horodatage.
-- Chaque ingestion renvoie tout l'historique : on garde la version la plus récente de chaque point.
with points as (
    select
        record_key   as token_id,
        ingested_at,
        unnest(payload -> '$.history[*]') as point
    from {{ source('bronze', 'clob_prices_history') }}
)

select
    token_id,
    to_timestamp(try_cast(point ->> 't' as bigint)) as price_at,
    try_cast(point ->> 'p' as double)               as price,
    ingested_at
from points
qualify row_number() over (partition by token_id, price_at order by ingested_at desc) = 1
