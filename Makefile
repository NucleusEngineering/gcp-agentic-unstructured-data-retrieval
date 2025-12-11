# Include the .env file and export its variables so they are available to shell commands
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

TESTPATH := $(ROOT_DIR)/tests/

.PHONY: install
install: # Install virtual environment with poetry
	@echo "🚀 Installing dependencies using Poetry"
	@poetry install

.PHONY: check
check: # Check lock file consistency and run static code analysis
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@poetry check --lock
	@echo "🚀 Linting code: Running ruff"
	@poetry run ruff check --fix src/
	@echo "🚀 Static type checking: Running mypy"
	@poetry run mypy src/
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@poetry run deptry src/

.PHONY: generate-data
generate-data: # Generate synthetic PDF medical records for testing
	@echo "🚀 Generating synthetic data..."
	@poetry run python scripts/generate_data.py

.PHONY: enable-apis
enable-apis: # Enable required Google Cloud APIs
	@echo "🚀 Enabling Discovery Engine API..."
	@gcloud services enable discoveryengine.googleapis.com --project=$(PROJECT_ID)

.PHONY: create-datastore
create-datastore: enable-apis # Create the Vertex AI Search Data Store using the provided script
	@echo "🚀 Setting your active Google Cloud project. You may be prompted for authentication."
	@gcloud config set project $(PROJECT_ID)
	@echo "🚀 Creating Vertex AI Search Data Store..."
	@bash scripts/create_datastore.sh

.PHONY: create-engine
create-engine: # Create the Enterprise Search App (Engine) using the provided script
	@echo "🚀 Creating Enterprise Search App (Engine)..."
	@poetry run python scripts/create_enterprise_engine.py

.PHONY: create-gcs-bucket
create-gcs-bucket: # Create the GCS bucket for document ingestion
	@echo "🚀 Creating GCS Bucket..."
	@gsutil mb -p $(PROJECT_ID) -l $(LOCATION) gs://$(GCS_BUCKET_NAME) || true

.PHONY: infra
infra: # Run all infrastructure setup steps
	@make create-datastore && make create-engine && make create-gcs-bucket
	@echo "✅ All infrastructure created successfully!"