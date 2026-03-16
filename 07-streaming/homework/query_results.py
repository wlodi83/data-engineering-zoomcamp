"""
Query PostgreSQL for Flink job results (Q4-Q6).

Usage:
    uv run python query_results.py
"""

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres",
)
cur = conn.cursor()

# Q4: Tumbling window - which PULocationID had the most trips?
print("=" * 60)
print("Q4: Top PULocationID by trips in a 5-minute tumbling window")
print("=" * 60)
cur.execute("""
    SELECT PULocationID, num_trips
    FROM green_trips_tumbling_pu
    ORDER BY num_trips DESC
    LIMIT 5;
""")
for row in cur.fetchall():
    print(f"  PULocationID={row[0]}, num_trips={row[1]}")

# Q5: Session window - longest session
print()
print("=" * 60)
print("Q5: Longest session (most trips in a single session)")
print("=" * 60)
cur.execute("""
    SELECT PULocationID, num_trips, window_start, window_end
    FROM green_trips_session_pu
    ORDER BY num_trips DESC
    LIMIT 5;
""")
for row in cur.fetchall():
    print(f"  PULocationID={row[0]}, num_trips={row[1]}, "
          f"window_start={row[2]}, window_end={row[3]}")

# Q6: Tumbling window - hour with highest total tips
print()
print("=" * 60)
print("Q6: Hour with highest total tip amount")
print("=" * 60)
cur.execute("""
    SELECT window_start, total_tips
    FROM green_trips_tips_hourly
    ORDER BY total_tips DESC
    LIMIT 5;
""")
for row in cur.fetchall():
    print(f"  window_start={row[0]}, total_tips={row[1]:.2f}")

cur.close()
conn.close()
