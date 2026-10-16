-- Le dernier run d'ingestion doit avoir réussi : sinon les marts reflètent un état ancien.
select run_id, status, error
from {{ ref('stg_ingestion_runs') }}
qualify row_number() over (order by started_at desc) = 1
    and status <> 'success'
