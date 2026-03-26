"""dlt source definitions for PushMetrics operational data."""

import dlt
from dlt.sources.sql_database import sql_database

from pipeline.anonymize import ANONYMIZE_COLUMNS, DROP_COLUMNS, hash_id


# Tables to extract with their incremental columns
TABLES = {
    "workflow": {"cursor_column": "changed_on"},
    "workflow_log": {"cursor_column": "start_time"},
    "noteflow_run": {"cursor_column": "start_time"},
    "noteflow_run_task": {"cursor_column": "start_time"},
    "block_execution": {"cursor_column": "start_date"},
    "report": {"cursor_column": "changed_on"},
    "report_block": {"cursor_column": None},  # Full load (association table)
    "block": {"cursor_column": "changed_on"},
    "logs": {"cursor_column": "dttm"},
}


def anonymize_row(row: dict, table_name: str) -> dict:
    """Anonymize a single row: hash PII columns, drop sensitive columns."""
    row = dict(row)

    for col in ANONYMIZE_COLUMNS.get(table_name, []):
        if col in row:
            row[col] = hash_id(row[col])
    for col in DROP_COLUMNS.get(table_name, []):
        row.pop(col, None)

    return row


def _make_resource(table_name: str, config: dict):
    """Create a standalone dlt resource that reads from sql_database and anonymizes."""

    cursor_column = config["cursor_column"]

    if cursor_column:
        @dlt.resource(name=table_name, write_disposition="append")
        def _resource(
            last_value=dlt.sources.incremental(cursor_column),
        ):
            source = sql_database(
                credentials=dlt.secrets["sources.pushmetrics.credentials"],
                schema="public",
                table_names=[table_name],
                backend="sqlalchemy",
            )
            for row in source.resources[table_name]:
                yield anonymize_row(row, table_name)
    else:
        @dlt.resource(name=table_name, write_disposition="replace")
        def _resource():
            source = sql_database(
                credentials=dlt.secrets["sources.pushmetrics.credentials"],
                schema="public",
                table_names=[table_name],
                backend="sqlalchemy",
            )
            for row in source.resources[table_name]:
                yield anonymize_row(row, table_name)

    return _resource


@dlt.source(name="pushmetrics")
def pushmetrics_source():
    """dlt source that extracts operational tables from PushMetrics PostgreSQL."""
    for table_name, config in TABLES.items():
        yield _make_resource(table_name, config)
