"""@bruin
name: ingestion.food_nutrients
type: python
connection: duckdb_local
materialization:
  type: table
@bruin"""

from pathlib import Path
import pandas as pd


def materialize():
    csv_path = Path(__file__).with_name("food_nutrients.csv")
    df = pd.read_csv(csv_path)
    df["food_id"] = df["food_id"].astype(int)
    df["nutrient"] = df["nutrient"].astype(str).str.strip()
    df["value_per_100g"] = df["value_per_100g"].astype(float)
    df["unit"] = df["unit"].astype(str).str.strip()
    return df