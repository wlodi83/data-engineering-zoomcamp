"""
Q3: Count trips with trip_distance > 5.0 km.

Usage:
    python3.12 consumer.py
"""

import json

from kafka import KafkaConsumer

server = "localhost:9092"
topic_name = "green-trips"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=[server],
    auto_offset_reset="earliest",
    group_id=None,  # no group = always read from beginning
    consumer_timeout_ms=10000,  # stop after 10s of no new messages
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

print(f"Listening to {topic_name}...")

count = 0
long_trips = 0

for message in consumer:
    trip = message.value
    count += 1
    if trip["trip_distance"] > 5.0:
        long_trips += 1

    if count % 10000 == 0:
        print(f"Processed {count} messages, long trips so far: {long_trips}")

print(f"\nTotal messages: {count}")
print(f"Trips with trip_distance > 5.0: {long_trips}")
