-- Rattache chaque événement aux thèmes de la watchlist, par tag ou par slug d'événement.
-- Grain : événement × thème.
with selectors as (
    select * from {{ ref('watchlist_selectors') }}
),

events as (
    select distinct event_id, event_slug from {{ ref('stg_gamma__events') }}
),

by_tag as (
    select t.event_id, s.theme_id
    from {{ ref('stg_gamma__event_tags') }} as t
    inner join selectors as s
        on s.selector_type = 'tag' and s.selector_value = t.tag_slug
),

by_event as (
    select e.event_id, s.theme_id
    from events as e
    inner join selectors as s
        on s.selector_type = 'event' and s.selector_value = e.event_slug
)

select distinct event_id, theme_id from by_tag
union
select distinct event_id, theme_id from by_event
