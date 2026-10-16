{#
  Macros DuckDB (côté base) pour lire la couche bronze avec un schéma d'enveloppe FIXE.
  Le payload brut reste en JSON : c'est la couche silver qui l'interprète.
  Créées à chaque exécution via `on-run-start` (dbt_project.yml).
  (Pas de read_json direct dans _sources.yml : dbt-duckdb y interprète les accolades.)
#}
{% macro create_bronze_readers() %}
create or replace macro bronze_records(path) as table
    select *
    from read_json(
        path,
        format = 'newline_delimited',
        hive_partitioning = true,
        columns = {
            record_id: 'VARCHAR', run_id: 'VARCHAR', ingested_at: 'TIMESTAMPTZ',
            source: 'VARCHAR', endpoint: 'VARCHAR', record_key: 'VARCHAR', params: 'JSON',
            contract_ok: 'BOOLEAN', contract_errors: 'JSON', payload: 'JSON'
        }
    );

create or replace macro bronze_runs(path) as table
    select *
    from read_json(
        path,
        columns = {
            run_id: 'VARCHAR', mode: 'VARCHAR', started_at: 'TIMESTAMPTZ',
            finished_at: 'TIMESTAMPTZ', status: 'VARCHAR', error: 'VARCHAR', counts: 'JSON'
        }
    );
{% endmacro %}
