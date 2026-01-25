variable "credentials" {
  description = "My Credentials"
  default     = "./keys/bquery-275621-369ff234bb9b.json"
}


variable "project" {
  description = "Project"
  default     = "bquery-275621"
}

variable "region" {
  description = "Region"
  default     = "europe-west3"
}

variable "location" {
  description = "Project Location"
  default     = "EU"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "demo_dataset_lw"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "terraform-demo-terra-bucket-lw"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}