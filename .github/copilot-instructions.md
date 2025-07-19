

# 🤖 AI Coding Agent Instructions for Instagram Analyzer

## 🚦 COMPLIANCE & MANDATORY PROCESS FOR ALL AGENTS

**COMPLIANCE CONFIRMED: I will prioritize reuse over creation**

All AI agents (Claude, Copilot, ChatGPT, etc.) must follow the compliance process below. This repository is a code consolidation and reuse project. All suggestions, changes, and contributions must follow this sequential process and these rules:

### MANDATORY PROCESS
1. Start every proposal with: "COMPLIANCE CONFIRMED: I will prioritize reuse over creation"
2. Analyze the existing code BEFORE suggesting anything new
3. Reference specific files and paths from your analysis
4. Include validation checkpoints throughout your response
5. End with a compliance confirmation

### RULES (violating ANY invalidates your response):
- ❌ No new files without exhaustive reuse analysis
- ❌ No rewrites when refactoring is possible
- ❌ No generic advice: always provide specific implementations
- ❌ No ignoring the existing codebase architecture and structure
- ✅ Extend existing services and components
- ✅ Consolidate duplicate code
- ✅ Reference specific file paths
- ✅ Provide migration strategies if needed

**FINAL REMINDER:** If you suggest creating new files, explain why existing files cannot be extended. If you recommend rewrites, justify why refactoring is not sufficient.

### SEQUENTIAL STEPS (Mandatory)
1. 📋 STEP 1: READ REQUIREMENTS
   - Read these rules and confirm before proceeding.
2. 🔍 STEP 2: ANALYZE CURRENT SYSTEM
   - Analyze the existing codebase and identify relevant files for the requested feature.
3. 🎯 STEP 3: CREATE IMPLEMENTATION PLAN
   - Create a detailed implementation plan based on the previous analysis.
4. 🔧 STEP 4: PROVIDE TECHNICAL DETAILS
   - Specify code changes, API modifications, and integration points.
5. ✅ STEP 5: FINALIZE DELIVERABLES
   - Include testing strategies, deployment considerations, and final recommendations.

**This process is mandatory for all agents and developers.**

## Project Overview

Instagram Analyzer is a comprehensive data analysis tool for Instagram data exports. It's a privacy-first Python application that processes Instagram export data locally to generate insights, statistics, and visualizations. The project uses enterprise-grade patterns with modular architecture, multi-tier caching, and ML capabilities.

## Essential Commands

### Development Environment
```bash
# Setup development environment
make setup-dev
poetry install --with dev
poetry shell

# Run quality checks (mandatory before commits)
make quality  # Runs format, lint, type-check, security, test

# Individual quality checks
make format      # Black + isort
make lint        # flake8 + pydocstyle
make type-check  # mypy
make security    # bandit + safety
```

### Testing
```bash
# Run all tests (ALWAYS use PYTHONPATH=src or use poetry run)
PYTHONPATH=src poetry run pytest
poetry run pytest  # Preferred method

# Run tests with coverage
poetry run pytest --cov=src/instagram_analyzer --cov-report=html

# Run specific test types
poetry run pytest tests/unit/              # Unit tests
poetry run pytest tests/integration/       # Integration tests
poetry run pytest -m unit                  # Tests marked as unit
poetry run pytest -m integration           # Tests marked as integration

# Test specific components (v0.2.08+ improvements)
poetry run pytest tests/test_conversations_simple.py  # Improved conversation tests
poetry run pytest tests/unit/analyzers/               # Analyzer-specific tests
poetry run pytest tests/unit/exporters/               # Export-specific tests
```

### Application Usage
```bash
# CLI command is 'instagram-miner' (not 'instagram-analyzer')
instagram-miner analyze /path/to/instagram/export
instagram-miner analyze /path/to/data --format html --anonymize

# Web Dashboard (v0.2.08+) - FastAPI + MCP Integration
instagram-miner web --host 127.0.0.1 --port 8000  # Security: bind to localhost
instagram-miner web --config mcp_config.json      # Custom MCP server config

# MCP Integration Commands
# MCP servers provide distributed analysis, caching, and real-time capabilities
# Configuration in mcp_config.json for: filesystem, redis, AI, github, selenium
```

