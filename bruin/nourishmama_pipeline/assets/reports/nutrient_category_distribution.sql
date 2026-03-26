/* @bruin
name: reports.nutrient_category_distribution
type: duckdb.sql
materialization:
  type: table
depends:
  - marts.nutrient_rankings
@bruin */

select
    nutrient,
    category,
    target_group,
    is_baby_friendly,
    min_age_months,
    max_age_months,
    count(*) as food_count,
    avg(value_per_100g) as avg_value_per_100g
from marts.nutrient_rankings
group by 1, 2, 3, 4, 5, 6
order by nutrient, avg_value_per_100g desc