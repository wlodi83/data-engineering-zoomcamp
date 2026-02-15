3.
select count(*) from prod.fct_monthly_zone_revenue;

4.
select pickup_zone, sum(revenue_monthly_total_amount) as total_revenue
from prod.fct_monthly_zone_revenue
where revenue_month >= '2020-01-01' and revenue_month < '2021-01-01'
and service_type = 'Green'
group by 1
order by 2 desc
limit 5;

5.
select sum(total_monthly_trips) as total_monthly_trips
from prod.fct_monthly_zone_revenue
where revenue_month = '2019-10-01'
and service_type = 'Green';