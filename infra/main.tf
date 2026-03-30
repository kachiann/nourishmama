terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "nourishmama_data" {
  name          = var.bucket_name
  location      = var.location
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "datasets" {
  for_each   = toset(var.datasets)
  dataset_id = each.value
  location   = var.location
}