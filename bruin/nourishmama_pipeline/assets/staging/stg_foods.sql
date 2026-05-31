/* @bruin
name: staging.stg_foods
type: duckdb.sql
materialization:
  type: table
depends:
  - ingestion.foods
@bruin */

select
    cast(food_id as integer)          as food_id,
    trim(food_name)                   as food_name,
    trim(category)                    as category,
    trim(target_group)                as target_group,
    cast(is_baby_friendly as boolean) as is_baby_friendly,
    trim(texture_stage)               as texture_stage,
    cast(min_age_months as integer)   as min_age_months,
    cast(max_age_months as integer)   as max_age_months,

    -- Derived: human-readable developmental stage label
    case
        when min_age_months between 4  and 6  then '4–6 months (First Foods)'
        when min_age_months between 6  and 8  then '6–8 months (Purees & Mashes)'
        when min_age_months between 8  and 11 then '8–11 months (Soft Solids)'
        when min_age_months >= 12             then '12+ months (Family Foods)'
        else 'Unknown'
    end                               as developmental_stage,

    -- Derived: texture safety classification
    case
        when texture_stage in ('not_safe_whole', 'choking_risk', 'not_for_babies', 'adult_texture')
            then FALSE
        else TRUE
    end                               as is_texture_safe

from ingestion.foods
where food_name is not null