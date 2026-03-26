"""DuckDB exploration of the S3 data lake (Parquet files).

Use this for ad-hoc analysis without incurring Athena query costs.
Can read from local Parquet files or directly from S3.
"""

import os
import duckdb


S3_BUCKET = os.environ.get("S3_BUCKET", "pushmetrics-analytics-lake")
DATA_PATH = os.environ.get("DATA_PATH", f"s3://{S3_BUCKET}/raw/")


def get_connection() -> duckdb.DuckDBPyConnection:
    """Create a DuckDB connection with S3 support."""
    con = duckdb.connect()

    # Configure S3 access (uses AWS env vars or IAM role)
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute(f"SET s3_region='{os.environ.get('AWS_REGION', 'eu-central-1')}';")

    return con


def workflow_health_summary(con: duckdb.DuckDBPyConnection):
    """Quick workflow health check."""
    query = f"""
    SELECT
        status,
        COUNT(*) as count,
        AVG(EPOCH(end_time - start_time)) as avg_duration_sec,
        MIN(start_time) as earliest,
        MAX(start_time) as latest
    FROM read_parquet('{DATA_PATH}workflow_log/*.parquet')
    WHERE start_time IS NOT NULL
    GROUP BY status
    ORDER BY count DESC
    """
    print("\n=== Workflow Health Summary ===")
    print(con.execute(query).fetchdf().to_string())


def block_type_distribution(con: duckdb.DuckDBPyConnection):
    """Block type usage distribution."""
    query = f"""
    SELECT
        block_type,
        COUNT(*) as executions,
        AVG(EPOCH(end_date - start_date)) as avg_duration_sec,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
        COUNT(CASE WHEN status IN ('failed', 'error') THEN 1 END) as failed
    FROM read_parquet('{DATA_PATH}block_execution/*.parquet')
    WHERE start_date IS NOT NULL
    GROUP BY block_type
    ORDER BY executions DESC
    """
    print("\n=== Block Type Distribution ===")
    print(con.execute(query).fetchdf().to_string())


def daily_activity(con: duckdb.DuckDBPyConnection):
    """Daily platform activity overview."""
    query = f"""
    SELECT
        DATE_TRUNC('day', start_time) as day,
        COUNT(*) as runs,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
        COUNT(CASE WHEN status IN ('failed', 'error') THEN 1 END) as failed
    FROM read_parquet('{DATA_PATH}noteflow_run/*.parquet')
    WHERE start_time IS NOT NULL
    GROUP BY day
    ORDER BY day DESC
    LIMIT 30
    """
    print("\n=== Daily Activity (Last 30 Days) ===")
    print(con.execute(query).fetchdf().to_string())


if __name__ == "__main__":
    con = get_connection()
    workflow_health_summary(con)
    block_type_distribution(con)
    daily_activity(con)
    con.close()
