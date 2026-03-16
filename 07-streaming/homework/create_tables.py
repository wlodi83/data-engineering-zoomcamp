"""
Create PostgreSQL tables for Flink job results (Q4-Q6).

Usage:
    uv run python create_tables.py
"""

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres",
)
conn.autocommit = True
cur = conn.cursor()

# Q4: Tumbling window - trips per pickup location
cur.execute("""
    DROP TABLE IF EXISTS green_trips_tumbling_pu;
    CREATE TABLE green_trips_tumbling_pu (
        window_start TIMESTAMP(3),
        PULocationID INT,
        num_trips BIGINT,
        PRIMARY KEY (window_start, PULocationID)
    );
""")
print("Created table: green_trips_tumbling_pu")

# Q5: Session window - trips per pickup location
cur.execute("""
    DROP TABLE IF EXISTS green_trips_session_pu;
    CREATE TABLE green_trips_session_pu (
        window_start TIMESTAMP(3),
        window_end TIMESTAMP(3),
        PULocationID INT,
        num_trips BIGINT,
        PRIMARY KEY (window_start, PULocationID)
    );
""")
print("Created table: green_trips_session_pu")

# Q6: Tumbling window - tips per hour
cur.execute("""
    DROP TABLE IF EXISTS green_trips_tips_hourly;
    CREATE TABLE green_trips_tips_hourly (
        window_start TIMESTAMP(3),
        total_tips DOUBLE PRECISION,
        PRIMARY KEY (window_start)
    );
""")
print("Created table: green_trips_tips_hourly")

cur.close()
conn.close()
print("\nAll tables created successfully.")
