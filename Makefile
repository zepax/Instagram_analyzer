# Instagram Analyzer - Comprehensive Development Makefile
# This Makefile provides all essential development workflow commands

# Variables
PYTHON = python3
POETRY = poetry
PROJECT_NAME = instagram-analyzer
SRC_DIR = src/instagram_analyzer
TESTS_DIR = tests
DOCS_DIR = docs

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
MAGENTA = \033[0;35m
CYAN = \033[0;36m
WHITE = \033[0;37m
RESET = \033[0m

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)Instagram Analyzer Development Makefile$(RESET)"
	@echo "$(YELLOW)Usage: make [target]$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Git Automation Targets
.PHONY: git-setup
git-setup: ## Setup git automation and hooks
	@echo "$(BLUE)Setting up git automation...$(RESET)"
	@bash scripts/setup-git-automation.sh

.PHONY: branch-new
branch-new: ## Create new feature branch interactively
	@echo "$(BLUE)Creating new feature branch...$(RESET)"
	@python scripts/git-automation.py --interactive

.PHONY: branch-history
branch-history: ## Show branch creation history
	@echo "$(BLUE)Branch History:$(RESET)"
	@python scripts/git-automation.py --history

.PHONY: git-config
git-config: ## Show git automation configuration
	@echo "$(BLUE)Git Automation Configuration:$(RESET)"
	@python scripts/git-automation.py --config

# Quick branch creation targets
.PHONY: feat
feat: ## Create feature branch (usage: make feat DESC="description")
	@python scripts/git-automation.py --type feature --description "$(DESC)"

.PHONY: fix
fix: ## Create bugfix branch (usage: make fix DESC="description")
	@python scripts/git-automation.py --type bugfix --description "$(DESC)"

.PHONY: perf
perf: ## Create optimization branch (usage: make perf DESC="description")
	@python scripts/git-automation.py --type optimization --description "$(DESC)"

.PHONY: docs
docs: ## Create documentation branch (usage: make docs DESC="description")
	@python scripts/git-automation.py --type documentation --description "$(DESC)"

# Setup and Installation
.PHONY: setup-dev
setup-dev: ## Complete development environment setup
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	@$(POETRY) install --with dev
	@$(POETRY) run pre-commit install
	@make git-setup
	@echo "$(GREEN)✅ Development environment ready!$(RESET)"

.PHONY: install-dev
install-dev: ## Install with development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	@$(POETRY) install --with dev

.PHONY: install
install: ## Install production dependencies only
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	@$(POETRY) install --only main

# Quality and Testing
.PHONY: quality
quality: format lint type-check security test ## Run all quality checks (recommended)
	@echo "$(GREEN)✅ All quality checks passed!$(RESET)"

.PHONY: test
test: ## Run all tests (automatically sets PYTHONPATH=src)
	@echo "$(BLUE)Running tests...$(RESET)"
	@PYTHONPATH=src $(POETRY) run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	@PYTHONPATH=src $(POETRY) run pytest --cov=$(SRC_DIR) --cov-report=html --cov-report=term

.PHONY: test-fast
test-fast: ## Run tests with minimal output
	@echo "$(BLUE)Running fast tests...$(RESET)"
	@PYTHONPATH=src $(POETRY) run pytest -x -q

.PHONY: format
format: ## Format code (black + isort)
	@echo "$(BLUE)Formatting code...$(RESET)"
	@$(POETRY) run black $(SRC_DIR)/ $(TESTS_DIR)/
	@$(POETRY) run isort $(SRC_DIR)/ $(TESTS_DIR)/
	@echo "$(GREEN)✅ Code formatted$(RESET)"

.PHONY: lint
lint: ## Lint code (flake8 + pydocstyle)
	@echo "$(BLUE)Linting code...$(RESET)"
	@$(POETRY) run flake8 $(SRC_DIR)/ $(TESTS_DIR)/
	@$(POETRY) run pydocstyle $(SRC_DIR)/
	@echo "$(GREEN)✅ Linting passed$(RESET)"

.PHONY: type-check
type-check: ## Type checking (mypy)
	@echo "$(BLUE)Running type checks...$(RESET)"
	@$(POETRY) run mypy $(SRC_DIR)/
	@echo "$(GREEN)✅ Type checking passed$(RESET)"

.PHONY: security
security: ## Security checks (bandit + safety)
	@echo "$(BLUE)Running security checks...$(RESET)"
	@$(POETRY) run bandit -r $(SRC_DIR)/
	@$(POETRY) run safety check
	@echo "$(GREEN)✅ Security checks passed$(RESET)"

# CI/CD Simulation
.PHONY: ci-full
ci-full: ## Simulate complete CI/CD pipeline
	@echo "$(MAGENTA)🚀 Running complete CI/CD simulation...$(RESET)"
	@make quality
	@make test-cov
	@echo "$(GREEN)✅ CI/CD simulation completed successfully!$(RESET)"

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	@$(POETRY) run pre-commit run --all-files

# Development Utilities
.PHONY: clean
clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete
	@echo "$(GREEN)✅ Cleaned build artifacts$(RESET)"

.PHONY: info
info: ## Show environment information
	@echo "$(CYAN)Development Environment Information:$(RESET)"
	@echo "Python version: $(shell python --version)"
	@echo "Poetry version: $(shell poetry --version)"
	@echo "Project root: $(shell pwd)"
	@echo "Virtual env: $(shell poetry env info --path)"
	@echo "Dependencies: $(shell poetry show --tree --only main | wc -l) main, $(shell poetry show --tree --with dev | wc -l) total"

.PHONY: show-deps
show-deps: ## Show dependency tree
	@echo "$(BLUE)Dependency tree:$(RESET)"
	@$(POETRY) show --tree

# Application Testing
.PHONY: test-cli
test-cli: ## Test CLI functionality
	@echo "$(BLUE)Testing CLI functionality...$(RESET)"
	@$(POETRY) run instagram-miner --help
	@echo "$(GREEN)✅ CLI test passed$(RESET)"

.PHONY: test-import
test-import: ## Test package import
	@echo "$(BLUE)Testing package import...$(RESET)"
	@$(POETRY) run python -c "from instagram_analyzer import InstagramAnalyzer; print('✅ Import successful')"

# Special targets for common workflows
.PHONY: quick-check
quick-check: test-fast lint ## Quick development check
	@echo "$(GREEN)✅ Quick check passed$(RESET)"

.PHONY: commit-ready
commit-ready: format lint type-check test ## Prepare for commit
	@echo "$(GREEN)✅ Ready to commit!$(RESET)"

# Git workflow integration
.PHONY: git-setup
git-setup: ## Setup Git automation tools
	@echo "$(BLUE)Setting up Git automation...$(RESET)"
	@bash scripts/setup-git-automation.sh
	@echo "$(GREEN)✅ Git automation setup complete$(RESET)"

.PHONY: branch-new
branch-new: ## Create new feature branch interactively
	@echo "$(BLUE)Creating new feature branch...$(RESET)"
	@python scripts/git-automation.py --interactive

.PHONY: branch-history
branch-history: ## Show branch history
	@echo "$(BLUE)Branch history:$(RESET)"
	@python scripts/git-automation.py --history

.PHONY: quality-commit
quality-commit: quality ## Run quality checks and prepare for commit
	@echo "$(GREEN)✅ Quality checks passed - ready to commit!$(RESET)"
	@echo "$(YELLOW)Use: git add . && git commit -m 'feat: Your feature description'$(RESET)"

.PHONY: workflow-status
workflow-status: ## Show current workflow status
	@echo "$(BLUE)Current Git Status:$(RESET)"
	@git branch --show-current
	@git status --porcelain
	@echo "$(BLUE)Quality Status:$(RESET)"
	@$(MAKE) quick-check

.PHONY: workflow-validate
workflow-validate: ## Validate workflow compliance
	@echo "$(BLUE)Validating workflow compliance...$(RESET)"
	@python scripts/validate-workflow.py

.PHONY: workflow-help
workflow-help: ## Show workflow help
	@echo "$(BLUE)Instagram Analyzer - Git Workflow Commands:$(RESET)"
	@echo ""
	@echo "$(YELLOW)Setup:$(RESET)"
	@echo "  make git-setup      - Setup Git automation tools"
	@echo "  make workflow-validate - Validate workflow compliance"
	@echo ""
	@echo "$(YELLOW)Daily Development:$(RESET)"
	@echo "  make branch-new     - Create new feature branch"
	@echo "  make quality-commit - Quality check before commit"
	@echo "  make workflow-status - Show current status"
	@echo ""
	@echo "$(YELLOW)Quality Gates:$(RESET)"
	@echo "  make quality        - Full quality pipeline"
	@echo "  make quick-check    - Fast development check"
	@echo "  make commit-ready   - Prepare for commit"
	@echo ""
	@echo "$(YELLOW)Information:$(RESET)"
	@echo "  make branch-history - Show branch history"
	@echo "  make info          - Project information"

.PHONY: pr-ready
pr-ready: ci-full ## Prepare for pull request
	@echo "$(GREEN)✅ Ready for pull request!$(RESET)"

# Git status helpers
.PHONY: status
status: ## Show git and development status
	@echo "$(CYAN)Git Status:$(RESET)"
	@git status --short
	@echo ""
	@echo "$(CYAN)Current Branch:$(RESET)"
	@git branch --show-current
	@echo ""
	@echo "$(CYAN)Recent Commits:$(RESET)"
	@git log --oneline -5

# Development Workflow Examples
.PHONY: workflow-example
workflow-example: ## Show example development workflow
	@echo "$(CYAN)Example Development Workflow:$(RESET)"
	@echo "1. $(GREEN)make setup-dev$(RESET)              # Setup development environment"
	@echo "2. $(GREEN)make branch-new$(RESET)              # Create feature branch interactively"
	@echo "3. $(GREEN)make test$(RESET)                    # Run tests while developing"
	@echo "4. $(GREEN)make quality$(RESET)                # Run all quality checks"
	@echo "5. $(GREEN)git commit -m 'feat: ...'$(RESET)    # Commit changes (auto-formatted)"
	@echo "6. $(GREEN)git push$(RESET)                     # Push branch"
	@echo "7. Create PR on GitHub"
	@echo ""
	@echo "$(YELLOW)Quick Commands:$(RESET)"
	@echo "$(GREEN)make feat DESC='new feature'$(RESET)    # Quick feature branch"
	@echo "$(GREEN)make fix DESC='bug fix'$(RESET)         # Quick bugfix branch"
	@echo "$(GREEN)make ci-full$(RESET)                   # Complete CI simulation"

# Phony targets
.PHONY: all
all: setup-dev quality test-cov ## Complete setup and validation

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
