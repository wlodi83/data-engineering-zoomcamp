/* @bruin

name: staging.trips
type: duckdb.sql
depends:
  - ingestion.trips
  - ingestion.payment_lookup

materialization:
  type: table

columns:
  - name: pickup_datetime
    type: timestamp
    description: "When the trip started"
    primary_key: true
    checks:
      - name: not_null
  - name: dropoff_datetime
    type: timestamp
    description: "When the trip ended"
    primary_key: true
    checks:
      - name: not_null
  - name: pickup_location_id
    type: integer
    description: "TLC pickup location ID"
    primary_key: true
  - name: dropoff_location_id
    type: integer
    description: "TLC dropoff location ID"
    primary_key: true
  - name: fare_amount
    type: float
    description: "Base fare in USD"
    primary_key: true
    checks:
      - name: not_null
  - name: taxi_type
    type: string
    description: "Type of taxi (yellow, green)"
    checks:
      - name: not_null
      - name: accepted_values
        value:
          - yellow
          - green
  - name: payment_type_name
    type: string
    description: "Payment method name from lookup"

custom_checks:
  - name: row_count_positive
    description: Ensure the table is not empty
    query: SELECT COUNT(*) > 0 FROM staging.trips
    value: 1

@bruin */

WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY
                tpep_pickup_datetime,
                tpep_dropoff_datetime,
                pu_location_id,
                do_location_id,
                fare_amount,
                taxi_type
            ORDER BY extracted_at DESC
        ) AS row_num
    FROM ingestion.trips
    WHERE tpep_pickup_datetime >= '{{ start_datetime }}'
      AND tpep_pickup_datetime < '{{ end_datetime }}'
)

SELECT
    d.tpep_pickup_datetime AS pickup_datetime,
    d.tpep_dropoff_datetime AS dropoff_datetime,
    d.pu_location_id AS pickup_location_id,
    d.do_location_id AS dropoff_location_id,
    d.passenger_count,
    d.trip_distance,
    d.fare_amount,
    d.tip_amount,
    d.total_amount,
    d.payment_type,
    p.payment_type_name,
    d.taxi_type,
    d.extracted_at
FROM deduplicated d
LEFT JOIN ingestion.payment_lookup p
    ON d.payment_type = p.payment_type_id
WHERE d.row_num = 1
