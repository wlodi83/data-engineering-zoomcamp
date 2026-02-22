"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append
@bruin"""

import json
import os
from datetime import datetime
from typing import List, Tuple

import pandas as pd
from dateutil.relativedelta import relativedelta

# NYC Taxi TLC data endpoint
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/"


def parse_date(date_str: str) -> datetime:
    """Parse a date string in various formats that Bruin may provide."""
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")


def generate_months_to_ingest(start_date: str, end_date: str) -> List[Tuple[int, int]]:
    """Generate a list of (year, month) tuples for the given date range."""
    start = parse_date(start_date)
    end = parse_date(end_date)

    months = []
    current = start.replace(day=1)
    while current <= end:
        months.append((current.year, current.month))
        current += relativedelta(months=1)

    return months


def build_parquet_url(taxi_type: str, year: int, month: int) -> str:
    """Build the TLC parquet file URL for a given taxi type and month."""
    return f"{BASE_URL}{taxi_type}_tripdata_{year}-{month:02d}.parquet"


def fetch_trip_data(taxi_type: str, year: int, month: int) -> pd.DataFrame:
    """Fetch a single parquet file and add a taxi_type column."""
    import requests
    from io import BytesIO

    url = build_parquet_url(taxi_type, year, month)
    print(f"Fetching {url}")

    response = requests.get(url)
    response.raise_for_status()

    df = pd.read_parquet(BytesIO(response.content))
    df["taxi_type"] = taxi_type
    print(f"  -> {len(df)} rows")

    return df


def materialize() -> pd.DataFrame:
    """Main entry point: fetch trip data for all taxi types and months in the date range."""
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    taxi_types = json.loads(os.environ.get("BRUIN_VARS", "{}")).get("taxi_types", ["yellow"])

    months = generate_months_to_ingest(start_date, end_date)
    print(f"Months to ingest: {months}")
    print(f"Taxi types: {taxi_types}")

    all_frames = []
    for year, month in months:
        for taxi_type in taxi_types:
            try:
                df = fetch_trip_data(taxi_type, year, month)
                all_frames.append(df)
            except Exception as e:
                print(f"  -> Failed: {e}, skipping")

    if all_frames:
        result = pd.concat(all_frames, ignore_index=True)
        result["extracted_at"] = datetime.utcnow()
        print(f"Total rows: {len(result)}")
        return result
    else:
        print("No data fetched")
        return pd.DataFrame()
