/* @bruin
name: marts.nutrient_rankings
type: bq.sql
materialization:
  type: table
depends:
  - staging.stg_mother_nutrition
@bruin */

select
    food_id,
    food_name,
    category,
    nutrient,
    value_per_100g,
    unit,
    target_group,
    is_baby_friendly,
    min_age_months,
    max_age_months,
    texture_stage,
    rank() over (
        partition by nutrient, target_group
        order by value_per_100g desc
    ) as nutrient_rank,
    rank() over (
        partition by nutrient, category, target_group
        order by value_per_100g desc
    ) as category_nutrient_rank
from staging.stg_mother_nutrition