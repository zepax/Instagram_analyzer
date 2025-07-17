# Contributing to Instagram Analyzer

Thank you for your interest in contributing to Instagram Analyzer! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** and clone your fork
2. **Install dependencies** using Poetry:
   ```bash
   poetry install
   ```
3. **Set up pre-commit hooks**:
   ```bash
   poetry run pre-commit install
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Requirements

- Python 3.9+
- Poetry for dependency management
- Git for version control

## 🏗️ Project Structure

```
instagram_analyzer/
├── instagram_analyzer/        # Main package
│   ├── core/                 # Core analysis logic
│   ├── parsers/              # Data parsing modules
│   ├── analyzers/            # Analysis modules
│   ├── exporters/            # Export functionality
│   ├── models/               # Pydantic data models
│   ├── cache/                # Caching system
│   ├── utils/                # Utility functions
│   └── templates/            # HTML templates
├── tests/                    # Test suite
├── docs/                     # Documentation
└── examples/                 # Example scripts
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=instagram_analyzer

# Run specific test categories
poetry run pytest -m unit
poetry run pytest -m integration
```

### Writing Tests

- Write tests for all new functionality
- Aim for >80% test coverage
- Use descriptive test names
- Group related tests in classes
- Use pytest fixtures for common setup

### Test Structure

```python
import pytest
from instagram_analyzer.models import Post

class TestPost:
    def test_post_creation_valid_data(self):
        """Test that Post can be created with valid data."""
        # Test implementation

    def test_post_creation_invalid_data(self):
        """Test that Post raises ValidationError with invalid data."""
        # Test implementation
```

## 🎨 Code Style

We use several tools to maintain code quality:

### Formatting
- **Black**: Code formatting
- **isort**: Import sorting

### Linting
- **flake8**: General linting
- **mypy**: Type checking
- **bandit**: Security analysis

### Running Code Quality Checks

```bash
# Run all pre-commit hooks
poetry run pre-commit run --all-files

# Run individual tools
poetry run black instagram_analyzer/
poetry run isort instagram_analyzer/
poetry run flake8 instagram_analyzer/
poetry run mypy instagram_analyzer/
poetry run bandit -r instagram_analyzer/
```

## 📝 Commit Messages

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples
```
feat(parser): add support for story interactions
fix(analyzer): handle division by zero in statistics
docs(readme): update installation instructions
test(models): add tests for StoryInteraction model
```

## 🏷️ Branching Strategy

- `main`: Stable, production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `release/*`: Release preparation branches
- `hotfix/*`: Critical bug fixes

## 📊 Pull Request Process

1. **Create a feature branch** from `develop`
2. **Make your changes** following code style guidelines
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run tests and quality checks**:
   ```bash
   poetry run pytest
   poetry run pre-commit run --all-files
   ```
6. **Submit a pull request** to `develop`

### PR Requirements

- [ ] All tests pass
- [ ] Code coverage is maintained (>80%)
- [ ] Pre-commit hooks pass
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (for significant changes)

## 📚 Documentation

### Docstring Style

Use Google-style docstrings:

```python
def analyze_posts(posts: List[Post], include_media: bool = True) -> Dict[str, Any]:
    """Analyze a collection of posts.

    Args:
        posts: List of Post objects to analyze.
        include_media: Whether to include media analysis.

    Returns:
        Dictionary containing analysis results with keys:
        - 'total_posts': Number of posts analyzed
        - 'media_types': Distribution of media types
        - 'engagement': Engagement statistics

    Raises:
        ValueError: If posts list is empty.
        AnalysisError: If analysis fails.

    Example:
        >>> posts = [Post(...), Post(...)]
        >>> results = analyze_posts(posts)
        >>> print(results['total_posts'])
        2
    """
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Dict, Optional, Union
from pathlib import Path

def parse_json_file(file_path: Path, encoding: str = 'utf-8') -> Optional[Dict[str, Any]]:
    """Parse a JSON file and return the data."""
```

## 🔧 Development Tips

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/instagram-analyzer.git
cd instagram-analyzer

# Install dependencies
poetry install

# Set up pre-commit hooks
poetry run pre-commit install

# Run tests to ensure everything works
poetry run pytest
```

### Using the Cache System

When developing new analyzers, consider using the caching system:

```python
from instagram_analyzer.cache import cached_analysis

class MyAnalyzer:
    @cached_analysis(ttl=3600)  # Cache for 1 hour
    def expensive_analysis(self, data: List[Post]) -> Dict[str, Any]:
        # Your expensive analysis here
        pass
```

### Memory Considerations

For large datasets, use lazy loading and streaming:

```python
@property
def large_dataset(self) -> List[SomeModel]:
    """Lazy load large dataset."""
    if self._large_dataset is None:
        self._large_dataset = self._load_large_dataset_lazy()
    return self._large_dataset
```

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Environment details** (Python version, OS, etc.)
2. **Steps to reproduce** the issue
3. **Expected behavior**
4. **Actual behavior**
5. **Error messages** (full traceback if applicable)
6. **Sample data** (if relevant and doesn't contain personal information)

### Issue Template

```markdown
## Bug Report

**Environment:**
- Python version: 3.11.0
- Instagram Analyzer version: 0.2.1
- OS: Ubuntu 22.04

**Steps to Reproduce:**
1. Load Instagram export data
2. Run analyzer.analyze()
3. Error occurs

**Expected Behavior:**
Analysis should complete successfully.

**Actual Behavior:**
KeyError: 'media' raised during analysis.

**Error Message:**
```
Traceback (most recent call last):
...
```

**Additional Context:**
- Data export from Instagram dated 2025-07-01
- ~1000 posts in dataset
```

## 📈 Performance Guidelines

- Use `@cached_analysis` for expensive computations
- Implement lazy loading for large datasets
- Use streaming parsers for files >50MB
- Profile memory usage for new features
- Consider batching for large operations

## 🔒 Security Guidelines

- Never commit sensitive data (API keys, personal information)
- Use `bandit` security checks
- Sanitize user inputs
- Follow principle of least privilege
- Implement proper error handling to avoid information leakage

## 📄 License

By contributing to Instagram Analyzer, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

If you have questions about contributing:

1. Check the [documentation](docs/)
2. Search [existing issues](../../issues)
3. Create a new issue with the "question" label
4. Reach out to the maintainers

Thank you for contributing to Instagram Analyzer! 🎉
