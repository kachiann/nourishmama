from google.cloud import bigquery
import streamlit as st

PROJECT_ID = "nourishmama-project"

st.set_page_config(
    page_title="NourishMama Cloud",
    page_icon="🌱",
    layout="wide",
)

st.markdown(
    """
    # 🌱 NourishMama Cloud
    ### Nutrition insights for nursing mothers and baby-friendly foods under 1 year

    Explore nutrient-rich foods for mothers and age-appropriate foods for babies under 1.
    """
)


@st.cache_data
def load_data():
    client = bigquery.Client(project=PROJECT_ID)

    dist_query = f"""
        SELECT *
        FROM `{PROJECT_ID}.reports.nutrient_category_distribution`
    """

    top_query = f"""
        SELECT *
        FROM `{PROJECT_ID}.reports.top_foods_by_nutrient`
    """

    dist_df = client.query(dist_query).to_dataframe()
    top_df = client.query(top_query).to_dataframe()

    return dist_df, top_df


dist_df, top_df = load_data()

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("Total Foods", len(top_df["food_name"].unique()))
metric_col2.metric("Nutrients Covered", len(top_df["nutrient"].unique()))
metric_col3.metric("Categories", len(top_df["category"].unique()))

st.markdown(
    "Use the filters below to explore nutrient distribution across food categories and identify top foods for key nutrients."
)

audience = st.radio(
    "View nutrition insights for:",
    ["Baby under 1", "Mother", "Both"],
    horizontal=True,
)

selected_age = None
if audience == "Baby under 1":
    selected_age = st.selectbox(
        "Select baby age (months)",
        [6, 7, 8, 9, 10, 11],
        index=0,
    )

filtered_dist_base = dist_df.copy()
filtered_top_base = top_df.copy()

if audience == "Baby under 1":
    filtered_dist_base = filtered_dist_base[
        (filtered_dist_base["is_baby_friendly"] == True)
        & (filtered_dist_base["min_age_months"] <= selected_age)
        & (filtered_dist_base["max_age_months"] >= selected_age)
    ]

    filtered_top_base = filtered_top_base[
        (filtered_top_base["is_baby_friendly"] == True)
        & (filtered_top_base["min_age_months"] <= selected_age)
        & (filtered_top_base["max_age_months"] >= selected_age)
    ]

elif audience == "Mother":
    filtered_dist_base = filtered_dist_base[
        filtered_dist_base["target_group"].isin(["mother", "both"])
    ]

    filtered_top_base = filtered_top_base[
        filtered_top_base["target_group"].isin(["mother", "both"])
    ]

else:
    filtered_dist_base = filtered_dist_base[
        filtered_dist_base["target_group"].isin(["mother", "both"])
        | (
            (filtered_dist_base["is_baby_friendly"] == True)
            & (filtered_dist_base["min_age_months"] <= 11)
            & (filtered_dist_base["max_age_months"] >= 6)
        )
    ]

    filtered_top_base = filtered_top_base[
        filtered_top_base["target_group"].isin(["mother", "both"])
        | (
            (filtered_top_base["is_baby_friendly"] == True)
            & (filtered_top_base["min_age_months"] <= 11)
            & (filtered_top_base["max_age_months"] >= 6)
        )
    ]

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Nutrient distribution by category")

    nutrient_options = sorted(filtered_dist_base["nutrient"].unique()) if not filtered_dist_base.empty else []
    selected_nutrient = st.selectbox(
        "Select a nutrient",
        nutrient_options,
        index=0 if nutrient_options else None,
        key="dist_nutrient",
    )

    filtered_dist = (
        filtered_dist_base[filtered_dist_base["nutrient"] == selected_nutrient].copy()
        if nutrient_options else filtered_dist_base
    )

    if filtered_dist.empty:
        st.warning("No data available for this selection.")
    else:
        filtered_dist = filtered_dist.sort_values("avg_value_per_100g", ascending=False)

        st.bar_chart(
            filtered_dist.set_index("category")["avg_value_per_100g"],
            use_container_width=True,
        )

        if audience == "Baby under 1":
            st.info(
                f"💡 Insight: For babies aged {selected_age} months, {selected_nutrient} is most concentrated in **{filtered_dist.iloc[0]['category']}** foods."
            )
        elif audience == "Mother":
            st.info(
                f"💡 Insight: For mothers, {selected_nutrient} is most concentrated in **{filtered_dist.iloc[0]['category']}** foods."
            )
        else:
            st.info(
                f"💡 Insight: Across mother and baby-friendly foods, {selected_nutrient} is most concentrated in **{filtered_dist.iloc[0]['category']}** foods."
            )

        st.dataframe(filtered_dist, use_container_width=True)

with col2:
    st.markdown("### Top foods by nutrient")

    nutrient_options_top = sorted(filtered_top_base["nutrient"].unique()) if not filtered_top_base.empty else []
    selected_top_nutrient = st.selectbox(
        "Select a nutrient for top foods",
        nutrient_options_top,
        index=0 if nutrient_options_top else None,
        key="top_nutrient",
    )

    filtered_top = (
        filtered_top_base[filtered_top_base["nutrient"] == selected_top_nutrient].copy()
        if nutrient_options_top else filtered_top_base
    )

    if filtered_top.empty:
        st.warning("No data available for this selection.")
    else:
        filtered_top = filtered_top.sort_values("nutrient_rank", ascending=True)

        chart_df = filtered_top[["food_name", "value_per_100g"]].set_index("food_name")

        st.bar_chart(
            chart_df["value_per_100g"],
            use_container_width=True,
        )

        top_food = filtered_top.iloc[0]["food_name"]
        texture = filtered_top.iloc[0]["texture_stage"]

        if audience == "Baby under 1":
            st.info(
                f"🥇 Top {selected_top_nutrient} source for babies aged {selected_age} months: **{top_food}** ({texture})"
            )
        elif audience == "Mother":
            st.info(
                f"🥇 Top {selected_top_nutrient} source for mothers: **{top_food}**"
            )
        else:
            st.info(
                f"🥇 Top {selected_top_nutrient} source across mother and baby-friendly foods: **{top_food}**"
            )

        st.dataframe(filtered_top, use_container_width=True)

st.markdown("---")
st.caption("Built with Bruin + BigQuery + Streamlit + Terraform")