### Build and Release
```bash
# Build package
poetry build

# Simulate CI pipeline
make ci-full

# Version management
poetry version patch  # x.y.Z
poetry version minor  # x.Y.z
```

## Architecture Overview

### Core Data Flow
1. **Data Detection**: `parsers/data_detector.py` identifies Instagram export structure
2. **Parsing**: `parsers/json_parser.py` converts JSON to Pydantic models (`models/`)
3. **Analysis**: `core/analyzer.py` orchestrates analysis modules (`analyzers/`)
4. **Export**: `exporters/` generates HTML, PDF, or JSON reports
5. **Caching**: Two-tier caching system (`cache/`) for performance

### Key Components
- **`core/analyzer.py`**: Main `InstagramAnalyzer` class - entry point for all operations
- **`parsers/`**: Data parsing and validation (streaming with ijson for large files)
- **`models/`**: Pydantic v2 data models with strict typing
- **`analyzers/`**: Analysis modules (basic_stats, temporal_analysis, conversation_analyzer, network_analysis)
- **`exporters/`**: Report generation (HTML with Chart.js/D3.js, PDF with ReportLab)
- **`cache/`**: Memory + disk caching with intelligent fallback
- **`ml/`**: Machine learning pipeline for sentiment analysis and engagement prediction
- **`web/`**: FastAPI web dashboard with drag & drop upload, progress tracking
- **`mcp/`**: Model Context Protocol integration for distributed analysis and caching
- **`cli.py`**: Click-based CLI with Rich terminal output

### Important Patterns
- **Streaming Processing**: Uses `ijson` for large JSON files, memory profiling patterns
- **Cache-First**: Always check `CacheManager` before expensive operations
- **Lazy Loading**: Models use property-based loading for memory efficiency
- **Error Recovery**: Custom exception hierarchy with retry decorators
- **Privacy-First**: All processing is local-only, with anonymization utilities

## File Organization Rules

- **Source code**: ONLY in `src/instagram_analyzer/` (never at root)
- **Tests**: ONLY in `tests/unit/` or `tests/integration/`
- **Configuration**: Centralized in `config/` directory
- **Import pattern**: `from instagram_analyzer.module import Class`
- **PYTHONPATH**: Always set `PYTHONPATH=src` for commands

## Development Workflow

### Git Workflow
- **Always adapt to the latest active version branch.** The version branch (e.g., `v0.2.09`) will increment frequently as development progresses—always check which version is current before starting work.
- Never branch from `main`.
- For every new feature, improvement, or fix, create a dedicated branch named `feature/<short-description>`, `fix/<short-description>`, or `improvement/<short-description>` from the latest version branch.
- Frequently pull updates from the version branch to keep your feature branch up to date:
  ```bash
  # Replace v0.2.XX with the current version branch
  git checkout v0.2.XX
  git pull origin v0.2.XX
  git checkout -b feature/your-feature-name v0.2.XX
  # ...work on your feature...
  git pull origin v0.2.XX  # regularly update your branch
  ```
- Merge targets should always be the current version branch (e.g., `v0.2.09`).
- Run `make quality` (format, lint, type-check, security, test) before every commit and before opening a pull request.
- Use descriptive commit messages that reference the feature or fix.

### Code Conventions
- **Testing**: All new code requires tests (target >80% coverage)
- **Type checking**: Full mypy compliance required
- **Formatting**: Black + isort (configured in pyproject.toml)
- **Documentation**: Docstrings required for public APIs

### Common Development Tasks

#### Adding New Analysis Features
1. Create analyzer in `analyzers/` inheriting from base patterns
2. Register in `core/analyzer.py` analysis pipeline
3. Add tests in `tests/unit/analyzers/`
4. Update HTML template for visualization if needed

#### Adding Export Formats
1. Create exporter in `exporters/` with `export()` method
2. Register format in `cli.py`
3. Add templates in `templates/` if needed

#### Performance Optimization
- Profile with `utils/memory_profiler.py` patterns
- Use `cache_decorators.py` for expensive operations
- Implement streaming with `utils/streaming_parser.py`

#### Web Dashboard Development (v0.2.08+)
1. Create endpoints in `web/api/main.py` following FastAPI patterns
2. Use `mcp/redis_adapter.py` for session management and progress tracking
3. Configure MCP servers in `mcp_config.json` (filesystem, redis, AI, github, selenium)
4. Add templates in `web/templates/` with Bootstrap + Chart.js integration
5. Test with drag & drop file upload and real-time progress updates

