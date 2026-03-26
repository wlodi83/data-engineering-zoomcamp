with source as (
    select * from {{ source('raw', 'report') }}
),

staged as (
    select
        id as report_id,
        workspace_id,
        created_on,
        changed_on,
        date(created_on) as created_date
    from source
)

select * from staged
