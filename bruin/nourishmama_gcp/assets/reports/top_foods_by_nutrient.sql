/* @bruin
name: reports.top_foods_by_nutrient
type: bq.sql
materialization:
  type: table
depends:
  - marts.nutrient_rankings
@bruin */

select
    nutrient,
    food_name,
    category,
    target_group,
    value_per_100g,
    unit,
    nutrient_rank,
    is_baby_friendly,
    min_age_months,
    max_age_months,
    texture_stage
from marts.nutrient_rankings
where nutrient_rank <= 5
order by nutrient, nutrient_rank