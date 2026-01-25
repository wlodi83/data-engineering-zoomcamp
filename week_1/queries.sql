--Q3
select count(*) from public.yellow_taxi_data
where lpep_pickup_datetime >= '2025-11-01'
and lpep_pickup_datetime < '2025-12-01'
and trip_distance <= 1
limit 100;

--Q4
select lpep_pickup_datetime, max(trip_distance) from public.yellow_taxi_data
where lpep_pickup_datetime >= '2025-11-01'
and lpep_pickup_datetime < '2025-12-01'
and trip_distance <= 100
group by 1
order by 2 desc
limit 100;

--Q5
select z."Zone", sum(total_amount)
from public.yellow_taxi_data as d
inner join public.zones as z on z."LocationID" = d."PULocationID"
where lpep_pickup_datetime >= '2025-11-18'
and lpep_pickup_datetime < '2025-11-19'
group by 1
order by 2 desc
limit 100;

--Q6
select zd."Zone", max(tip_amount)
from public.yellow_taxi_data as d
inner join public.zones as z on z."LocationID" = d."PULocationID"
inner join public.zones as zd on zd."LocationID" = d."DOLocationID"
where lpep_pickup_datetime >= '2025-11-01'
and lpep_pickup_datetime < '2025-12-01'
and trip_distance <= 100
and z."Zone" = 'East Harlem North'
group by 1
order by 2 desc
limit 100;