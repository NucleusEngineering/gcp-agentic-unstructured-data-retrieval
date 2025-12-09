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

.PHONY: create-engine
create-engine: # Create the Enterprise Search Engine using the provided script
	@echo "🚀 Creating Enterprise Search Engine..."
	@poetry run python scripts/create_enterprise_engine.py