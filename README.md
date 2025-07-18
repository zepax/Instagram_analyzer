# Instagram Analyzer

[![Python Ve# Installation

### Prerequisites
- Python 3.9 or higher
- Poetry (recommended) or pip

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-username/instagram-data-mining.git
cd instagram-data-mining

# Install dependencies with Poetry (recommended)
poetry installimg.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency%20management-poetry-blue)](https://python-poetry.org/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-80%2B%25-brightgreen)](#testing)

A comprehensive analysis tool for Instagram data exports. Analyze your Instagram activity, generate insights, and create detailed reports about your social media usage patterns.

## ✨ Key Features

### 📊 Data Processing
- **Multi-Format Support**: Handles Instagram's JSON export format with automatic structure detection
- **Content Analysis**: Posts, stories, reels, comments, likes, and profile information
- **Data Validation**: Comprehensive validation and error reporting
- **Privacy Protection**: Local processing with anonymization options
- **Performance Optimized**: Lazy loading and caching for efficient memory usage

### 🔍 Analysis Capabilities
- **Basic Statistics**: Content counts, engagement metrics, and activity summaries
- **Temporal Analysis**: Activity patterns, posting schedules, and trend analysis
- **Engagement Analysis**: Like/comment ratios, interaction patterns, and performance metrics
- **Content Insights**: Hashtag analysis, media type distribution, and content patterns
- **Profile Analysis**: Account activity, follower interactions, and usage statistics

### 📈 Advanced Features
- **Machine Learning**: Sentiment analysis, engagement prediction, and content categorization
- **Caching System**: Three-tier caching (memory, disk, database) for improved performance
- **Export Options**: HTML reports, JSON data, and PDF summaries
- **CLI Interface**: Command-line tools for batch processing and automation
- **API Integration**: Programmatic access for custom analysis workflows

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- Poetry (recommended) or pip

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-username/instagram-analyzer.git
cd instagram-analyzer

# Install dependencies with Poetry (recommended)
poetry install

# Activate virtual environment
poetry shell
```

### Alternative Installation

```bash
# Install with pip
pip install -e .

# Or install specific dependency groups
poetry install --with dev,ml
```

## 🔧 Usage

### Command Line Interface

The main CLI tool is `instagram-miner` with the following commands:

#### 1. Validate Data Export

```bash
# Validate Instagram data export structure
instagram-miner validate /path/to/instagram/export

# With verbose output
instagram-miner validate /path/to/instagram/export -v
```

#### 2. Get Basic Information

```bash
# Display basic information about the data export
instagram-miner info /path/to/instagram/export
```

#### 3. Analyze Data

```bash
# Basic analysis with HTML report
instagram-miner analyze /path/to/instagram/export

# Specify output directory and format
instagram-miner analyze /path/to/instagram/export -o ./output -f html

# Include media analysis (slower but more comprehensive)
instagram-miner analyze /path/to/instagram/export --include-media

# Anonymize sensitive data in reports
instagram-miner analyze /path/to/instagram/export --anonymize

# Generate compact HTML report (smaller file size)
instagram-miner analyze /path/to/instagram/export --compact --max-items 50

# Generate PDF report
instagram-miner analyze /path/to/instagram/export -f pdf -o ./reports
```

#### Global Options

```bash
# Enable verbose logging
instagram-miner -v analyze /path/to/data

# Set specific log level
instagram-miner --log-level DEBUG analyze /path/to/data

# Enable file logging
instagram-miner --log-file ./logs analyze /path/to/data
```

### Programmatic API

#### Basic Usage

```python
from instagram_analyzer import InstagramAnalyzer

# Initialize analyzer
analyzer = InstagramAnalyzer("/path/to/instagram/export")

# Load data (optional - uses lazy loading by default)
analyzer.load_data()

# Validate data
validation = analyzer.validate_data()
print(f"Data loaded: {validation['data_loaded']['valid']}")

# Perform analysis
results = analyzer.analyze()

# Export results
analyzer.export_html("./output")
analyzer.export_json("./output/data.json")
```

#### Advanced Usage

```python
from instagram_analyzer import InstagramAnalyzer

# Initialize with custom options
analyzer = InstagramAnalyzer(
    data_path="/path/to/export",
    lazy_loading=True  # Enable lazy loading for large datasets
)

# Access specific data types
posts = analyzer.posts  # Returns lazy-loaded posts
stories = analyzer.stories  # Returns lazy-loaded stories
profile = analyzer.profile  # Returns profile information

# Generate specific analyses
stats = analyzer.basic_stats
temporal = analyzer.temporal_analysis
engagement = analyzer.engagement_analysis

# Export with options
analyzer.export_html("./output", anonymize=True)
analyzer.export_html("./output", compact=True, max_items=100)  # Compact reports
analyzer.export_json("./output/data.json", anonymize=True)
```

### Supported Data Types

The analyzer supports the following Instagram data types:

- ✅ **Posts**: Single and carousel posts with metadata
- ✅ **Stories**: Regular and archived stories
- ✅ **Reels**: Short-form video content
- ✅ **Comments**: Comments on posts and reels
- ✅ **Likes**: Liked posts and comments
- ✅ **Profile**: Account information and settings
- ✅ **Followers/Following**: Connection lists
- ✅ **Story Interactions**: Story views, polls, questions
- ✅ **Archived Content**: Previously archived posts
- ✅ **Recently Deleted**: Deleted content (if available)

## 📦 Compact Reports

For large Instagram datasets, the analyzer offers compact reporting to reduce file sizes:

### Size Optimization Features

- **Data Pagination**: Limits items per section (configurable with `--max-items`)
- **Media Optimization**: Reduces thumbnails and media processing
- **Network Graph Optimization**: Omits heavy network visualizations
- **Selective Content**: Shows only most recent/relevant content

### Usage Examples

```bash
# Generate compact report with top 50 items per section
instagram-miner analyze /path/to/data --compact --max-items 50

# Default compact mode (100 items per section)
instagram-miner analyze /path/to/data --compact
```

```python
# Programmatic usage
analyzer.export_html("./output", compact=True, max_items=50)
```

### Performance Benefits

- **File Size**: 75-90% reduction (20MB → 2-5MB)
- **Load Time**: Significantly faster HTML rendering
- **Memory Usage**: Reduced memory footprint
- **Compatibility**: Works with all existing features

## 📁 Data Structure

### Instagram Export Format

The tool expects Instagram data in the official JSON export format:

```
instagram-export/
├── your_instagram_activity/
│   ├── media/
│   │   ├── posts_1.json
│   │   ├── stories.json
│   │   └── archived_posts.json
│   ├── comments/
│   │   ├── post_comments_1.json
│   │   └── reels_comments.json
│   └── likes/
│       ├── liked_posts.json
│       └── liked_comments.json
├── media/
│   ├── posts/
│   │   └── YYYYMM/
│   │       └── *.jpg
│   └── stories/
│       └── YYYYMM/
│           └── *.jpg
└── personal_information/
    └── personal_information/
        └── personal_information.json
```

### Data Validation

The analyzer performs comprehensive validation:

```python
validation = analyzer.validate_data()

# Check validation results
if validation["data_loaded"]["valid"]:
    print(f"Loaded: {validation['data_loaded']['details']}")

if validation["profile_data"]["valid"]:
    print("Profile information found")

if validation["content_found"]["valid"]:
    print(f"Total content: {validation['content_found']['count']}")
```

## 🔒 Privacy & Security

### Local Processing
- **No External Connections**: All data processing happens locally
- **No Data Transmission**: Your data never leaves your machine
- **Offline Operation**: Works without internet connection

### Anonymization Features
- **Personal Data Removal**: Strips usernames, display names, and identifiers
- **Metadata Cleaning**: Removes location data and device information
- **Report Sanitization**: Generates shareable reports without sensitive data

### Data Security
- **Secure Processing**: Uses secure temporary files and memory handling
- **Cache Protection**: Encrypted caching for sensitive data
- **Audit Trail**: Comprehensive logging of all data processing activities

## 📊 Analysis Results

### Basic Statistics
```python
stats = analyzer.basic_stats
print(f"Posts: {stats.posts_count}")
print(f"Stories: {stats.stories_count}")
print(f"Engagement rate: {stats.engagement_rate:.2%}")
```

### Temporal Analysis
```python
temporal = analyzer.temporal_analysis
print(f"Most active hour: {temporal.peak_hour}")
print(f"Most active day: {temporal.peak_day}")
print(f"Activity consistency: {temporal.consistency_score:.2f}")
```

### Content Analysis
```python
content = analyzer.content_analysis
print(f"Top hashtags: {content.top_hashtags}")
print(f"Media types: {content.media_distribution}")
print(f"Average caption length: {content.avg_caption_length}")
```

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/instagram_analyzer
```

### Code Quality

```bash
# Format code
poetry run black src/instagram_analyzer/ tests/

# Sort imports
poetry run isort src/instagram_analyzer/ tests/

# Type checking
poetry run mypy src/instagram_analyzer/

# Lint code
poetry run flake8 src/instagram_analyzer/

# Run all quality checks
make quality
```

### Testing

```bash
# Run all tests
PYTHONPATH=src poetry run pytest

# Run specific test file
PYTHONPATH=src poetry run pytest tests/unit/test_models.py

# Run with coverage report
PYTHONPATH=src poetry run pytest --cov=src/instagram_analyzer --cov-report=html
```

## 🏗️ Architecture

### Core Components

- **`core/analyzer.py`**: Main `InstagramAnalyzer` class
- **`parsers/`**: Data parsing and validation modules
- **`models/`**: Pydantic data models for all Instagram content types
- **`analyzers/`**: Analysis modules for statistics and insights
- **`exporters/`**: Report generation (HTML, JSON, PDF)
- **`cache/`**: Three-tier caching system
- **`ml/`**: Machine learning models and features
- **`utils/`**: Utility functions and helpers

### Data Flow

1. **Data Detection**: Automatically detects Instagram export structure
2. **Validation**: Validates data integrity and format
3. **Parsing**: Converts JSON to typed Python objects
4. **Analysis**: Generates statistics and insights
5. **Export**: Creates reports in multiple formats

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for privacy-conscious Instagram users
- Thanks to all contributors and beta testers
- Special thanks to the Python data science community

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/instagram-analyzer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/instagram-analyzer/discussions)
- 📖 **Documentation**: [Full Documentation](docs/README.md)

---

**Disclaimer**: This tool is not affiliated with Meta/Instagram. It's designed to help users analyze their own exported data for personal insights and privacy awareness.
