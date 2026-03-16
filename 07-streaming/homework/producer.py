"""
Q2: Send green taxi trip data to the green-trips Kafka topic.

Usage:
    # First create the topic:
    docker exec -it workshop-redpanda-1 rpk topic create green-trips

    # Then run the producer:
    uv run python producer.py
"""

import json
from time import time

import pandas as pd
from kafka import KafkaProducer

url = "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-10.parquet"

columns = [
    "lpep_pickup_datetime",
    "lpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
    "trip_distance",
    "tip_amount",
    "total_amount",
]

df = pd.read_parquet(url, columns=columns)
print(f"Read {len(df)} rows")


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=json_serializer,
)

t0 = time()

topic_name = "green-trips"

for idx, row in df.iterrows():
    message = {
        "lpep_pickup_datetime": str(row["lpep_pickup_datetime"]),
        "lpep_dropoff_datetime": str(row["lpep_dropoff_datetime"]),
        "PULocationID": int(row["PULocationID"]),
        "DOLocationID": int(row["DOLocationID"]),
        "passenger_count": float(row["passenger_count"]) if pd.notna(row["passenger_count"]) else 0.0,
        "trip_distance": float(row["trip_distance"]),
        "tip_amount": float(row["tip_amount"]),
        "total_amount": float(row["total_amount"]),
    }
    producer.send(topic_name, value=message)

    if (idx + 1) % 10000 == 0:
        print(f"Sent {idx + 1} rows...")

producer.flush()

t1 = time()
print(f"Sent {len(df)} rows")
print(f"took {(t1 - t0):.2f} seconds")
