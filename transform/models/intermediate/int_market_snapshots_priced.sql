-- Calculs de prix sur chaque instantané de marché. Grain : marché × instantané.
-- Les listes DuckDB commencent à l'indice 1 : outcome_prices[1] = issue « Yes ».
select
    market_id,
    event_id,
    snapshot_at,
    market_slug,
    question,
    outcomes = ['Yes', 'No']                                          as is_binary,
    clob_token_ids[1]                                                 as yes_token_id,
    outcome_prices[1]                                                 as yes_price,
    list_sum(outcome_prices)                                          as outcome_prices_sum,
    best_bid,
    best_ask,
    round(best_ask - best_bid, 4)                                     as spread,
    last_trade_price,
    {{ implied_probability('best_bid', 'best_ask', 'last_trade_price') }} as implied_probability,
    liquidity_usd,
    volume_usd,
    volume_24h_usd,
    api_change_1d,
    api_change_7d,
    end_at,
    is_active,
    is_closed,
    resolution_source,
    contract_ok
from {{ ref('stg_gamma__market_snapshots') }}
