# Instagram Analyzer

Advanced Instagram data analysis tool for processing exported data and generating comprehensive insights, statistics, and visualizations.

## Features

### 🔍 Core Analysis
- **Data Detection**: Automatically detects Instagram export structure and validates data integrity
- **Comprehensive Parsing**: Supports posts, stories, reels, profile data, and more
- **Privacy-First**: All processing happens locally - no data sent to external servers

### 📊 Analytics Capabilities
- **Basic Statistics**: Posts, stories, reels counts, engagement metrics
- **Temporal Analysis**: Activity patterns by hour, day, week, month
- **Content Analysis**: Media types, hashtag usage, caption analysis
- **Engagement Insights**: Likes, comments, interaction patterns

### 📈 Visualizations & Reports
- **HTML Reports**: Interactive dashboards with charts and graphs
- **PDF Export**: Professional reports for sharing
- **JSON Export**: Raw data for further analysis
- **Privacy Options**: Anonymization features for sensitive data

## Installation

### Prerequisites
- Python 3.9 or higher
- Poetry (recommended) or pip

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/instagram-analyzer.git
cd instagram-analyzer

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/your-username/instagram-analyzer.git
cd instagram-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -e .
```

## Quick Start

### 1. Download Your Instagram Data

1. Go to Instagram Settings → Privacy and Security → Data Download
2. Request your data in JSON format
3. Download and extract the ZIP file

### 2. Run Analysis

```bash
# Basic analysis
instagram-analyzer analyze /path/to/instagram/data

# With custom output directory
instagram-analyzer analyze /path/to/instagram/data --output ./my_analysis

# Generate PDF report with anonymized data
instagram-analyzer analyze /path/to/instagram/data --format pdf --anonymize

# Include media analysis (slower but more detailed)
instagram-analyzer analyze /path/to/instagram/data --include-media
```

### 3. View Results

The tool will generate a comprehensive report in your chosen format (HTML by default) with:
- Activity timeline and patterns
- Engagement statistics
- Content breakdown
- Privacy analysis
- Interactive visualizations

## Command Line Interface

### Main Commands

```bash
# Analyze Instagram data
instagram-analyzer analyze DATA_PATH [OPTIONS]

# Validate data structure
instagram-analyzer validate DATA_PATH

# Get basic information
instagram-analyzer info DATA_PATH

# Show help
instagram-analyzer --help
```

### Options

- `--output, -o`: Output directory for reports
- `--format, -f`: Output format (html, json, pdf)
- `--include-media`: Include media file analysis
- `--anonymize`: Anonymize sensitive data
- `--verbose, -v`: Enable verbose output

## Data Structure Support

The tool supports various Instagram export formats:

- **Full Export**: Complete data download with all categories
- **Content Export**: Posts, stories, and reels only
- **Partial Export**: Limited data sets

### Supported Data Types

- ✅ Posts (single and carousel)
- ✅ Stories (including highlights)
- ✅ Reels and IGTV
- ✅ Comments and likes
- ✅ Profile information
- ✅ Followers/following lists
- ⏳ Direct messages (coming soon)
- ⏳ Live videos (coming soon)

## Privacy & Security

### Local Processing
- All data processing happens on your local machine
- No data is sent to external servers
- No internet connection required for analysis

### Anonymization Options
- Remove or hash personal identifiers
- Strip metadata from reports
- Generate shareable reports without sensitive data

### Sensitive Data Detection
- Automatic detection of emails, phone numbers, URLs
- Privacy risk assessment
- Recommendations for data protection

## Example Analysis Output

### Basic Statistics
```
📊 Content Summary
- Total Posts: 245
- Total Stories: 1,890
- Total Reels: 67
- Date Range: Jan 2020 - Dec 2023

💝 Engagement Overview
- Average Likes per Post: 45.2
- Average Comments per Post: 8.7
- Most Liked Post: 234 likes
- Engagement Rate: 12.3%
```

### Temporal Patterns
```
⏰ Activity Patterns
- Most Active Hour: 7 PM (23 posts)
- Most Active Day: Sunday (67 posts)
- Peak Month: August 2023 (34 posts)
- Posting Consistency: 78% score
```

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=instagram_analyzer

# Run specific test file
poetry run pytest tests/unit/test_models.py
```

### Code Quality

```bash
# Format code
poetry run black .

# Sort imports
poetry run isort .

# Type checking
poetry run mypy instagram_analyzer

# Lint code
poetry run flake8
```

## API Usage

You can also use Instagram Analyzer as a Python library:

```python
from instagram_analyzer import InstagramAnalyzer

# Initialize analyzer
analyzer = InstagramAnalyzer("/path/to/instagram/data")

# Load data
analyzer.load_data()

# Run analysis
results = analyzer.analyze(include_media=True)

# Export results
analyzer.export_html("./output", anonymize=True)
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/instagram-analyzer.git
cd instagram-analyzer

# Install development dependencies
poetry install --with dev

# Install pre-commit hooks
pre-commit install
```

## Roadmap

### Phase 1 - Core Features ✅
- [x] Basic data parsing and validation
- [x] Core analysis modules
- [x] CLI interface
- [x] HTML/JSON export

### Phase 2 - Advanced Analysis 🚧
- [ ] Sentiment analysis for comments/captions
- [ ] Network analysis for connections
- [ ] Advanced visualizations
- [ ] PDF export with charts

### Phase 3 - Enhanced Features 📋
- [ ] Direct message analysis
- [ ] Geolocation analysis
- [ ] Machine learning insights
- [ ] Web dashboard interface

### Phase 4 - Integrations 💡
- [ ] Export to other platforms
- [ ] API for third-party tools
- [ ] Plugin system
- [ ] Cloud processing options

## FAQ

**Q: Is my data safe?**
A: Yes! All processing happens locally on your machine. No data is sent to external servers.

**Q: What Instagram export format is supported?**
A: The tool supports JSON format exports from Instagram's official data download feature.

**Q: Can I share the generated reports?**
A: Yes! Use the `--anonymize` flag to remove sensitive information before sharing.

**Q: How long does analysis take?**
A: Typically 1-5 minutes for standard exports. Larger datasets or media analysis may take longer.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ for the Instagram community
- Thanks to all contributors and beta testers
- Special thanks to the Python data science community

## Support

- 📧 Email: support@instagram-analyzer.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/instagram-analyzer/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/instagram-analyzer/discussions)
- 📖 Documentation: [Full Documentation](https://instagram-analyzer.readthedocs.io)

---

**Disclaimer**: This tool is not affiliated with Meta/Instagram. It's designed to help users analyze their own exported data for personal insights and privacy awareness.
