/* @bruin
name: marts.fact_mother_nutrition
type: duckdb.sql
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
    texture_stage

from staging.stg_mother_nutrition
where food_id is not null
  and nutrient is not null
  and value_per_100g is not null