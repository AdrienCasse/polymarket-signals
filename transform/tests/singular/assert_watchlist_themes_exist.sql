-- Chaque sélecteur de la watchlist pointe vers un thème décrit dans themes.csv.
select s.theme_id
from {{ ref('watchlist_selectors') }} as s
left join {{ ref('themes') }} as t using (theme_id)
where t.theme_id is null
