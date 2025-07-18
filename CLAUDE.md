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
# IMPORTANT: Actual CLI command is 'instagram-miner' (not 'instagram-analyzer')
# Run the CLI tool
instagram-miner analyze /path/to/instagram/data

# With options
instagram-miner analyze /path/to/data --output ./output --format html --anonymize

# Validate data structure
instagram-miner validate /path/to/data

# Get basic info
instagram-miner info /path/to/data
```

### Development and Testing
```bash
# CRITICAL: Always set PYTHONPATH=src for all commands
# Run tests
PYTHONPATH=src poetry run pytest

# Run tests with coverage
PYTHONPATH=src poetry run pytest --cov=src/instagram_analyzer

# Run specific test file
PYTHONPATH=src poetry run pytest tests/unit/test_models.py

# Quality checks (recommended - runs all checks)
make quality  # Runs format, lint, type-check, security, test

# Individual quality commands
poetry run black src/instagram_analyzer/ tests/
poetry run isort src/instagram_analyzer/ tests/
poetry run mypy src/instagram_analyzer/
poetry run flake8 src/instagram_analyzer/
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

- **CLI**: `instagram-miner` → `instagram_analyzer.cli:main` (configured in pyproject.toml)
- **API**: `data-api` → `instagram_analyzer.api:start` (FastAPI server)
- **Programmatic**: Import `InstagramAnalyzer` from `instagram_analyzer.core`

## Critical Project Structure Notes

**IMPORTANT**: This project uses a **dual-directory structure**:

- **Primary Implementation**: `/src/instagram_analyzer/` (complete, use this)
  - Full feature set including ML, API, advanced caching
  - Modern src-layout packaging pattern
  - All imports: `from instagram_analyzer.module import Class`

- **Legacy/Simplified**: `/instagram_analyzer/` (basic version, avoid for new development)
  - Missing many modules (cache, ML, API, extractors)
  - Appears to be backup or distribution copy

**All development work should target `/src/instagram_analyzer/` and require `PYTHONPATH=src`**

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

# 🔧 **MANDATORY GIT WORKFLOW FOR ALL AI ASSISTANTS**

**CRITICAL**: All AI assistants MUST follow this exact workflow. No exceptions.

## **Branch Strategy (REQUIRED)**

### **Branch Types & Naming:**
- **`main`**: Production-ready code only
- **`v0.x.x`**: Version development branches (work here)
- **`feature/description`**: New features
- **`hotfix/description`**: Critical fixes
- **`bugfix/description`**: Bug fixes

### **Current Working Branch:**
- **Primary**: `v0.2.05` (current version branch)
- **Next**: `v0.2.06` (when 0.2.05 is complete)

## **MANDATORY WORKFLOW STEPS**

### **1. BEFORE Starting ANY Work:**
```bash
# Check current branch
git branch

# Switch to version branch (NOT main)
git checkout v0.2.05

# Always pull latest changes
git pull origin v0.2.05

# Verify clean state
git status
```

### **2. Create Feature Branch:**
```bash
# Use automation script (RECOMMENDED)
python scripts/git-automation.py --interactive

# Or manual creation
git checkout -b feature/your-feature-name v0.2.05
```

### **3. Development Cycle:**
```bash
# Make changes
# Run quality checks (MANDATORY before commit)
make quality

# Commit with proper format
git add .
git commit -m "feat: Add your feature description"

# Push regularly (backup)
git push -u origin feature/your-feature-name
```

### **4. Before Merge/PR:**
```bash
# Update base branch
git checkout v0.2.05
git pull origin v0.2.05

# Rebase feature branch
git checkout feature/your-feature-name
git rebase v0.2.05

# Final quality check
make quality
```

### **5. Merge Feature:**
```bash
# Switch to version branch
git checkout v0.2.05

# Merge with no-fast-forward
git merge --no-ff feature/your-feature-name

# Push version branch
git push origin v0.2.05

# Clean up feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

## **COMMIT STANDARDS (ENFORCED)**

### **Commit Message Format:**
```
<type>: <description>

<optional body>

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### **Commit Types:**
- **`feat`**: New feature
- **`fix`**: Bug fix
- **`docs`**: Documentation
- **`style`**: Code formatting
- **`refactor`**: Code refactoring
- **`test`**: Tests
- **`chore`**: Maintenance

## **QUALITY GATES (MANDATORY)**

