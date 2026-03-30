"""@bruin
name: raw.usda_food_nutrient
type: python
connection: gcp-default
depends:
  - ingestion.usda_foundation_to_gcs

materialization:
  type: table
@bruin"""

from google.cloud import bigquery

PROJECT_ID = "nourishmama-project"
DATASET_ID = "raw"
TABLE_ID = "usda_food_nutrient"
GCS_URI = "gs://nourishmama-project-datalake-eu/raw/usda_foundation/latest/food_nutrient.csv"


def materialize():
    client = bigquery.Client(project=PROJECT_ID)

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_uri(GCS_URI, table_ref, job_config=job_config)
    job.result()

    table = client.get_table(table_ref)
    return [{
        "table_name": table_ref,
        "row_count": table.num_rows,
        "source_uri": GCS_URI,
    }]