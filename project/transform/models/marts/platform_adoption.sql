-- Platform adoption metrics over time
-- Dashboard: report/block creation trends, workspace activity

with daily_reports as (
    select
        created_date,
        count(*) as new_reports,
        count(distinct workspace_id) as active_workspaces
    from {{ ref('stg_reports') }}
    group by created_date
),

daily_blocks as (
    select
        created_date,
        count(*) as new_blocks,
        block_type,
        count(distinct workspace_id) as workspaces_using_type
    from {{ ref('stg_blocks') }}
    group by created_date, block_type
),

block_type_summary as (
    select
        created_date,
        sum(new_blocks) as total_new_blocks
    from daily_blocks
    group by created_date
)

select
    coalesce(r.created_date, b.created_date) as date,
    coalesce(r.new_reports, 0) as new_reports,
    coalesce(r.active_workspaces, 0) as active_workspaces,
    coalesce(b.total_new_blocks, 0) as new_blocks
from daily_reports r
full outer join block_type_summary b on r.created_date = b.created_date
order by date
