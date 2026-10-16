-- Marchés imbriqués dans les événements, aplatis. Grain : marché × instantané d'ingestion.
-- Gamma encode outcomes / outcomePrices / clobTokenIds en CHAÎNES JSON ('["Yes","No"]') :
-- `->>` renvoie le texte, puis from_json le décode (fonctionne aussi si l'API renvoie un vrai tableau).
with markets as (
    select
        e.event_id,
        e.ingested_at,
        e.contract_ok,
        unnest(e.payload -> '$.markets[*]') as m
    from {{ ref('stg_gamma__events') }} as e
),

typed as (
    select
        m ->> 'id'                                                    as market_id,
        event_id,
        ingested_at                                                   as snapshot_at,
        contract_ok,
        m ->> 'slug'                                                  as market_slug,
        m ->> 'question'                                              as question,
        m ->> 'conditionId'                                           as condition_id,
        from_json(m ->> 'outcomes', '["VARCHAR"]')                    as outcomes,
        list_transform(
            from_json(m ->> 'outcomePrices', '["VARCHAR"]'), p -> try_cast(p as double)
        )                                                             as outcome_prices,
        from_json(m ->> 'clobTokenIds', '["VARCHAR"]')                as clob_token_ids,
        try_cast(m ->> 'bestBid' as double)                           as best_bid,
        try_cast(m ->> 'bestAsk' as double)                           as best_ask,
        try_cast(m ->> 'lastTradePrice' as double)                    as last_trade_price,
        try_cast(m ->> 'liquidityNum' as double)                      as liquidity_usd,
        try_cast(m ->> 'volumeNum' as double)                         as volume_usd,
        try_cast(m ->> 'volume24hr' as double)                        as volume_24h_usd,
        try_cast(m ->> 'oneDayPriceChange' as double)                 as api_change_1d,
        try_cast(m ->> 'oneWeekPriceChange' as double)                as api_change_7d,
        try_cast(m ->> 'endDate' as timestamptz)                      as end_at,
        try_cast(m ->> 'active' as boolean)                           as is_active,
        try_cast(m ->> 'closed' as boolean)                           as is_closed,
        m ->> 'resolutionSource'                                      as resolution_source
    from markets
)

select *
from typed
-- un même marché peut être vu deux fois dans un run (événement couvert par deux sélecteurs)
qualify row_number() over (partition by market_id, snapshot_at order by contract_ok desc) = 1
