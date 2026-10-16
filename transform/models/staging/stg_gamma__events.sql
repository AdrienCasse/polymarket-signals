-- Un événement Gamma par enregistrement bronze (grain : événement × instantané d'ingestion).
select
    record_id,
    run_id,
    ingested_at,
    contract_ok,
    payload ->> 'id'                                  as event_id,
    payload ->> 'slug'                                as event_slug,
    payload ->> 'title'                               as event_title,
    try_cast(payload ->> 'endDate' as timestamptz)    as event_end_at,
    try_cast(payload ->> 'active' as boolean)         as is_active,
    try_cast(payload ->> 'closed' as boolean)         as is_closed,
    payload
from {{ source('bronze', 'gamma_events') }}
