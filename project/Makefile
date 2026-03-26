.PHONY: setup extract transform explore deploy lint test clean flow register

# Load env vars
include .env
export

setup: ## Terraform + install Python deps
	cd terraform && terraform init && terraform apply -auto-approve
	pip install -r pipeline/requirements.txt
	cd transform && dbt deps

extract: ## Run dlt extraction only
	python -m pipeline.extract

transform: ## Run dbt transformations only
	cd transform && dbt run

test-dbt: ## Run dbt tests
	cd transform && dbt test

flow: ## Run full Prefect flow locally
	python -m pipeline.flow

register: ## Register Prefect deployment (schedule + work pool)
	python -m pipeline.deployment

explore: ## Launch DuckDB exploration
	python explore/analysis.py

lint: ## Lint Python code
	ruff check pipeline/ explore/
	cd transform && dbt compile

test: ## Run pipeline tests
	pytest pipeline/ -v

deploy: ## Deploy Prefect worker to EKS
	cd helm && helm upgrade --install analytics-pipeline ./analytics-pipeline \
		--namespace analytics \
		--create-namespace \
		--values analytics-pipeline/values.yaml

docker-build: ## Build pipeline Docker image
	docker build -t pushmetrics-analytics-pipeline .

docker-run: ## Run pipeline locally in Docker
	docker run --env-file .env pushmetrics-analytics-pipeline

clean: ## Remove local artifacts
	rm -rf explore/*.parquet transform/target/ transform/dbt_packages/

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
