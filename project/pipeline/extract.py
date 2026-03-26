"""Main dlt extraction pipeline — PushMetrics PostgreSQL → S3 (Parquet)."""

import dlt

from pipeline.sources import pushmetrics_source


def run():
    """Run the extraction pipeline."""
    pipeline = dlt.pipeline(
        pipeline_name="pushmetrics_analytics",
        destination="filesystem",
        dataset_name="raw",
    )

    source = pushmetrics_source()

    info = pipeline.run(
        source,
        loader_file_format="parquet",
        write_disposition="merge",
    )

    print(f"Pipeline completed: {info}")
    print(f"Load info: {info.load_packages}")

    return info


if __name__ == "__main__":
    run()
