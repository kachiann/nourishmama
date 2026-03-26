"""@bruin
name: ingestion.mother_nutrition
type: python
connection: duckdb_local

materialization:
  type: table
@bruin"""

from pathlib import Path
import pandas as pd


def materialize():
    csv_path = Path(__file__).with_name("mother_nutrition.csv")
    df = pd.read_csv(csv_path)

    df["food_id"] = df["food_id"].astype(int)
    df["food_name"] = df["food_name"].astype(str)
    df["category"] = df["category"].astype(str)
    df["nutrient"] = df["nutrient"].astype(str)
    df["value_per_100g"] = df["value_per_100g"].astype(float)
    df["unit"] = df["unit"].astype(str)
    df["target_group"] = df["target_group"].astype(str)
    df["is_baby_friendly"] = df["is_baby_friendly"].astype(bool)
    df["min_age_months"] = df["min_age_months"].astype(int)
    df["max_age_months"] = df["max_age_months"].astype(int)
    df["texture_stage"] = df["texture_stage"].astype(str)

    return df