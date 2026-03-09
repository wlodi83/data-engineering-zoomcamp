from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlretrieve

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

YELLOW_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-11.parquet"
ZONES_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"


def download_if_missing(url: str, target_path: Path) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if not target_path.exists():
        print(f"Downloading {url} -> {target_path}")
        urlretrieve(url, target_path)
    return target_path


def parquet_file_sizes_mb(path: Path) -> list[float]:
    files = [p for p in path.rglob("*.parquet") if p.is_file()]
    return [p.stat().st_size / (1024 * 1024) for p in files]


def main() -> None:
    parser = argparse.ArgumentParser(description="DE Zoomcamp 2026 - Module 6 homework solver")
    parser.add_argument("--data-dir", default="data", help="Directory for input/output data")
    parser.add_argument(
        "--output-dir",
        default="data/yellow_2025_11_repartitioned",
        help="Directory where repartitioned parquet files will be written",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    yellow_path = data_dir / "yellow_tripdata_2025-11.parquet"
    zones_path = data_dir / "taxi_zone_lookup.csv"
    output_dir = Path(args.output_dir)

    download_if_missing(YELLOW_URL, yellow_path)
    download_if_missing(ZONES_URL, zones_path)

    spark = (
        SparkSession.builder.master("local[*]")
        .appName("de-zoomcamp-2026-hw6")
        .getOrCreate()
    )

    try:
        # Q1
        print(f"Q1 Spark version: {spark.version}")

        # Load yellow trips once for all tasks
        df = spark.read.parquet(str(yellow_path))

        # Q2
        if output_dir.exists():
            # Keep behavior deterministic by removing previous output files
            import shutil

            shutil.rmtree(output_dir)

        df.repartition(4).write.mode("overwrite").parquet(str(output_dir))
        sizes_mb = parquet_file_sizes_mb(output_dir)
        avg_size_mb = sum(sizes_mb) / len(sizes_mb) if sizes_mb else 0.0
        print(f"Q2 parquet files count: {len(sizes_mb)}")
        print(f"Q2 average parquet file size (MB): {avg_size_mb:.2f}")

        # Q3
        trips_on_15 = (
            df.where(F.to_date(F.col("tpep_pickup_datetime")) == F.lit("2025-11-15"))
            .count()
        )
        print(f"Q3 trips started on 2025-11-15: {trips_on_15}")

        # Q4
        longest_trip_hours = (
            df.select(
                (
                    (
                        F.unix_timestamp(F.col("tpep_dropoff_datetime"))
                        - F.unix_timestamp(F.col("tpep_pickup_datetime"))
                    )
                    / 3600.0
                ).alias("trip_hours")
            )
            .agg(F.max("trip_hours").alias("max_trip_hours"))
            .first()["max_trip_hours"]
        )
        print(f"Q4 longest trip (hours): {longest_trip_hours:.1f}")

        # Q5
        print("Q5 Spark UI local port: 4040")

        # Q6
        zones_df = spark.read.option("header", True).csv(str(zones_path))
        least_frequent_zone_row = (
            df.groupBy("PULocationID")
            .count()
            .join(
                zones_df,
                df.PULocationID == zones_df.LocationID.cast("int"),
                how="left",
            )
            .orderBy(F.col("count").asc(), F.col("Zone").asc())
            .select("Zone", "count")
            .first()
        )

        if least_frequent_zone_row is None:
            print("Q6 least frequent pickup zone: no data")
        else:
            print(
                "Q6 least frequent pickup zone: "
                f"{least_frequent_zone_row['Zone']} (count={least_frequent_zone_row['count']})"
            )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
