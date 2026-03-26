variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "s3_bucket_name" {
  description = "S3 bucket for the data lake"
  type        = string
  default     = "pushmetrics-analytics-lake"
}

variable "glue_database_name" {
  description = "Glue catalog database name"
  type        = string
  default     = "pushmetrics_analytics"
}

variable "athena_workgroup_name" {
  description = "Athena workgroup name"
  type        = string
  default     = "pushmetrics-analytics"
}

variable "eks_oidc_provider_arn" {
  description = "ARN of the EKS cluster OIDC provider (for IAM Roles for Service Accounts)"
  type        = string
}

variable "eks_oidc_provider" {
  description = "EKS OIDC provider URL (without https://)"
  type        = string
}
