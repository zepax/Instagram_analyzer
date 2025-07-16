# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Instagram Analyzer is a Python tool for analyzing Instagram data exports. It processes JSON files from Instagram's data download feature to generate comprehensive insights, statistics, and visualizations about user activity.

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies with Poetry (recommended)
poetry install

# Install development dependencies
poetry install --with dev

# Activate virtual environment
poetry shell
```

### Main Application Commands
```bash
# Run the CLI tool
instagram-analyzer analyze /path/to/instagram/data

# With options
instagram-analyzer analyze /path/to/data --output ./output --format html --anonymize

# Validate data structure
instagram-analyzer validate /path/to/data

# Get basic info
instagram-analyzer info /path/to/data
```

### Development and Testing
```bash
# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=instagram_analyzer

# Run specific test file
poetry run pytest tests/unit/test_models.py

# Code formatting
poetry run black .

# Import sorting
poetry run isort .

# Type checking
poetry run mypy instagram_analyzer

# Linting
poetry run flake8
```

## Architecture Overview

### Core Components

- **`core/analyzer.py`**: Main `InstagramAnalyzer` class that orchestrates data loading, analysis, and export
- **`parsers/`**: Data parsing modules that convert Instagram JSON exports into structured models
  - `data_detector.py`: Identifies Instagram export structure and validates data integrity
  - `json_parser.py`: Converts JSON files to typed Pydantic models
  - `conversation_parser.py`: Handles direct message conversation parsing
- **`models/`**: Pydantic data models for posts, stories, reels, profiles, users, and conversations
  - Comprehensive conversation models with message threading and analytics
  - Media models with support for various content types
  - User interaction models for likes, comments, reactions
- **`analyzers/`**: Analysis modules for basic statistics, temporal patterns, and engagement metrics
  - `basic_stats.py`: Content counts and engagement metrics
  - `temporal_analysis.py`: Activity patterns over time
  - `conversation_analyzer.py`: Direct message analysis and insights
- **`exporters/`**: Output generators for HTML, JSON, and PDF reports
  - `html_exporter.py`: Interactive HTML dashboards
  - `pdf_exporter.py`: Professional PDF reports with charts and tables
- **`utils/`**: Utility functions for date handling, file operations, privacy anonymization, text processing

### Data Flow

1. **Data Detection**: `parsers/data_detector.py` identifies Instagram export structure
2. **Parsing**: `parsers/json_parser.py` converts JSON files to typed models
3. **Analysis**: Various analyzers process the data to extract insights
4. **Export**: Results are formatted into HTML reports or other formats

### Key Classes

- `InstagramAnalyzer`: Main orchestrator class for the entire analysis pipeline (instagram_analyzer/core/analyzer.py:15)
- `JSONParser`: Handles parsing of Instagram JSON export files
- `BasicStatsAnalyzer`: Generates content counts, engagement metrics
- `TemporalAnalyzer`: Analyzes activity patterns over time
- `ConversationAnalyzer`: Processes direct message conversations with threading and metrics
- `HTMLExporter`: Creates interactive HTML dashboards
- `PDFExporter`: Generates professional PDF reports with ReportLab

### Configuration

- **Poetry**: Dependency management via `pyproject.toml`
- **Black**: Code formatting with 88 character line length
- **isort**: Import sorting with black profile
- **mypy**: Type checking enabled with strict settings
- **CLI**: Click-based interface with rich console output

## Entry Points

- **CLI**: `instagram_analyzer.cli:main` (configured in pyproject.toml)
- **API**: Import `InstagramAnalyzer` from `instagram_analyzer.core`

## Data Structure Support

The tool supports Instagram's official JSON export format and automatically detects various export types (full, content-only, partial). All processing happens locally with no external API calls.

### Supported Data Types

- ✅ Posts (single and carousel posts with media)
- ✅ Stories (including archived stories and highlights)
- ✅ Reels and IGTV content
- ✅ Comments and likes on posts/reels
- ✅ Profile information and metadata
- ✅ Direct message conversations with threading
- ✅ Story interactions (polls, questions, reactions)
- ✅ Followers/following lists and connections
- ✅ Media files (photos, videos, audio clips)

### Advanced Features

- **Conversation Analysis**: Message threading, response time analysis, emoji usage patterns
- **Privacy Protection**: Built-in anonymization tools for sensitive data
- **Temporal Analysis**: Activity patterns by hour, day, week, month with trend analysis
- **Rich Export Options**: Interactive HTML dashboards, professional PDF reports, JSON data exports
- **Media Type Detection**: Automatic classification of photos, videos, carousels, and stories

## Development Roadmap

The project has a comprehensive TODO list (`TODO.md`) organized in phases:

### Current Priority Areas
1. **Foundation & Quality** (Phase 1): Testing coverage >80%, error handling, documentation
2. **Performance & Scalability** (Phase 2): Caching, memory optimization, parallel processing
3. **Advanced Analytics** (Phase 3): Sentiment analysis, topic modeling, ML features
4. **User Experience** (Phase 4): Web dashboard, advanced visualizations
5. **Extensibility** (Phase 5): Plugin system, API development
6. **Security & Compliance** (Phase 6): Data encryption, GDPR compliance

### Available Tools & Libraries

The project is equipped with comprehensive tools for all development phases:

#### Core Development
- **Poetry**: Dependency management and virtual environments
- **Pydantic**: Data validation and serialization
- **Click + Rich**: CLI framework with beautiful console output
- **ReportLab**: Professional PDF generation
- **Pandas + NumPy**: Data analysis and manipulation

#### Visualization & Exports
- **Chart.js**: Interactive web charts
- **Matplotlib + Seaborn**: Statistical plotting
- **Plotly**: Advanced interactive visualizations
- **Pillow**: Image processing

#### Text & NLP Processing
- **TextBlob**: Sentiment analysis and basic NLP
- **WordCloud**: Text visualization
- **dateutil**: Advanced date parsing

#### Testing & Quality
- **pytest**: Testing framework with coverage support
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking
- **flake8**: Code linting

#### Future Integrations (Planned)
- **FastAPI**: Web API development
- **SQLite/PostgreSQL**: Data persistence
- **scikit-learn**: Machine learning capabilities
- **spaCy/NLTK**: Advanced NLP features
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline

### Development Workflow

1. **Choose a task** from `TODO.md` (start with Phase 1 for foundation)
2. **Create feature branch** following Git best practices
3. **Implement with tests** using existing patterns and tools
4. **Follow code standards** (black, isort, mypy, flake8)
5. **Update documentation** and CLAUDE.md if needed
6. **Submit PR** with comprehensive description

### AI-Assisted Development Notes

This project is fully equipped for AI-assisted development:
- **Comprehensive analysis** of all 28 core modules completed
- **Architecture patterns** well-documented for consistent development
- **TODO list** prioritized with clear implementation phases
- **Development tools** pre-configured and ready to use
- **Test infrastructure** in place for quality assurance
- **Documentation standards** established for maintainability

The codebase follows defensive security practices and is designed for local-only processing of user data exports.