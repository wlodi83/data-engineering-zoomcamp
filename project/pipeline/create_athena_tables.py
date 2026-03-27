"""Create Athena external tables pointing at S3 Parquet files."""

import boto3
import time

REGION = "eu-central-1"
DATABASE = "pushmetrics_analytics"
WORKGROUP = "pushmetrics-analytics"
S3_BASE = "s3://pushmetrics-analytics-lake/raw/raw"

athena = boto3.client("athena", region_name=REGION)

TABLES = {
    "workflow": """
        id BIGINT,
        workspace_id BIGINT,
        cron_rule STRING,
        is_active BOOLEAN,
        created_on TIMESTAMP,
        changed_on TIMESTAMP,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "workflow_log": """
        id BIGINT,
        workflow_id BIGINT,
        status STRING,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        progress DOUBLE,
        created_on TIMESTAMP,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "noteflow_run": """
        id BIGINT,
        workspace_id BIGINT,
        status STRING,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        created_on TIMESTAMP,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "noteflow_run_task": """
        id BIGINT,
        noteflow_run_id BIGINT,
        task_name STRING,
        status STRING,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        created_on TIMESTAMP,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "block_execution": """
        id BIGINT,
        block_id BIGINT,
        block_type STRING,
        status STRING,
        start_date TIMESTAMP,
        end_date TIMESTAMP,
        created_on TIMESTAMP,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "report": """
        id BIGINT,
        workspace_id BIGINT,
        created_on TIMESTAMP,
        changed_on TIMESTAMP,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "report_block": """
        report_id BIGINT,
        block_id BIGINT,
        block_type STRING,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "block": """
        id BIGINT,
        type STRING,
        workspace_id BIGINT,
        created_on TIMESTAMP,
        changed_on TIMESTAMP,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
    "logs": """
        id BIGINT,
        action STRING,
        user_id STRING,
        dttm TIMESTAMP,
        duration_ms BIGINT,
        `_dlt_load_id` STRING,
        `_dlt_id` STRING
    """,
}


def run_query(sql: str) -> str:
    """Execute an Athena query and wait for completion."""
    response = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": DATABASE},
        WorkGroup=WORKGROUP,
    )
    execution_id = response["QueryExecutionId"]

    while True:
        result = athena.get_query_execution(QueryExecutionId=execution_id)
        state = result["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)

    if state != "SUCCEEDED":
        reason = result["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
        print(f"  FAILED: {reason}")
    return state


def main():
    for table_name, columns in TABLES.items():
        sql = f"""
        CREATE EXTERNAL TABLE IF NOT EXISTS {table_name} (
            {columns.strip()}
        )
        STORED AS PARQUET
        LOCATION '{S3_BASE}/{table_name}/'
        """
        print(f"Creating table {table_name}...", end=" ")
        state = run_query(sql)
        print(state)

    # Verify with a count query
    print("\n--- Row counts ---")
    for table_name in TABLES:
        sql = f"SELECT COUNT(*) as cnt FROM {table_name}"
        response = athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={"Database": DATABASE},
            WorkGroup=WORKGROUP,
        )
        execution_id = response["QueryExecutionId"]
        while True:
            result = athena.get_query_execution(QueryExecutionId=execution_id)
            state = result["QueryExecution"]["Status"]["State"]
            if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
                break
            time.sleep(1)

        if state == "SUCCEEDED":
            rows = athena.get_query_results(QueryExecutionId=execution_id)
            count = rows["ResultSet"]["Rows"][1]["Data"][0]["VarCharValue"]
            print(f"  {table_name}: {count} rows")
        else:
            reason = result["QueryExecution"]["Status"].get("StateChangeReason", "")
            print(f"  {table_name}: FAILED - {reason}")


if __name__ == "__main__":
    main()
