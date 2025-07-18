# Instagram Analyzer - Development Makefile

.PHONY: help install install-dev test test-unit test-integration test-cov lint format type-check security clean build docs serve-docs pre-commit setup-dev

# Default target
help: ## Show this help message
	@echo "Instagram Analyzer - Development Commands"
	@echo "========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	poetry install --only=main

install-dev: ## Install all dependencies including dev tools
	poetry install
	poetry run pre-commit install

# Testing
test: ## Run all tests
	PYTHONPATH=src poetry run pytest

test-unit: ## Run only unit tests
	PYTHONPATH=src poetry run pytest -m unit

test-integration: ## Run only integration tests
	PYTHONPATH=src poetry run pytest -m integration

test-cov: ## Run tests with coverage report
	PYTHONPATH=src poetry run pytest --cov=src/instagram_analyzer --cov-report=html:output/coverage_html --cov-report=xml:output/coverage.xml --cov-report=term

test-watch: ## Run tests in watch mode
	PYTHONPATH=src poetry run ptw --runner "pytest --testmon"

# Code Quality
lint: ## Run linting checks
	poetry run flake8 src/instagram_analyzer/
	poetry run pydocstyle src/instagram_analyzer/

format: ## Format code with black and isort
	poetry run black src/instagram_analyzer/ tests/
	poetry run isort src/instagram_analyzer/ tests/

format-check: ## Check if code is properly formatted
	poetry run black --check src/instagram_analyzer/ tests/
	poetry run isort --check-only src/instagram_analyzer/ tests/

type-check: ## Run type checking with mypy
	poetry run mypy src/instagram_analyzer/

security: ## Run security checks
	poetry run bandit -r src/instagram_analyzer/
	poetry run safety check

pre-commit: ## Run all pre-commit hooks
	poetry run pre-commit run --all-files

# Quality All-in-One
quality: format lint type-check security test ## Run all quality checks

# Development
setup-dev: install-dev ## Setup development environment
	@echo "✅ Development environment setup complete!"
	@echo "📋 Next steps:"
	@echo "   1. Run 'make test' to verify installation"
	@echo "   2. Run 'make quality' before committing changes"
	@echo "   3. See 'make help' for available commands"

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

clean-all: clean ## Clean everything including virtual environment
	poetry env remove --all

# Building
build: clean ## Build the package
	poetry build

build-check: build ## Build and check the package
	poetry run twine check dist/*

# Documentation
docs: ## Generate documentation
	@echo "📚 Documentation generation not yet implemented"
	@echo "TODO: Add Sphinx documentation generation"

serve-docs: ## Serve documentation locally
	@echo "📚 Documentation serving not yet implemented"
	@echo "TODO: Add local documentation server"

# Analysis and Profiling
profile: ## Run performance profiling
	poetry run python -m cProfile -o profile.stats examples/profile_analysis.py
	poetry run python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

memory-profile: ## Run memory profiling
	poetry run mprof run examples/memory_analysis.py
	poetry run mprof plot

benchmark: ## Run performance benchmarks
	poetry run python examples/benchmark.py

# Database and Cache
clean-cache: ## Clean application cache
	rm -rf ~/.cache/instagram_analyzer/
	rm -rf .cache/

reset-db: ## Reset development database
	rm -rf *.db
	rm -rf data/*.db

# Example Commands
example-basic: ## Run basic analysis example
	poetry run python examples/basic_analysis.py

example-advanced: ## Run advanced analysis example
	poetry run python examples/advanced_analysis.py

example-export: ## Run export examples
	poetry run python examples/export_examples.py

# Release Management
version-patch: ## Bump patch version (x.y.Z)
	poetry version patch
	@echo "🔖 Version bumped to: $$(poetry version -s)"

version-minor: ## Bump minor version (x.Y.z)
	poetry version minor
	@echo "🔖 Version bumped to: $$(poetry version -s)"

version-major: ## Bump major version (X.y.z)
	poetry version major
	@echo "🔖 Version bumped to: $$(poetry version -s)"

tag-release: ## Create git tag for current version
	$(eval VERSION := $(shell poetry version -s))
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@echo "🏷️  Created tag: v$(VERSION)"

# CI/CD Simulation
ci-test: ## Simulate CI testing pipeline
	make format-check
	make lint
	make type-check
	make security
	make test-cov

ci-full: ## Simulate full CI/CD pipeline
	make clean
	make install-dev
	make ci-test
	make build-check

# Utility Commands
show-deps: ## Show dependency tree
	poetry show --tree

show-outdated: ## Show outdated dependencies
	poetry show --outdated

update-deps: ## Update dependencies
	poetry update

lock-deps: ## Update lock file only
	poetry lock --no-update

# Environment Info
info: ## Show environment information
	@echo "🐍 Python version: $$(python --version)"
	@echo "📦 Poetry version: $$(poetry --version)"
	@echo "📂 Project root: $$(pwd)"
	@echo "🔧 Virtual env: $$(poetry env info --path)"
	@echo "📋 Git branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repo')"

# Docker (if implemented)
docker-build: ## Build Docker image
	@echo "🐳 Docker support not yet implemented"
	@echo "TODO: Add Dockerfile and docker-compose.yml"

docker-run: ## Run in Docker container
	@echo "🐳 Docker support not yet implemented"

# Quick Commands for Daily Development
dev: setup-dev ## Alias for setup-dev

check: pre-commit ## Alias for pre-commit

fix: format ## Alias for format

# Testing shortcuts
t: test ## Short alias for test
tc: test-cov ## Short alias for test-cov
tu: test-unit ## Short alias for test-unit
ti: test-integration ## Short alias for test-integration
