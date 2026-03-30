"""@bruin
name: raw.usda_food
type: python
connection: gcp-default
depends:
  - ingestion.usda_foundation_to_gcs

materialization:
  type: table
@bruin"""

import io

import pandas as pd
from google.cloud import bigquery, storage

PROJECT_ID = "nourishmama-project"
BUCKET_NAME = "nourishmama-project-datalake-eu"
BLOB_NAME = "raw/usda_foundation/latest/food.csv"
TABLE_ID = f"{PROJECT_ID}.raw.usda_food"


def materialize():
    # Download from GCS
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    csv_bytes = blob.download_as_bytes()

    # Read as raw strings to avoid date/quote parsing issues
    df = pd.read_csv(
        io.BytesIO(csv_bytes),
        dtype=str,
        engine="python",
        keep_default_na=False,
        on_bad_lines="warn",
    )

    # Normalize column names a bit
    df.columns = [c.strip().lower() for c in df.columns]

    # Load to BigQuery as raw strings
    bq_client = bigquery.Client(project=PROJECT_ID)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )

    job = bq_client.load_table_from_dataframe(df, TABLE_ID, job_config=job_config)
    job.result()

    table = bq_client.get_table(TABLE_ID)

    return [{
        "table_name": TABLE_ID,
        "row_count": table.num_rows,
        "source_blob": f"gs://{BUCKET_NAME}/{BLOB_NAME}",
    }]