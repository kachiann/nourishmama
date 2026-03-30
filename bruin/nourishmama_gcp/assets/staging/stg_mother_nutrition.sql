/* @bruin
name: staging.stg_mother_nutrition
type: bq.sql
materialization:
  type: table
depends:
  - raw.mother_nutrition
@bruin */

select
    cast(food_id as int64) as food_id,
    trim(food_name) as food_name,
    trim(category) as category,
    trim(nutrient) as nutrient,
    cast(value_per_100g as float64) as value_per_100g,
    trim(unit) as unit,
    trim(target_group) as target_group,
    cast(is_baby_friendly as bool) as is_baby_friendly,
    cast(min_age_months as int64) as min_age_months,
    cast(max_age_months as int64) as max_age_months,
    trim(texture_stage) as texture_stage
from raw.mother_nutrition
where food_name is not null
  and nutrient is not null
  and value_per_100g is not null