-- Daily workflow health metrics
-- Dashboard tile: Workflow success rate over time (temporal)

with daily_stats as (
    select
        execution_date,
        count(*) as total_executions,
        count(case when is_success = true then 1 end) as successful,
        count(case when is_success = false then 1 end) as failed,
        avg(duration_seconds) as avg_duration_seconds,
        approx_percentile(duration_seconds, 0.5) as p50_duration_seconds,
        approx_percentile(duration_seconds, 0.95) as p95_duration_seconds,
        max(duration_seconds) as max_duration_seconds
    from {{ ref('stg_workflow_logs') }}
    group by execution_date
)

select
    execution_date,
    total_executions,
    successful,
    failed,
    round(cast(successful as double) / nullif(total_executions, 0) * 100, 2) as success_rate_pct,
    round(avg_duration_seconds, 1) as avg_duration_seconds,
    round(p50_duration_seconds, 1) as p50_duration_seconds,
    round(p95_duration_seconds, 1) as p95_duration_seconds,
    max_duration_seconds
from daily_stats
order by execution_date
