-- Probabilité de clôture quotidienne de l'issue « Yes » de chaque marché binaire.
-- Grain : marché × jour (dernier point du jour, en UTC).
with prices as (
    select
        m.market_id,
        p.token_id,
        cast(timezone('UTC', p.price_at) as date) as price_date,
        p.price_at,
        p.price
    from {{ ref('stg_clob__price_history') }} as p
    inner join {{ ref('dim_markets') }} as m
        on m.yes_token_id = p.token_id
)

select market_id, token_id, price_date, price as close_probability
from prices
qualify row_number() over (partition by market_id, price_date order by price_at desc) = 1
