{# Une probabilité (ou un prix d'issue) est toujours comprise entre 0 et 1. #}
{% test is_probability(model, column_name) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} is not null
  and ({{ column_name }} < 0 or {{ column_name }} > 1)
{% endtest %}
