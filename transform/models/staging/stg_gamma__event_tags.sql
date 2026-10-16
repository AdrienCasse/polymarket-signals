-- Thèmes (tags) de chaque événement, dernier état connu. Grain : événement × tag.
with latest_event as (
    select *
    from {{ ref('stg_gamma__events') }}
    qualify row_number() over (partition by event_id order by ingested_at desc) = 1
),

tags as (
    select
        event_id,
        unnest(payload -> '$.tags[*]') as tag
    from latest_event
)

select distinct
    event_id,
    tag ->> 'slug'  as tag_slug,
    tag ->> 'label' as tag_label
from tags