#### MCP Integration Patterns
```python
# Use MCP Redis for distributed caching
from instagram_analyzer.mcp.redis_adapter import get_mcp_redis

async def cache_analysis_result(analysis_data: Dict[str, Any]) -> bool:
    redis = get_mcp_redis()
    cache_key = await redis.generate_cache_key(file_hash, "full_analysis")
    return await redis.cache_analysis(cache_key, analysis_data, ttl=3600)
```

## Testing Patterns

### Mock Data
```python
# Use existing patterns from tests/
@pytest.fixture
def sample_instagram_data():
    return create_mock_instagram_export(
        posts_count=10,
        conversations_count=5,
        include_media=True
    )
```

### Caching Tests
```python
@cache_result(cache_key_func=lambda self, data: f"test_{hash(str(data))}")
def expensive_operation(self, data: Path) -> Results:
    # Test caching integration
```

## Key Dependencies

- **CLI**: Click + Rich for beautiful terminal output
- **Data**: Pandas + NumPy for analysis, ijson for streaming
- **Validation**: Pydantic v2 with strict typing
- **Visualization**: Chart.js (web), D3.js (interactive), Matplotlib/Plotly (static)
- **Export**: Jinja2 templates, ReportLab for PDF
- **ML**: scikit-learn, NLTK, spaCy for text analysis
- **Web**: FastAPI + Uvicorn for dashboard (v0.2.08+)
- **MCP Integration**: Model Context Protocol for distributed analysis and caching

## Privacy and Security

- **Local Processing**: No external connections, offline-capable
- **Anonymization**: Built-in privacy utilities in `utils/privacy_utils.py`
- **Security**: Bandit scanning, secure file handling patterns
- **Data Protection**: Encrypted caching for sensitive data

## Current State

- **Version**: 0.2.08 (latest stable) / 0.2.09 (development branch)
- **Coverage**: Target >80% (currently improving)
- **Quality Gates**: Full CI/CD with pre-commit hooks
- **Architecture**: Enterprise-ready with ML + Web Dashboard + MCP integration
- **Documentation**: Comprehensive with examples


## 🎯 Git Workflow for Active Development

- **Always adapt to the latest active version branch.** The version branch (e.g., `v0.2.09`) will increment frequently as development progresses—always check which version is current before starting work.
- Never branch from `main`.
- For every new feature, improvement, or fix, create a dedicated branch named `feature/<short-description>`, `fix/<short-description>`, or `improvement/<short-description>` from the latest version branch.
- Frequently pull updates from the version branch to keep your feature branch up to date:
  ```bash
  # Replace v0.2.XX with the current version branch
  git checkout v0.2.XX
  git pull origin v0.2.XX
  git checkout -b feature/your-feature-name v0.2.XX
  # ...work on your feature...
  git pull origin v0.2.XX  # regularly update your branch
  ```
- Merge targets should always be the current version branch (e.g., `v0.2.09`).
- Run `make quality` (format, lint, type-check, security, test) before every commit and before opening a pull request.
- Use descriptive commit messages that reference the feature or fix.

## **🏗️ Project Architecture**

This is a **Python data analysis tool** that processes Instagram data exports using a **src-layout** structure with Poetry dependency management. The codebase follows enterprise patterns with two-tier caching, streaming parsers, and modular analyzers.

### **Core Components & Data Flow**

1. **Data Ingestion**: `parsers/data_detector.py` → `parsers/json_parser.py` → `models/` (Pydantic)
2. **Analysis Pipeline**: `core/analyzer.py` orchestrates `analyzers/` modules (basic stats, temporal, conversation)
3. **Export**: `exporters/html_exporter.py` (Chart.js + D3.js), `exporters/pdf_exporter.py` (ReportLab)
4. **Caching**: Two-tier system (`cache/memory_cache.py` + `cache/disk_cache.py`) with intelligent fallback

### **Key Architectural Patterns**

- **Streaming Processing**: Use `ijson` for large JSON files, implement `memory_profiler.py` patterns
- **Cache-First**: Always check `CacheManager` before expensive operations (parsing, analysis)
- **Lazy Loading**: Models use `__slots__` and property-based loading for memory efficiency
- **Error Recovery**: Custom exception hierarchy in `exceptions.py` with retry decorators

