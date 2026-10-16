-- Dernier état connu de chaque marché. Grain : marché.
with latest as (
    select *
    from {{ ref('int_market_snapshots_priced') }}
    qualify row_number() over (partition by market_id order by snapshot_at desc) = 1
),

events as (
    select event_id, event_slug, event_title
    from {{ ref('stg_gamma__events') }}
    qualify row_number() over (partition by event_id order by ingested_at desc) = 1
)

select
    l.market_id,
    l.market_slug,
    l.question,
    l.event_id,
    e.event_slug,
    e.event_title,
    l.is_binary,
    l.yes_token_id,
    l.end_at,
    l.is_active,
    l.is_closed,
    l.resolution_source,
    l.snapshot_at as last_seen_at
from latest as l
left join events as e using (event_id)
