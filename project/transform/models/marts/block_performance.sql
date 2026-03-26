-- Block performance by type
-- Dashboard tile: Block type usage distribution (categorical)

with block_stats as (
    select
        block_type,
        execution_date,
        count(*) as executions,
        count(case when is_success = true then 1 end) as successful,
        count(case when is_success = false then 1 end) as failed,
        avg(duration_seconds) as avg_duration_seconds,
        approx_percentile(duration_seconds, 0.5) as p50_duration_seconds,
        approx_percentile(duration_seconds, 0.95) as p95_duration_seconds
    from {{ ref('stg_block_executions') }}
    group by block_type, execution_date
)

select
    block_type,
    execution_date,
    executions,
    successful,
    failed,
    round(cast(successful as double) / nullif(executions, 0) * 100, 2) as success_rate_pct,
    round(avg_duration_seconds, 1) as avg_duration_seconds,
    round(p50_duration_seconds, 1) as p50_duration_seconds,
    round(p95_duration_seconds, 1) as p95_duration_seconds
from block_stats
order by block_type, execution_date
