output "s3_bucket_name" {
  description = "Data lake S3 bucket"
  value       = aws_s3_bucket.data_lake.id
}

output "s3_bucket_arn" {
  description = "Data lake S3 bucket ARN"
  value       = aws_s3_bucket.data_lake.arn
}

output "glue_database" {
  description = "Glue catalog database name"
  value       = aws_glue_catalog_database.analytics.name
}

output "athena_workgroup" {
  description = "Athena workgroup name"
  value       = aws_athena_workgroup.analytics.name
}

output "pipeline_role_arn" {
  description = "IAM role ARN for the pipeline pod (use in Helm values)"
  value       = aws_iam_role.pipeline.arn
}
