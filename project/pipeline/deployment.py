"""Prefect deployment configuration.

Creates a deployment that runs on a Kubernetes work pool (EKS).
Schedule: daily at 4am UTC.

Usage:
    python -m pipeline.deployment     # Register deployment with Prefect Cloud
"""

from prefect import deploy
from prefect.runner.storage import DockerImage

from pipeline.flow import analytics_pipeline


def create_deployment():
    """Register the analytics pipeline deployment with Prefect Cloud."""

    deploy(
        analytics_pipeline.to_deployment(
            name="daily-analytics",
            cron="0 4 * * *",
            description="Daily PushMetrics platform analytics pipeline",
            tags=["analytics", "pushmetrics", "production"],
            parameters={},
        ),
        work_pool_name="eks-analytics",
        image=DockerImage(
            name="pushmetrics-analytics-pipeline",
            tag="latest",
            dockerfile="Dockerfile",
        ),
        push=False,  # CI/CD handles pushing to ECR
    )


if __name__ == "__main__":
    create_deployment()
