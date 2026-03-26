# PushMetrics Platform Analytics Pipeline

End-to-end data engineering pipeline that extracts operational metrics from the PushMetrics Query.me platform, loads them into a columnar data lake on S3, and serves analytics via AWS Athena + dbt transformations.

## Problem Statement

PushMetrics Query.me is a collaborative SQL editor and reporting platform. As usage grows, we need visibility into:

- **Workflow reliability** — Which workflows fail most? What's the average execution time trend?
- **Block performance** — Which block types are slowest? Where are the bottlenecks?
- **Platform adoption** — How are reports, blocks, and workflows being used over time?

This pipeline answers these questions by building an automated, daily analytics pipeline from the production PostgreSQL database to an Athena-based warehouse with dbt-modeled marts and Tableau dashboards.

## Architecture

```
PostgreSQL (staging read replica)
    │
    ▼
[Extraction] ─── dlt (incremental, with PII anonymization)
    │
    ▼
[Data Lake] ──── S3 (Parquet, partitioned by date + workspace)
    │              + DuckDB for local ad-hoc exploration
    ▼
[Warehouse] ──── AWS Athena (serverless, columnar via Parquet)
    │              + AWS Glue Data Catalog
    │              Partitioned by execution_date
    │              Clustered via Parquet row groups by workspace_id
    ▼
[Transforms] ─── dbt (dbt-athena adapter)
    │              staging → intermediate → marts
    ▼
[Dashboard] ──── Tableau (JDBC → Athena)
    │
[Orchestration] ─ Prefect (flow on EKS via Kubernetes work pool)
                   Prefect Cloud for scheduling, monitoring, retries
```

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Extraction | [dlt](https://dlthub.com/) | Schema evolution, incremental loads, built-in Parquet + S3 destination |
| Data Lake | S3 + Parquet | Columnar, compressed, partitioned — native to AWS ecosystem |
| Warehouse | AWS Athena | Serverless, queries S3 Parquet directly, ~$0 at our data volume |
| Catalog | AWS Glue | Required by Athena, Terraform-managed |
| Transforms | dbt (dbt-athena) | Industry standard, version-controlled SQL transformations |
| Dashboard | Tableau | Existing team expertise, JDBC connector to Athena |
| Orchestration | Prefect + EKS | Flow-based orchestration with retries, scheduling, and monitoring via Prefect Cloud; worker runs on existing EKS cluster |
| IaC | Terraform | S3 bucket, Glue database, Athena workgroup, IAM roles |
| Exploration | DuckDB | Local Parquet analysis without Athena costs |

## Data Sources (PushMetrics PostgreSQL)

All data is anonymized at extraction time — user IDs are hashed, no PII is stored.

| Source Table | Extracted Fields | Purpose |
|---|---|---|
| `workflow` | id, workspace_id, cron_rule, is_active, created_on | Workflow configurations |
| `workflow_log` | id, workflow_id, status, start_time, end_time, progress | Execution history |
| `noteflow_run` | id, workspace_id, status, start_time, end_time | Run-level metrics |
| `noteflow_run_task` | id, run_id, status, start_time, end_time | Task-level metrics |
| `block_execution` | id, block_id, block_type, start_date, end_date, status | Block performance |
| `report` | id, workspace_id, created_on, changed_on | Report metadata |
| `report_block` | report_id, block_id, block_type | Report composition |
| `block` | id, type, workspace_id, created_on | Block inventory |
| `logs` | action, user_id (hashed), dttm | Platform action log |

## Project Structure

```
project/
├── README.md
├── Makefile                        # Common commands
├── Dockerfile                      # Pipeline container
├── docker-compose.yml              # Local dev (source Postgres)
├── .env.example                    # Required environment variables
├── terraform/
│   ├── main.tf                     # S3, Glue, Athena, IAM
│   ├── variables.tf
│   └── outputs.tf
├── pipeline/
│   ├── __init__.py
│   ├── flow.py                     # Prefect flow (extract → transform → test)
│   ├── deployment.py               # Prefect deployment config (K8s work pool)
│   ├── extract.py                  # dlt pipeline definition
│   ├── anonymize.py                # PII hashing utilities
│   ├── sources.py                  # dlt source/resource definitions
│   ├── config.toml                 # dlt configuration
│   ├── secrets.toml.example        # dlt secrets template
│   └── requirements.txt            # Python dependencies
├── transform/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/                # stg_workflow_logs, stg_block_executions, ...
│       ├── intermediate/           # Joined/enriched models
│       └── marts/                  # workflow_health, block_performance, platform_adoption
├── explore/
│   └── analysis.py                 # DuckDB exploration scripts
├── helm/
│   └── analytics-pipeline/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── worker.yaml         # Prefect worker Deployment (polls for flow runs)
│           └── configmap.yaml      # Pipeline configuration
└── .github/
    └── workflows/
        └── ci.yml                  # Lint, test, build + push Docker image
```

## Setup

### Prerequisites

- AWS account with permissions for S3, Glue, Athena, IAM
- Terraform >= 1.5
- Python 3.11+
- Docker
- kubectl + Helm (for EKS deployment)
- Prefect Cloud account (free tier)
- Access to PushMetrics staging database (read replica)

### 1. Infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars  # Set your AWS region, bucket name, etc.
terraform init
terraform plan
terraform apply
```

### 2. Prefect Cloud Setup

```bash
pip install prefect
prefect cloud login                           # Authenticate with Prefect Cloud

# Create the Kubernetes work pool
prefect work-pool create eks-analytics --type kubernetes
```

### 3. Local Development

```bash
cp .env.example .env                          # Fill in database credentials
pip install -r pipeline/requirements.txt

# Run the full flow locally
make flow

# Or run individual steps
make extract
make transform
```

### 4. Explore with DuckDB

```bash
python explore/analysis.py                    # Query Parquet files locally
```

### 5. Register Deployment

```bash
make register                                 # Register flow + schedule with Prefect Cloud
```

### 6. Deploy Worker to EKS

```bash
# Create Prefect API key secret
kubectl create namespace analytics
kubectl -n analytics create secret generic prefect-api-key \
  --from-literal=api-key=<your-prefect-api-key>

# Deploy the worker
make deploy
```

## Orchestration

The pipeline uses **Prefect** for orchestration:

- **Flow**: `pushmetrics-analytics` — 3 tasks (extract → transform → test)
- **Schedule**: Daily at 4:00 AM UTC via Prefect Cloud
- **Worker**: Runs as a Kubernetes Deployment on EKS, polls Prefect Cloud for scheduled runs
- **Execution**: Each flow run creates a K8s Job with the pipeline Docker image
- **Retries**: Extraction retries 2x (60s delay), transforms retry 1x (30s delay)
- **Monitoring**: Prefect Cloud UI shows run history, logs, task durations, failure alerts

```
Prefect Cloud (schedule + UI)
    │
    │  polls for scheduled runs
    ▼
Prefect Worker (K8s Deployment on EKS)
    │
    │  creates K8s Job for each flow run
    ▼
Pipeline Job (K8s Job)
    ├── Task 1: dlt extract (PG → S3 Parquet)
    ├── Task 2: dbt run (staging → marts on Athena)
    └── Task 3: dbt test (data quality validation)
```

## Dashboard

Tableau connects to Athena via JDBC. Two main views:

1. **Workflow Health** (temporal) — Daily success/failure rates, average execution duration trend, P95 latency
2. **Block Performance** (categorical) — Execution count and avg duration by block type, failure rate heatmap

## Reproducibility

```bash
# Full local run (requires Docker + AWS credentials)
make setup          # Terraform + install deps
make flow           # Run full Prefect flow locally
make explore        # Open DuckDB analysis

# Deploy to EKS
make register       # Register deployment with Prefect Cloud
make deploy         # Deploy Prefect worker to EKS
```

## Design Decisions

### Why Athena over Redshift?
At our data volume (~50K-100K rows/day), Redshift Serverless minimum costs exceed Athena's per-query pricing by 10-100x. Athena queries S3 Parquet directly — no server, no idle costs. We get columnar storage benefits (Parquet) and partitioning (Hive-style on S3) without warehouse management overhead.

### Why Prefect over Airflow?
We already use Prefect in the PushMetrics platform (Noteflow). A Prefect worker is a single K8s Deployment vs Airflow's 3+ components (scheduler, webserver, database). Prefect Cloud provides scheduling and monitoring UI for free, eliminating self-hosted infrastructure. The pipeline is 3 tasks — Airflow's DAG complexity is unnecessary here.

### Why dlt over custom scripts?
dlt handles schema evolution, incremental loading (merge/append strategies), and has native S3+Parquet destination support. Writing custom `psycopg2 → boto3 → parquet` code would require reimplementing all of this.

### Why hash user IDs instead of dropping them?
Hashed IDs preserve cardinality for user-level analytics (DAU, retention) without exposing PII. We can count unique users and track behavior patterns without knowing who they are.
