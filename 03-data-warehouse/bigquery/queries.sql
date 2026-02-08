CREATE OR REPLACE EXTERNAL TABLE `bquery-275621.03_homework.yellow_taxi_trip_ext`
OPTIONS (
  format = 'parquet',
  uris = ['gs://zoomcamp-lw/yellow_tripdata_2024-01.parquet', 'gs://zoomcamp-lw/yellow_tripdata_2024-02.parquet', 'gs://zoomcamp-lw/yellow_tripdata_2024-03.parquet', 'gs://zoomcamp-lw/yellow_tripdata_2024-04.parquet', 'gs://zoomcamp-lw/yellow_tripdata_2024-05.parquet',
  'gs://zoomcamp-lw/yellow_tripdata_2024-06.parquet']
);


CREATE OR REPLACE TABLE `bquery-275621.03_homework.yellow_taxi_trip_mat` AS
SELECT * FROM `bquery-275621.03_homework.yellow_taxi_trip_ext`;

--1
SELECT count(*) FROM `bquery-275621.03_homework.yellow_taxi_trip_ext`;

--2
SELECT count(distinct PULocationID) FROM `bquery-275621.03_homework.yellow_taxi_trip_ext`;

SELECT count(distinct PULocationID) FROM `bquery-275621.03_homework.yellow_taxi_trip_mat`;

--3

SELECT PULocationID FROM `bquery-275621.03_homework.yellow_taxi_trip_mat`;

SELECT PULocationID, DOLocationID FROM `bquery-275621.03_homework.yellow_taxi_trip_mat`;

--5
CREATE OR REPLACE TABLE `bquery-275621.03_homework.yellow_taxi_trip_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT * FROM `bquery-275621.03_homework.yellow_taxi_trip_ext`;


SELECT count(*) FROM `bquery-275621.03_homework.yellow_taxi_trip_mat`
WHERE fare_amount = 0;

--6

SELECT count(distinct VendorID) FROM `bquery-275621.03_homework.yellow_taxi_trip_mat`
WHERE tpep_dropoff_datetime >= '2024-03-01' and tpep_dropoff_datetime <= '2024-03-15';

SELECT count(distinct VendorID) FROM `bquery-275621.03_homework.yellow_taxi_trip_partitioned_clustered`
WHERE tpep_dropoff_datetime >= '2024-03-01' and tpep_dropoff_datetime <= '2024-03-15';

--9

SELECT count(*) FROM `bquery-275621.03_homework.yellow_taxi_trip_mat`;