-- Manifestes d'ingestion : base des contrôles de fraîcheur et de santé du pipeline.
select
    run_id,
    mode,
    started_at,
    finished_at,
    status,
    error,
    date_diff('second', started_at, finished_at) as duration_s,
    counts
from {{ source('bronze', 'ingestion_runs') }}
