-- Tableau de bord macro : un marché ouvert de la watchlist par ligne, prêt à lire.
-- C'est l'interface publique du projet (contrat de schéma appliqué), consommée par
-- `polysignals explain` et, à terme, par fintrack. Grain : marché × thème.
{% set q = var('quality') %}

with current_markets as (
    select s.*
    from {{ ref('int_market_snapshots_priced') }} as s
    inner join {{ ref('dim_markets') }} as d
        on d.market_id = s.market_id and d.last_seen_at = s.snapshot_at
    where s.is_binary and s.is_active and not s.is_closed
),

-- Les variations sont ancrées sur le dernier jour d'historique de chaque marché (et non sur
-- current_date) : le résultat est déterministe, quelle que soit la date de reconstruction.
daily as (
    select
        *,
        max(price_date) over (partition by market_id) as anchor_date
    from {{ ref('fct_daily_prices') }}
),

history as (
    select
        market_id,
        arg_max(close_probability, price_date)
            filter (where price_date <= anchor_date - interval 7 day)     as close_7d_ago,
        arg_max(close_probability, price_date)
            filter (where price_date <= anchor_date - interval 30 day)    as close_30d_ago,
        min(close_probability)
            filter (where price_date > anchor_date - interval 90 day)     as min_90d,
        max(close_probability)
            filter (where price_date > anchor_date - interval 90 day)     as max_90d
    from daily
    group by market_id
),

enriched as (
    select
        m.market_id,
        t.theme_id,
        th.theme_label,
        d.event_title,
        m.question,
        m.market_slug,
        m.implied_probability,
        m.implied_probability - h.close_7d_ago                            as change_7d,
        m.implied_probability - h.close_30d_ago                           as change_30d,
        h.min_90d,
        h.max_90d,
        m.best_bid,
        m.best_ask,
        m.spread,
        m.last_trade_price,
        m.liquidity_usd,
        m.volume_24h_usd,
        m.end_at,
        date_diff('day', cast(m.snapshot_at as date), cast(m.end_at as date))            as days_to_resolution,
        m.resolution_source,
        th.why_it_matters,
        th.academy_lesson,
        m.snapshot_at                                                     as as_of
    from current_markets as m
    inner join {{ ref('dim_markets') }} as d using (market_id)
    inner join {{ ref('int_event_themes') }} as t on t.event_id = m.event_id
    inner join {{ ref('themes') }} as th on th.theme_id = t.theme_id
    left join history as h on h.market_id = m.market_id
),

quality as (
    select
        *,
        list_filter([
            case when spread is null then 'carnet d''ordres vide' end,
            case when spread > {{ q.unusable_spread }}
                then 'écart achat/vente très large (' || round(spread * 100, 1) || ' pts)' end,
            case when liquidity_usd < {{ q.unusable_liquidity }}
                then 'liquidité quasi nulle' end
        ], x -> x is not null) as blocking_reasons,
        list_filter([
            case when spread > {{ q.fragile_spread }} and spread <= {{ q.unusable_spread }}
                then 'écart achat/vente large (' || round(spread * 100, 1) || ' pts)' end,
            case when liquidity_usd >= {{ q.unusable_liquidity }}
                      and liquidity_usd < {{ q.fragile_liquidity }}
                then 'liquidité faible (' || cast(round(liquidity_usd) as bigint) || ' $)' end,
            case when days_to_resolution > {{ q.fragile_horizon_days }}
                then 'échéance lointaine (le prix intègre aussi le coût d''immobiliser l''argent)' end
        ], x -> x is not null) as warning_reasons
    from enriched
)

select
    market_id,
    theme_id,
    theme_label,
    event_title,
    question,
    market_slug,
    cast(implied_probability as double)                                   as implied_probability,
    cast(change_7d as double)                                             as change_7d,
    cast(change_30d as double)                                            as change_30d,
    cast(min_90d as double)                                               as min_90d,
    cast(max_90d as double)                                               as max_90d,
    cast(best_bid as double)                                              as best_bid,
    cast(best_ask as double)                                              as best_ask,
    cast(spread as double)                                                as spread,
    cast(last_trade_price as double)                                      as last_trade_price,
    cast(liquidity_usd as double)                                         as liquidity_usd,
    cast(volume_24h_usd as double)                                        as volume_24h_usd,
    end_at,
    cast(days_to_resolution as integer)                                   as days_to_resolution,
    case
        when len(blocking_reasons) > 0 then 'inexploitable'
        when len(warning_reasons) > 0 then 'fragile'
        else 'solide'
    end                                                                   as signal_quality,
    cast(list_concat(blocking_reasons, warning_reasons) as varchar[])     as quality_reasons,
    resolution_source,
    why_it_matters,
    academy_lesson,
    as_of
from quality
-- Marché jamais échangé et carnet quasi vide : il n'existe AUCUNE probabilité lisible.
-- On l'exclut plutôt que d'afficher un chiffre inventé (cf. academy/02).
where implied_probability is not null
