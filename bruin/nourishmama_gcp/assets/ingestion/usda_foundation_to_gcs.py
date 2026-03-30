"""@bruin
name: ingestion.usda_foundation_to_gcs
type: python
connection: gcp-default
@bruin"""

"""
NourishMama USDA FoodData Central ingestion
Downloads the Foundation Foods CSV bundle and uploads to GCS raw zone.
"""

import io
import os
import zipfile
from datetime import datetime, timezone

import requests
from google.cloud import storage

USDA_URL = os.environ.get(
    "USDA_URL",
    "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_foundation_food_csv_2024-10-31.zip",
)
GCS_BUCKET = os.environ.get("GCS_BUCKET", "nourishmama-project-datalake-eu")
GCS_PREFIX = os.environ.get("GCS_PREFIX", "raw/usda_foundation")

TARGET_FILES = {
    "food.csv",
    "nutrient.csv",
    "food_nutrient.csv",
    "food_category.csv",
}


def upload_to_gcs(client: storage.Client, bucket_name: str, blob_name: str, data: bytes) -> None:
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data, content_type="text/csv")
    print(f"Uploaded gs://{bucket_name}/{blob_name} ({len(data):,} bytes)")


def extract_source_version(url: str) -> str:
    filename = os.path.basename(url)
    if "FoodData_Central_foundation_food_csv_" in filename:
        return filename.replace("FoodData_Central_foundation_food_csv_", "").replace(".zip", "")
    return "unknown"


def materialize():
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source_version = extract_source_version(USDA_URL)

    print(f"[{run_date}] Downloading USDA FDC bundle: {USDA_URL}")

    headers = {"User-Agent": "NourishMama/1.0"}
    response = requests.get(USDA_URL, timeout=300, headers=headers)
    response.raise_for_status()

    raw_bytes = response.content
    print(f"Downloaded {len(raw_bytes):,} bytes")

    gcs_client = storage.Client()
    uploaded = []

    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        for member in zf.namelist():
            filename = os.path.basename(member)
            if filename in TARGET_FILES:
                print(f"Extracting {filename}...")
                csv_bytes = zf.read(member)

                versioned_blob = (
                    f"{GCS_PREFIX}/source_version={source_version}/ingested_at={run_date}/{filename}"
                )
                latest_blob = f"{GCS_PREFIX}/latest/{filename}"

                upload_to_gcs(gcs_client, GCS_BUCKET, versioned_blob, csv_bytes)
                upload_to_gcs(gcs_client, GCS_BUCKET, latest_blob, csv_bytes)
                uploaded.append(filename)

    missing = TARGET_FILES - set(uploaded)
    if missing:
        raise RuntimeError(f"Missing expected files in zip: {missing}")

    print(f"Ingestion complete. Uploaded {len(uploaded)} files.")
    return [{
        "source_version": source_version,
        "ingested_at": run_date,
        "files_uploaded": len(uploaded),
        "bucket_name": GCS_BUCKET,
    }]


if __name__ == "__main__":
    materialize()