"""Prefect flow for the PushMetrics analytics pipeline.

Orchestrates: dlt extraction → dbt transformations
Deployed as a Prefect work pool on EKS, scheduled daily at 4am UTC.
"""

import subprocess

from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta

from pipeline.extract import run as run_extraction


@task(
    name="dlt-extract",
    retries=2,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1),
    log_prints=True,
)
def extract():
    """Extract data from PushMetrics PostgreSQL → S3 Parquet."""
    logger = get_run_logger()
    logger.info("Starting dlt extraction...")

    info = run_extraction()

    logger.info(f"Extraction complete: {info.load_packages}")
    return info


@task(
    name="dbt-transform",
    retries=1,
    retry_delay_seconds=30,
    log_prints=True,
)
def transform():
    """Run dbt transformations (staging → marts) on Athena."""
    logger = get_run_logger()
    logger.info("Starting dbt transformations...")

    result = subprocess.run(
        ["dbt", "run", "--project-dir", "transform", "--profiles-dir", "transform"],
        capture_output=True,
        text=True,
    )

    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(f"dbt run failed: {result.stderr}")

    return result.stdout


@task(
    name="dbt-test",
    log_prints=True,
)
def test_transforms():
    """Run dbt tests to validate data quality."""
    logger = get_run_logger()
    logger.info("Running dbt tests...")

    result = subprocess.run(
        ["dbt", "test", "--project-dir", "transform", "--profiles-dir", "transform"],
        capture_output=True,
        text=True,
    )

    logger.info(result.stdout)
    if result.returncode != 0:
        logger.warning(f"dbt tests had failures: {result.stderr}")

    return result.stdout


@flow(
    name="pushmetrics-analytics",
    description="Daily PushMetrics platform analytics: extract → transform → test",
    log_prints=True,
)
def analytics_pipeline():
    """Main pipeline flow: extract from PostgreSQL, transform with dbt, validate."""
    logger = get_run_logger()
    logger.info("=== PushMetrics Analytics Pipeline ===")

    # Step 1: Extract
    extract_result = extract()

    # Step 2: Transform (depends on extraction)
    transform_result = transform(wait_for=[extract_result])

    # Step 3: Test data quality (depends on transform)
    test_result = test_transforms(wait_for=[transform_result])

    logger.info("=== Pipeline complete ===")
    return {
        "extract": str(extract_result),
        "transform": transform_result,
        "tests": test_result,
    }


if __name__ == "__main__":
    analytics_pipeline()
