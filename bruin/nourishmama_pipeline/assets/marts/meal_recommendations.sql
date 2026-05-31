/* @bruin
name: marts.meal_recommendations
type: duckdb.sql
materialization:
  type: table
depends:
  - staging.stg_foods
  - staging.stg_food_nutrients
@bruin */

-- One row per food with aggregated nutrient profile + recommendation metadata.
-- Consumers (Streamlit, reports) filter by baby_age_months and/or texture_stage.

with nutrient_profile as (
    select
        food_id,
        -- Pivot key nutrients as columns for quick Streamlit display
        max(case when nutrient = 'Protein'      then round(value_per_100g, 1) end) as protein_g,
        max(case when nutrient = 'Iron'         then round(value_per_100g, 2) end) as iron_mg,
        max(case when nutrient = 'Calcium'      then round(value_per_100g, 1) end) as calcium_mg,
        max(case when nutrient = 'Vitamin C'    then round(value_per_100g, 1) end) as vitamin_c_mg,
        max(case when nutrient = 'Folate'       then round(value_per_100g, 1) end) as folate_mcg,
        max(case when nutrient = 'Vitamin A'    then round(value_per_100g, 1) end) as vitamin_a_mcg,
        max(case when nutrient = 'Vitamin D'    then round(value_per_100g, 2) end) as vitamin_d_mcg,
        max(case when nutrient = 'Omega3'       then round(value_per_100g, 2) end) as omega3_g,
        max(case when nutrient = 'Fiber'        then round(value_per_100g, 1) end) as fiber_g,
        max(case when nutrient = 'Potassium'    then round(value_per_100g, 1) end) as potassium_mg,
        max(case when nutrient = 'Magnesium'    then round(value_per_100g, 1) end) as magnesium_mg,
        -- Count distinct nutrients tracked — proxy for how nutrient-dense the food is
        count(distinct nutrient) as tracked_nutrient_count
    from staging.stg_food_nutrients
    group by food_id
),

-- Identify the top nutrient per food (the standout nutrient)
top_nutrient as (
    select distinct on (food_id)
        food_id,
        nutrient          as top_nutrient,
        value_per_100g    as top_nutrient_value,
        unit              as top_nutrient_unit
    from staging.stg_food_nutrients
    order by food_id, value_per_100g desc
)

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

    -- Nutrient profile columns
    np.protein_g,
    np.iron_mg,
    np.calcium_mg,
    np.vitamin_c_mg,
    np.folate_mcg,
    np.vitamin_a_mcg,
    np.vitamin_d_mcg,
    np.omega3_g,
    np.fiber_g,
    np.potassium_mg,
    np.magnesium_mg,
    np.tracked_nutrient_count,

    -- Standout nutrient for recommendation card headline
    tn.top_nutrient,
    tn.top_nutrient_value,
    tn.top_nutrient_unit,

    -- Nutrient density score: sum of rank-normalised values (lower total rank = denser)
    -- Useful for sorting "best overall" foods for a given filter
    (
        coalesce(np.protein_g,    0) * 0.20 +
        coalesce(np.iron_mg,      0) * 5.00 +   -- iron weighted high (critical for babies)
        coalesce(np.calcium_mg,   0) * 0.01 +
        coalesce(np.vitamin_c_mg, 0) * 0.10 +
        coalesce(np.folate_mcg,   0) * 0.05 +
        coalesce(np.vitamin_a_mcg,0) * 0.02 +
        coalesce(np.omega3_g,     0) * 10.0 +
        coalesce(np.fiber_g,      0) * 0.50
    )                                           as nutrition_score,

    -- Recommendation tags (array of strings → useful in Streamlit)
    list_filter([
        case when np.iron_mg     >= 2.0  then 'High Iron'     end,
        case when np.protein_g   >= 8.0  then 'High Protein'  end,
        case when np.calcium_mg  >= 100  then 'High Calcium'  end,
        case when np.vitamin_c_mg>= 20   then 'Vitamin C Boost' end,
        case when np.omega3_g    >= 1.0  then 'Omega-3 Rich'  end,
        case when np.folate_mcg  >= 80   then 'Folate Rich'   end,
        case when np.fiber_g     >= 3.0  then 'Good Fiber'    end,
        case when f.texture_stage = 'pureed'  then 'First Foods Ready' end,
        case when f.is_baby_friendly          then 'Baby Safe'         end
    ], x -> x is not null)                      as recommendation_tags

from staging.stg_foods          f
join nutrient_profile           np using (food_id)
join top_nutrient               tn using (food_id)

order by nutrition_score desc