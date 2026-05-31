/* @bruin
name: staging.stg_food_nutrients
type: duckdb.sql
materialization:
  type: table
depends:
  - ingestion.food_nutrients
@bruin */

select
    cast(food_id as integer)          as food_id,
    trim(nutrient)                    as nutrient,
    cast(value_per_100g as double)    as value_per_100g,
    trim(unit)                        as unit
from ingestion.food_nutrients
where food_id    is not null
  and nutrient   is not null
  and value_per_100g is not null
  and value_per_100g > 0