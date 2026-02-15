with taxi_zone_lookup as (
    select *
    from {{ ref('taxi_zone_lookup') }}
),

renamed as (
    select
        locationid as location_id,
        borough as borough,
        zone as zone,
        service_zone as service_zone
    from taxi_zone_lookup
)

select * from renamed