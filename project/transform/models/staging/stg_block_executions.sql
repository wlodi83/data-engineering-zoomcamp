with source as (
    select * from {{ source('raw', 'block_execution') }}
),

staged as (
    select
        id as block_execution_id,
        block_id,
        block_type,
        status,
        start_date as started_at,
        end_date as ended_at,
        created_on,
        -- Derived fields
        date(start_date) as execution_date,
        case
            when end_date is not null and start_date is not null
            then date_diff('second', start_date, end_date)
        end as duration_seconds,
        case
            when status = 'completed' then true
            when status in ('failed', 'error') then false
            else null
        end as is_success
    from source
    where start_date is not null
)

select * from staged
