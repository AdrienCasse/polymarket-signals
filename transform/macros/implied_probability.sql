{#
  Probabilité implicite affichée pour une issue, selon la règle de Polymarket :
  - point milieu (meilleur achat + meilleure vente) / 2 si l'écart est serré ;
  - sinon dernier prix échangé, car un point milieu au milieu d'un écart large ne veut rien dire.
  Voir academy/01-prix-probabilite.md
#}
{% macro implied_probability(best_bid, best_ask, last_trade_price) -%}
    case
        when {{ best_bid }} is not null and {{ best_ask }} is not null
             and {{ best_ask }} - {{ best_bid }} <= {{ var('midpoint_max_spread') }}
            then round(({{ best_bid }} + {{ best_ask }}) / 2, 4)
        else {{ last_trade_price }}
    end
{%- endmacro %}
