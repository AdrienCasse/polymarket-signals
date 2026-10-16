-- Tout enregistrement bronze doit respecter son contrat (src/polysignals/models.py).
-- En cas d'échec : `polysignals contracts` liste les violations à corriger.
select 'gamma_events' as stream, record_id, contract_errors
from {{ source('bronze', 'gamma_events') }}
where not contract_ok
union all
select 'clob_prices_history', record_id, contract_errors
from {{ source('bronze', 'clob_prices_history') }}
where not contract_ok
