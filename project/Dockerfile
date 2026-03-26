FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY pipeline/requirements.txt pipeline/requirements.txt
RUN pip install --no-cache-dir -r pipeline/requirements.txt

# dbt deps
COPY transform/ transform/
RUN cd transform && dbt deps

# Pipeline code
COPY pipeline/ pipeline/

# Prefect flow as entrypoint
ENTRYPOINT ["python", "-m", "pipeline.flow"]
