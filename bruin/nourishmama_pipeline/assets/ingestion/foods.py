"""@bruin
name: ingestion.foods
type: python
connection: duckdb_local
materialization:
  type: table
@bruin"""
from pathlib import Path
import pandas as pd


def materialize():
    csv_path = Path(__file__).with_name("foods.csv")
    df = pd.read_csv(csv_path)
    df["food_id"] = df["food_id"].astype(int)
    df["food_name"] = df["food_name"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    df["target_group"] = df["target_group"].astype(str).str.strip()
    df["is_baby_friendly"] = df["is_baby_friendly"].map(
        {"TRUE": True, "FALSE": False, True: True, False: False}
    ).astype(bool)
    df["texture_stage"] = df["texture_stage"].astype(str).str.strip()
    df["min_age_months"] = df["min_age_months"].astype(int)
    df["max_age_months"] = df["max_age_months"].astype(int)
    return df