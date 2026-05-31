/* @bruin
name: reports.feeding_insights_by_stage
type: duckdb.sql
materialization:
  type: table
depends:
  - marts.meal_recommendations
@bruin */

-- Summary per developmental stage: food count, avg nutrition score,
-- top food, and dominant nutrient tags — useful for dashboard stage cards.

with tag_explosion as (
    select
        developmental_stage,
        unnest(recommendation_tags) as tag
    from marts.meal_recommendations
    where is_baby_friendly = true
),

top_tags as (
    select
        developmental_stage,
        tag,
        count(*) as tag_count,
        row_number() over (
            partition by developmental_stage
            order by count(*) desc
        ) as tag_rank
    from tag_explosion
    group by 1, 2
),

best_food_per_stage as (
    select distinct on (developmental_stage)
        developmental_stage,
        food_name          as top_food,
        nutrition_score    as top_food_score,
        top_nutrient       as top_food_nutrient
    from marts.meal_recommendations
    where is_baby_friendly = true
    order by developmental_stage, nutrition_score desc
)

select
    m.developmental_stage,
    m.min_age_months,
    m.max_age_months,
    count(distinct m.food_id)                   as available_food_count,
    round(avg(m.nutrition_score), 2)            as avg_nutrition_score,
    round(avg(m.tracked_nutrient_count), 1)     as avg_nutrients_tracked,

    -- Top food for this stage
    bf.top_food,
    bf.top_food_score,
    bf.top_food_nutrient,

    -- Top 3 nutrient tags for this stage
    max(case when tt.tag_rank = 1 then tt.tag end) as primary_tag,
    max(case when tt.tag_rank = 2 then tt.tag end) as secondary_tag,
    max(case when tt.tag_rank = 3 then tt.tag end) as tertiary_tag

from marts.meal_recommendations     m
join best_food_per_stage            bf using (developmental_stage)
left join top_tags                  tt using (developmental_stage)
where m.is_baby_friendly = true
group by
    m.developmental_stage,
    m.min_age_months,
    m.max_age_months,
    bf.top_food,
    bf.top_food_score,
    bf.top_food_nutrient
order by m.min_age_months