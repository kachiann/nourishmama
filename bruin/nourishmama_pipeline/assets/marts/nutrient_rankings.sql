/* @bruin
name: marts.nutrient_rankings
type: duckdb.sql
materialization:
  type: table
depends:
  - staging.stg_foods
  - staging.stg_food_nutrients
@bruin */

select
    f.food_id,
    f.food_name,
    f.category,
    f.target_group,
    f.is_baby_friendly,
    f.texture_stage,
    f.is_texture_safe,
    f.min_age_months,
    f.max_age_months,
    f.developmental_stage,
    n.nutrient,
    n.value_per_100g,
    n.unit,

    -- Rank within nutrient across all foods in same target group
    rank() over (
        partition by n.nutrient, f.target_group
        order by n.value_per_100g desc
    ) as nutrient_rank,

    -- Rank within nutrient inside the same food category
    rank() over (
        partition by n.nutrient, f.category, f.target_group
        order by n.value_per_100g desc
    ) as category_nutrient_rank,

    -- Rank within nutrient for the specific developmental stage
    rank() over (
        partition by n.nutrient, f.developmental_stage
        order by n.value_per_100g desc
    ) as stage_nutrient_rank

from staging.stg_foods          f
join staging.stg_food_nutrients n using (food_id)