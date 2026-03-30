variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west3"
}

variable "bucket_name" {
  description = "GCS bucket name"
  type        = string
}

variable "datasets" {
  description = "BigQuery datasets"
  type        = list(string)
  default     = ["raw", "staging", "marts", "reports"]
}

variable "location" {
  description = "Shared location for GCS and BigQuery"
  type        = string
  default     = "EU"
}