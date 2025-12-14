# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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


.PHONY: grant-permissions
grant-permissions: # Grant necessary IAM roles for the project
	@echo "🚀 Granting required IAM roles to the current user..."
	@gcloud projects add-iam-policy-binding $(PROJECT_ID) --member="user:$$(gcloud config get-value account)" --role="roles/aiplatform.user"
	@gcloud projects add-iam-policy-binding $(PROJECT_ID) --member="user:$$(gcloud config get-value account)" --role="roles/serviceusage.serviceUsageConsumer"
	@echo "🚀 Setting the quota project for Application Default Credentials..."
	@gcloud auth application-default set-quota-project $(PROJECT_ID)

.PHONY: infra
infra: # Run all infrastructure setup steps
	@make grant-permissions && make create-datastore && make create-engine && make create-gcs-bucket
	@echo "✅ All infrastructure created successfully!"