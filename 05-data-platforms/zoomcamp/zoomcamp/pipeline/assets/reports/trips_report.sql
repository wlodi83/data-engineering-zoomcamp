/* @bruin

name: reports.trips_report
type: duckdb.sql
depends:
  - staging.trips

materialization:
  type: table

columns:
  - name: trip_date
    type: date
    description: "Trip date"
    primary_key: true
    checks:
      - name: not_null
  - name: taxi_type
    type: string
    description: "Type of taxi (yellow, green)"
    primary_key: true
    checks:
      - name: not_null
  - name: payment_type_name
    type: string
    description: "Payment method name"
    primary_key: true
  - name: trip_count
    type: bigint
    description: "Number of trips"
    checks:
      - name: positive
  - name: total_passengers
    type: bigint
    description: "Total passenger count"
    checks:
      - name: non_negative
  - name: total_distance
    type: float
    description: "Sum of trip distances"
    checks:
      - name: non_negative
  - name: total_fare
    type: float
    description: "Sum of fare amounts"
    checks:
      - name: non_negative
  - name: total_tips
    type: float
    description: "Sum of tip amounts"
    checks:
      - name: non_negative
  - name: total_revenue
    type: float
    description: "Sum of total amounts"
    checks:
      - name: non_negative
  - name: avg_fare
    type: float
    description: "Average fare per trip"
    checks:
      - name: non_negative
  - name: avg_trip_distance
    type: float
    description: "Average trip distance"
    checks:
      - name: non_negative
  - name: avg_passengers
    type: float
    description: "Average passengers per trip"
    checks:
      - name: non_negative

custom_checks:
  - name: row_count_positive
    description: Ensure the table is not empty
    query: SELECT COUNT(*) > 0 FROM reports.trips_report
    value: 1

@bruin */

-- Aggregate trips by date, taxi type, and payment type
SELECT
    CAST(pickup_datetime AS DATE) AS trip_date,
    taxi_type,
    payment_type_name,

    -- Count metrics
    COUNT(*) AS trip_count,
    SUM(COALESCE(passenger_count, 0)) AS total_passengers,

    -- Distance metrics
    SUM(COALESCE(trip_distance, 0)) AS total_distance,

    -- Revenue metrics
    SUM(COALESCE(fare_amount, 0)) AS total_fare,
    SUM(COALESCE(tip_amount, 0)) AS total_tips,
    SUM(COALESCE(total_amount, 0)) AS total_revenue,

    -- Average metrics
    AVG(COALESCE(fare_amount, 0)) AS avg_fare,
    AVG(COALESCE(trip_distance, 0)) AS avg_trip_distance,
    AVG(COALESCE(passenger_count, 0)) AS avg_passengers
FROM staging.trips
WHERE pickup_datetime >= '{{ start_datetime }}'
  AND pickup_datetime < '{{ end_datetime }}'
GROUP BY
    CAST(pickup_datetime AS DATE),
    taxi_type,
    payment_type_name
