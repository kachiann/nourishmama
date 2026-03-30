output "bucket_name" {
  value = google_storage_bucket.nourishmama_data.name
}

output "dataset_names" {
  value = [for d in google_bigquery_dataset.datasets : d.dataset_id]
}