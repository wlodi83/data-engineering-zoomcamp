with source as (
    select * from {{ source('raw', 'noteflow_run') }}
),

staged as (
    select
        id as run_id,
        workspace_id,
        status,
        start_time,
        end_time,
        created_on,
        date(start_time) as execution_date,
        case
            when end_time is not null and start_time is not null
            then date_diff('second', start_time, end_time)
        end as duration_seconds,
        case
            when status = 'completed' then true
            when status in ('failed', 'error') then false
            else null
        end as is_success
    from source
    where start_time is not null
)

select * from staged