### **Before Every Commit:**
```bash
# Run all quality checks
make quality

# Individual checks if needed
make format      # Black + isort
make lint        # Flake8 + pydocstyle
make type-check  # MyPy
make security    # Bandit + safety
make test        # All tests
```

### **Never Commit Without:**
- ✅ All tests passing
- ✅ No linting errors
- ✅ No type errors
- ✅ Security checks passed

## **MERGE STRATEGY (STRICT)**

### **Merge Frequency:**
- **Small features**: Same day
- **Medium features**: Within 3 days
- **Large features**: Break into smaller features

### **Merge Requirements:**
- Feature branch must be up-to-date with base
- All quality checks must pass
- No merge conflicts
- Use `--no-ff` for feature merges

## **VERSION MANAGEMENT**

### **Version Branches:**
- Work on `v0.2.05` until ready for release
- Create `v0.2.06` for next version
- Tag versions when complete: `git tag v0.2.05`

### **Version Increment Rules:**
- **PATCH** (0.2.05 → 0.2.06): Bug fixes, small features
- **MINOR** (0.2.x → 0.3.0): Significant features
- **MAJOR** (0.x.x → 1.0.0): Breaking changes

## **AUTOMATION TOOLS**

### **Git Automation Script:**
```bash
# Interactive branch creation
python scripts/git-automation.py --interactive

# View branch history
python scripts/git-automation.py --history

# Setup git hooks
bash scripts/setup-git-automation.sh
```

## **EMERGENCY PROCEDURES**

### **Fix Broken Commit:**
```bash
# Soft reset (keep changes)
git reset --soft HEAD~1

# Hard reset (discard changes)
git reset --hard HEAD~1
```

### **Resolve Merge Conflicts:**
```bash
# During merge/rebase
git status
# Edit conflicted files
git add resolved-file.py
git rebase --continue
```

## **FORBIDDEN ACTIONS**

### **NEVER DO:**
- ❌ Commit directly to `main`
- ❌ Force push to shared branches
- ❌ Merge without quality checks
- ❌ Skip tests or linting
- ❌ Create long-lived feature branches (>3 days)

### **ALWAYS DO:**
- ✅ Work on version branches (`v0.2.05`)
- ✅ Create feature branches for each task
- ✅ Run `make quality` before commits
- ✅ Use semantic commit messages
- ✅ Rebase before merge

## **Development Workflow with Makefile**

The project includes a comprehensive Makefile for streamlined development:

### **Essential Makefile Commands**
```bash
# Setup and installation
make setup-dev          # Complete dev environment setup
make install-dev        # Install with dev dependencies

# Quality and testing (most important)
make quality            # All-in-one: format, lint, type-check, security, test
make test              # Run all tests (sets PYTHONPATH=src automatically)
make test-cov          # Run tests with coverage report

# Individual checks
make format            # Format code (black + isort)
make lint              # Lint code (flake8 + pydocstyle)
make type-check        # Type checking (mypy)
make security          # Security checks (bandit + safety)

# CI simulation
make ci-full           # Simulate complete CI/CD pipeline
make pre-commit        # Run all pre-commit hooks

# Git workflow integration
make git-setup         # Setup git automation
make branch-new        # Create new feature branch
make quality-commit    # Quality check + commit

# Utilities
make clean             # Clean build artifacts and cache
make info              # Show environment information
make show-deps         # Show dependency tree
```

### Key Architectural Patterns

1. **Streaming/Memory-Efficient Processing**
   - Uses `ijson` for large JSON files to avoid memory issues
   - `memory_profiler.py` patterns for resource monitoring
   - Lazy loading with `__slots__` in models

2. **Two-Tier Caching System**
   ```python
   @cache_result(cache_key_func=lambda self, data_path: f"parse_{hash(str(data_path))}")
   def expensive_operation(self, data_path: Path) -> Result:
   ```

3. **Pydantic v2 Models with Strict Typing**
   - All data models use Pydantic v2 with strict configuration
   - Custom base models with JSON encoders
   - Type-safe throughout the entire pipeline

4. **Rich Exception Hierarchy**
   - Custom exceptions in `src/instagram_analyzer/exceptions.py`
   - Retry decorators in `utils/retry_utils.py`
   - Structured error context and recovery

## Important Configuration Files

- **GitHub Copilot Instructions**: `.github/copilot-instructions.md` contains detailed architecture patterns
- **Makefile**: 200+ lines of development workflow automation
- **pyproject.toml**: Comprehensive Poetry configuration with all dependencies organized by groups
