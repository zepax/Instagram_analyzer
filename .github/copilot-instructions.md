# GitHub Copilot Instructions for Instagram Analyzer

## Project Architecture

This is a **Python data analysis tool** that processes Instagram data exports using a **src-layout** structure with Poetry dependency management. The codebase follows enterprise patterns with two-tier caching, streaming parsers, and modular analyzers.

### Core Components & Data Flow

1. **Data Ingestion**: `parsers/data_detector.py` → `parsers/json_parser.py` → `models/` (Pydantic)
2. **Analysis Pipeline**: `core/analyzer.py` orchestrates `analyzers/` modules (basic stats, temporal, conversation)
3. **Export**: `exporters/html_exporter.py` (Chart.js + D3.js), `exporters/pdf_exporter.py` (ReportLab)
4. **Caching**: Two-tier system (`cache/memory_cache.py` + `cache/disk_cache.py`) with intelligent fallback

### Key Architectural Patterns

- **Streaming Processing**: Use `ijson` for large JSON files, implement `memory_profiler.py` patterns
- **Cache-First**: Always check `CacheManager` before expensive operations (parsing, analysis)
- **Lazy Loading**: Models use `__slots__` and property-based loading for memory efficiency
- **Error Recovery**: Custom exception hierarchy in `exceptions.py` with retry decorators

## Development Workflow

### Essential Commands (use these patterns)

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

# CLI usage
poetry run instagram-analyzer analyze /path/to/data --format html --anonymize
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
