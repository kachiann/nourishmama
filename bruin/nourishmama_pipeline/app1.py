from pathlib import Path
import duckdb
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[2] / "nourishmama.duckdb"

if not DB_PATH.exists():
    st.error(f"❌ DuckDB not found at: {DB_PATH}")
    st.stop()

st.set_page_config(
    page_title="NourishMama",
    page_icon="🌱",
    layout="wide",
)

st.markdown(
    """
    # 🌱 NourishMama
    ### Nutrition insights for nursing mothers and baby-friendly foods under 1 year
    """
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # Core recommendation table — one row per food, pivoted nutrients + score
    recommendations_df = con.execute("""
        SELECT * FROM marts.meal_recommendations
    """).df()

    # Report tables for distribution and top-foods charts
    dist_df = con.execute("""
        SELECT * FROM reports.nutrient_category_distribution
    """).df()

    top_df = con.execute("""
        SELECT * FROM reports.top_foods_by_nutrient
    """).df()

    # Stage-level summary cards
    stage_df = con.execute("""
        SELECT * FROM reports.feeding_insights_by_stage
        ORDER BY min_age_months
    """).df()

    con.close()
    return recommendations_df, dist_df, top_df, stage_df


rec_df, dist_df, top_df, stage_df = load_data()

# -----------------------------
# KPI SECTION
# -----------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Foods", rec_df["food_id"].nunique())
col2.metric("Nutrients Tracked", len([
    c for c in rec_df.columns
    if c.endswith(("_g", "_mg", "_mcg"))
]))
col3.metric("Food Categories", rec_df["category"].nunique())

st.markdown("Use filters below to explore nutrition insights.")

# -----------------------------
# AUDIENCE + AGE FILTERS
# -----------------------------
audience = st.radio(
    "View nutrition insights for:",
    ["Baby under 1", "Mother", "Both"],
    horizontal=True,
)

selected_age = None
selected_texture = None

if audience == "Baby under 1":
    col_age, col_tex = st.columns(2)

    with col_age:
        selected_age = st.selectbox(
            "Baby age (months)",
            list(range(4, 12)),
            index=2,  # default to 6 months
        )

    with col_tex:
        texture_options = ["Any"] + sorted(
            rec_df[rec_df["is_baby_friendly"]]["texture_stage"]
            .dropna()
            .unique()
            .tolist()
        )
        selected_texture = st.selectbox("Texture stage", texture_options)


# -----------------------------
# FILTER HELPERS
# -----------------------------
def filter_recommendations(df):
    if audience == "Baby under 1":
        df = df[
            df["is_baby_friendly"] &
            df["is_texture_safe"] &
            (df["min_age_months"] <= selected_age) &
            (df["max_age_months"] >= selected_age)
        ]
        if selected_texture and selected_texture != "Any":
            df = df[df["texture_stage"] == selected_texture]
    elif audience == "Mother":
        df = df[df["target_group"].isin(["mother", "both"])]
    else:
        df = df[
            df["target_group"].isin(["mother", "both"]) |
            (df["is_baby_friendly"] & df["is_texture_safe"])
        ]
    return df.sort_values("nutrition_score", ascending=False)


def filter_reports(df):
    if audience == "Baby under 1":
        return df[
            df["is_baby_friendly"] &
            (df["min_age_months"] <= selected_age) &
            (df["max_age_months"] >= selected_age)
        ]
    elif audience == "Mother":
        return df[df["target_group"].isin(["mother", "both"])]
    else:
        return df


filtered_rec = filter_recommendations(rec_df.copy())
filtered_dist = filter_reports(dist_df.copy())
filtered_top = filter_reports(top_df.copy())

# -----------------------------
# TAB LAYOUT
# -----------------------------
tab1, tab2, tab3 = st.tabs([
    "🥗 Meal Recommendations",
    "📊 Nutrient Analysis",
    "📅 Developmental Stages",
])

# =============================
# TAB 1: MEAL RECOMMENDATIONS
# =============================
with tab1:
    st.markdown("### Recommended Foods")

    if filtered_rec.empty:
        st.warning("No foods match the current filters.")
    else:
        # Summary insight
        top_food = filtered_rec.iloc[0]
        st.success(
            f"🥇 Top pick: **{top_food['food_name']}** "
            f"— highest in **{top_food['top_nutrient']}** "
            f"({top_food['top_nutrient_value']} {top_food['top_nutrient_unit']} per 100g)"
        )

        # Recommendation cards (top 6)
        card_cols = st.columns(3)
        for i, (_, row) in enumerate(filtered_rec.head(6).iterrows()):
            with card_cols[i % 3]:
                tags = list(row["recommendation_tags"]) if row["recommendation_tags"] is not None else []
                tag_str = "  ".join([f"`{t}`" for t in tags[:3]])
                st.markdown(
                    f"**{row['food_name']}**  \n"
                    f"{row['category']} · {row['texture_stage']}  \n"
                    f"Score: `{row['nutrition_score']:.1f}`  \n"
                    f"{tag_str}"
                )

        st.markdown("---")
        st.markdown("#### Full list")

        display_cols = [
            "food_name", "category", "texture_stage", "developmental_stage",
            "nutrition_score", "top_nutrient",
            "protein_g", "iron_mg", "calcium_mg",
            "vitamin_c_mg", "omega3_g", "fiber_g",
            "recommendation_tags",
        ]
        st.dataframe(
            filtered_rec[display_cols].reset_index(drop=True),
            use_container_width=True,
        )

# =============================
# TAB 2: NUTRIENT ANALYSIS
# =============================
with tab2:
    col_left, col_right = st.columns(2)

    # --- Distribution chart ---
    with col_left:
        st.markdown("### Nutrient distribution by category")

        nutrient_options = sorted(filtered_dist["nutrient"].unique()) if not filtered_dist.empty else []

        if not nutrient_options:
            st.warning("No nutrient data for this selection.")
        else:
            selected_nutrient = st.selectbox(
                "Select nutrient",
                nutrient_options,
                key="dist_nutrient_select",
            )

            chart_data = (
                filtered_dist[filtered_dist["nutrient"] == selected_nutrient]
                .sort_values("avg_value_per_100g", ascending=False)
            )

            if not chart_data.empty:
                st.bar_chart(
                    chart_data.set_index("category")["avg_value_per_100g"],
                    use_container_width=True,
                )
                st.info(
                    f"💡 Top category for **{selected_nutrient}**: "
                    f"**{chart_data.iloc[0]['category']}** "
                    f"(avg {chart_data.iloc[0]['avg_value_per_100g']:.1f} per 100g)"
                )
                st.dataframe(chart_data, use_container_width=True)

    # --- Top foods chart ---
    with col_right:
        st.markdown("### Top foods by nutrient")

        nutrient_options_top = sorted(filtered_top["nutrient"].unique()) if not filtered_top.empty else []

        if not nutrient_options_top:
            st.warning("No top food data for this selection.")
        else:
            selected_top_nutrient = st.selectbox(
                "Select nutrient",
                nutrient_options_top,
                key="top_nutrient_select",
            )

            chart_top = (
                filtered_top[filtered_top["nutrient"] == selected_top_nutrient]
                .sort_values("nutrient_rank")
            )

            if not chart_top.empty:
                st.bar_chart(
                    chart_top.set_index("food_name")["value_per_100g"],
                    use_container_width=True,
                )
                st.info(
                    f"🥇 Top **{selected_top_nutrient}** source: "
                    f"**{chart_top.iloc[0]['food_name']}** "
                    f"({chart_top.iloc[0]['texture_stage']})"
                )
                st.dataframe(chart_top, use_container_width=True)

# =============================
# TAB 3: DEVELOPMENTAL STAGES
# =============================
with tab3:
    st.markdown("### Feeding insights by developmental stage")

    if stage_df.empty:
        st.warning("No stage data available.")
    else:
        for _, row in stage_df.iterrows():
            with st.expander(
                f"**{row['developmental_stage']}** — {row['available_food_count']} foods available",
                expanded=True,
            ):
                s1, s2, s3 = st.columns(3)
                s1.metric("Top Pick", row["top_food"])
                s2.metric("Avg Nutrition Score", f"{row['avg_nutrition_score']:.1f}")
                s3.metric("Nutrients Tracked (avg)", f"{row['avg_nutrients_tracked']:.0f}")

                tags = [
                    t for t in [row.get("primary_tag"), row.get("secondary_tag"), row.get("tertiary_tag")]
                    if t
                ]
                if tags:
                    st.markdown("**Key nutrients:** " + "  ".join([f"`{t}`" for t in tags]))

st.markdown("---")
st.caption("Built with Bruin · DuckDB · Streamlit")