## **⚙️ Development Workflow Commands**

### **Essential Commands (MANDATORY)**

```bash
# Development setup
poetry install && poetry shell
PYTHONPATH=src poetry run pytest  # Always set PYTHONPATH=src

# Quality checks (pre-commit pipeline)
make quality  # Runs: format, lint, type-check, security, test
poetry run pre-commit run --all-files

# Testing patterns
poetry run pytest tests/unit/  # Fast unit tests
poetry run pytest -m integration  # Slow integration tests
poetry run pytest --cov=src/instagram_analyzer --cov-report=html

# CLI usage (Note: command is 'instagram-miner' not 'instagram-analyzer')
instagram-miner analyze /path/to/data --format html --anonymize
```

### File Organization Rules

- **ALL source code**: `src/instagram_analyzer/` (never at root)
- **ALL tests**: `tests/unit/` or `tests/integration/`
- **Configuration**: `config/` directory (centralized)
- **Import pattern**: `from instagram_analyzer.module import Class`

## Code Patterns & Conventions

### Data Models (Pydantic)
```python
# Always use this pattern for models
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ConversationMessage(BaseModel):
    content: str = Field(..., description="Message text")
    timestamp: datetime
    sender_name: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
```

### Caching Integration
```python
# Use cache decorators for expensive operations
from instagram_analyzer.cache import cache_result

@cache_result(cache_key_func=lambda self, data_path: f"parse_{hash(str(data_path))}")
def parse_instagram_data(self, data_path: Path) -> ParsedData:
    # Expensive parsing logic
```

### Error Handling
```python
# Use project's exception hierarchy
from instagram_analyzer.exceptions import (
    InstagramAnalyzerError, DataParsingError, InvalidDataFormatError
)

# Always use retry decorators for I/O
from instagram_analyzer.utils.retry_utils import with_retry

@with_retry(max_attempts=3, backoff_strategy="exponential")
def load_json_file(file_path: Path) -> Dict[str, Any]:
```

### HTML Template Integration
```python
# Templates use Chart.js + D3.js patterns
template_data = {
    'stats': analysis_results,
    'charts_data': json.dumps(chart_data),  # Always JSON-serialize for templates
    'network_data': json.dumps(network_graph),  # D3.js format
}
```

## Testing Patterns

### Mock Data Generation
```python
# Use existing test patterns from tests/conftest.py
@pytest.fixture
def sample_instagram_data():
    return create_mock_instagram_export(
        posts_count=10,
        conversations_count=5,
        include_media=True
    )
```

### Integration Test Structure
```python
# Follow tests/integration/ patterns
def test_full_analysis_pipeline(tmp_path, sample_data):
    analyzer = InstagramAnalyzer(sample_data)
    analyzer.load_data()
    results = analyzer.analyze()
    assert results['basic_stats']['total_posts'] > 0
```

## Common Development Tasks

### Adding New Analyzers
1. Create `analyzers/my_analyzer.py` inheriting from `base.py`
2. Register in `core/analyzer.py` analysis pipeline
3. Add corresponding tests in `tests/unit/analyzers/`
4. Update HTML template if visualization needed

### Adding Export Formats
1. Create `exporters/my_exporter.py` implementing `export()` method
2. Register format in CLI (`cli.py`)
3. Add templates in `templates/` if needed

### Performance Optimization
- Always profile with `utils/memory_profiler.py` patterns
- Use `cache_decorators.py` for expensive operations
- Implement streaming with `utils/streaming_parser.py` patterns

## Project-Specific Notes

- **Privacy-First**: All processing is local-only, use `privacy_utils.py` for anonymization
- **Bilingual Codebase**: Comments/docs can be Spanish or English, code in English
- **TODO-Driven**: Check `TODO.md` for current priorities (organized in development phases)
- **Dev Container Ready**: Use `.devcontainer/` for consistent environment

## Dependencies & Integration Points

- **CLI Framework**: Click + Rich for beautiful terminal output
- **Data Processing**: Pandas + NumPy for heavy analysis
- **Visualization**: Chart.js (web), Matplotlib/Plotly (static), D3.js (interactive)
- **PDF Generation**: ReportLab with custom templates
- **Validation**: Pydantic v2 with strict type checking
