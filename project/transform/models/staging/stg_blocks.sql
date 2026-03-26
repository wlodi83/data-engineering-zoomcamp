with source as (
    select * from {{ source('raw', 'block') }}
),

staged as (
    select
        id as block_id,
        type as block_type,
        workspace_id,
        created_on,
        changed_on,
        date(created_on) as created_date
    from source
)

select * from staged
