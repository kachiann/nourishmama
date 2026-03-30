"""
NourishMama — USDA FoodData Central ingestion
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
GCS_BUCKET = os.environ.get("GCS_BUCKET", "nourishmum-project-nourishmum-lake")
GCS_PREFIX = "raw"

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
    print(f"  Uploaded gs://{bucket_name}/{blob_name}  ({len(data):,} bytes)")


def main() -> None:
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"[{run_date}] Downloading USDA FDC bundle...")

    response = requests.get(USDA_URL, stream=True, timeout=300)
    response.raise_for_status()

    raw_bytes = response.content
    print(f"  Downloaded {len(raw_bytes):,} bytes")

    gcs_client = storage.Client()
    uploaded = []

    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        for member in zf.namelist():
            filename = os.path.basename(member)
            if filename in TARGET_FILES:
                print(f"  Extracting {filename}...")
                csv_bytes = zf.read(member)

                # versioned path: raw/2024-10-31/food.csv
                blob_name = f"{GCS_PREFIX}/{run_date}/{filename}"
                upload_to_gcs(gcs_client, GCS_BUCKET, blob_name, csv_bytes)

                # latest symlink path: raw/latest/food.csv
                latest_blob = f"{GCS_PREFIX}/latest/{filename}"
                upload_to_gcs(gcs_client, GCS_BUCKET, latest_blob, csv_bytes)
                uploaded.append(filename)

    missing = TARGET_FILES - set(uploaded)
    if missing:
        raise RuntimeError(f"Missing expected files in zip: {missing}")

    print(f"\nIngestion complete. {len(uploaded)} files uploaded for run_date={run_date}")


if __name__ == "__main__":
    main()
