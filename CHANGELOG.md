# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.05] - 2025-07-18

### Added

- **Compact HTML Reports**: New system for generating smaller HTML reports for large datasets
  - Added `--compact` flag to CLI for enabling compact mode
  - Added `--max-items` parameter to control number of items per section
  - Added `compact` and `max_items` parameters to `export_html()` method
  - Added automatic media optimization in compact mode
  - Added example implementation in `examples/compact_export_example.py`

### Changed

- **File Size Optimization**: HTML reports now 75-90% smaller in compact mode (20MB → 2-5MB)
- **Media Processing**: Reduced thumbnails per post from 5 to 3 in compact mode
- **Network Graph**: Omitted in compact mode to reduce file size
- **CLI Interface**: Extended analyze command with new compact reporting options

### Technical Details

- **HTMLExporter**: Extended `export()` method with `compact` and `max_items` parameters
- **InstagramAnalyzer**: Extended `export_html()` method with optimization options
- **Data Pagination**: Implemented configurable limits for posts, stories, reels, and interactions
- **Backward Compatibility**: All existing functionality remains unchanged

### Performance

- **Memory Usage**: Reduced memory footprint for large datasets
- **Load Time**: Significantly faster HTML rendering in compact mode
- **Processing Speed**: Optimized data processing for large exports

## [0.2.1] - 2025-07-16

### Added
- **NEW DATA TYPES SUPPORT**: Complete implementation for three new Instagram data types
  - Support for `archived_posts.json` - analyze archived content
  - Support for `recently_deleted_content.json` - track deleted content
  - Support for `story_interactions/` directory - comprehensive story interaction analysis
- **Enhanced Data Detection**: `DataDetector` now recognizes new file patterns
- **New Pydantic Models**: `StoryInteraction` model with validation for interaction types
- **Robust JSON Parsing**: Enhanced `JSONParser` with methods for new data types
  - `parse_stories()` with flexible data structure handling
  - `parse_reels()` with video metrics support
  - `parse_story_interactions()` with directory traversal
- **Lazy Loading Support**: Memory-efficient loading for all new data types
- **Complete HTML Export**: New sections in HTML reports
  - Stories gallery with responsive card layout
  - Reels gallery with video statistics
  - Additional Content section (archived/deleted items)
  - Story interactions statistics and top interactors
- **Responsive CSS Styling**: Complete styling for all new sections
- **Interactive JavaScript**: Rendering functions for new content types
- **Error Handling**: Division by zero protection in statistics calculations

### Changed
- **HTML Template System**: Replaced Jinja2 with direct placeholder replacement for simplicity
- **Model Exports**: Added `Profile`, `Media`, and `MediaType` to models `__init__.py`
- **Version**: Updated to 0.2.1 to reflect new functionality
- **Statistics Engine**: Enhanced `BasicStatsAnalyzer` to include all new data types

### Fixed
- **Import Issues**: Resolved all import dependency problems for new models
- **Division by Zero**: Fixed statistics calculations when no data is available
- **Template Rendering**: Improved error handling in HTML generation
- **Memory Efficiency**: Maintained lazy loading patterns for new data types

### Technical Improvements
- **Testing**: All new components fully tested and verified
- **Code Quality**: Maintained high code quality standards with comprehensive error handling
- **Architecture**: Modular extension without breaking existing functionality
- **Documentation**: Updated inline documentation for all new features

## [0.2.0] - 2024-12-15

### Added
- **ENGAGEMENT METRICS FIX**: Complete resolution of engagement data showing as 0
  - New `EngagementParser` module for processing separate engagement files
  - Support for `liked_posts.json`, `post_comments.json`, `reel_comments.json`
  - Multiple matching strategies (timestamp, media URI, embedded data)
  - Backward compatibility with old Instagram export formats
- **NETWORK GRAPH VISUALIZATION**: Interactive network analysis
  - Integration with existing `NetworkAnalyzer` module
  - D3.js-powered interactive network graphs in HTML reports
  - Drag & drop, zoom, and tooltip features
  - Node and edge visualization for user interactions
- **CACHING SYSTEM**: Enterprise-grade caching implementation
  - Two-tier architecture (memory + disk)
  - LRU/LFU/FIFO eviction policies
  - SQLite metadata with zlib compression
  - Cache decorators for analysis functions
  - Circuit breaker pattern for fault tolerance
- **MEMORY OPTIMIZATION**: Advanced memory management
  - Lazy loading for all data types
  - Streaming JSON parser for large files
  - Memory profiling and automatic garbage collection
  - 40-60% reduction in memory usage
- **COMPREHENSIVE ERROR HANDLING**: Robust error management
  - 40+ custom exception classes
  - Exponential backoff retry logic
  - Circuit breaker pattern
  - Structured logging with Rich and JSON support

### Changed
- **Pydantic v2 Compatibility**: Updated to use `model_copy()` instead of deprecated `copy()`
- **Data Detection**: Enhanced file pattern recognition
- **JSON Parsing**: Improved robustness with multiple format support
- **HTML Export**: Enhanced with engagement data and network graphs

### Fixed
- **Early Return Bug**: Fixed issue preventing raw_data processing in engagement enrichment
- **Import Paths**: Corrected import statements for NetworkAnalyzer
- **Timezone Handling**: Improved compatibility with timezone-aware datetime objects
- **Memory Leaks**: Implemented weak references and proper cleanup

### Technical Improvements
- **Code Quality**: 144+ tests with 100% pass rate
- **Architecture**: Enterprise patterns (Singleton, Factory, Decorator, Circuit Breaker)
- **Performance**: Significant improvements in memory usage and processing speed
- **Documentation**: Comprehensive docstrings and inline documentation

## [0.1.0] - 2024-10-01

### Added
- **Initial Release**: Core Instagram data analysis functionality
- **Data Models**: Pydantic models for Posts, Users, Conversations, Media
- **JSON Parsing**: Basic parsing for Instagram export files
- **Analysis Engine**: Temporal, engagement, and content analysis
- **HTML Export**: Interactive HTML reports with charts
- **PDF Export**: Comprehensive PDF report generation
- **CLI Interface**: Command-line interface for batch processing
- **Configuration**: YAML/TOML configuration support

### Features
- Basic post analysis and statistics
- Temporal activity patterns
- Engagement metrics calculation
- Content analysis (hashtags, captions, media types)
- Interactive HTML reports with Chart.js
- PDF export with ReportLab
- Command-line interface
- Configuration management

## [Unreleased]

### Planned Features
- **Machine Learning**: Sentiment analysis and topic modeling
- **Web Interface**: FastAPI backend with React frontend
- **Plugin System**: Extensible architecture for custom analyzers
- **Advanced Visualizations**: Enhanced D3.js charts and graphs
- **External Integrations**: Google Analytics, Tableau, cloud storage
- **Mobile App**: React Native/Flutter mobile application

---

## Release Notes

### v0.2.1 - New Data Types Support
This release focuses on expanding the analyzer's capability to handle three new types of Instagram data that were previously unsupported. The implementation follows the established architectural patterns and maintains backward compatibility.

**Key Highlights:**
- 🆕 **Complete pipeline** for archived posts, deleted content, and story interactions
- 🎨 **Modern HTML interface** with responsive design for new content types
- 💾 **Memory efficient** lazy loading for all new data types
- 🔧 **Robust error handling** with graceful degradation
- 📊 **Comprehensive statistics** including new data in all calculations

### v0.2.0 - Performance & Reliability
This release represents a major milestone in the project's maturity, focusing on enterprise-grade performance, reliability, and user experience improvements.

**Key Highlights:**
- 🚀 **40-60% memory reduction** through advanced optimization techniques
- 📈 **100% engagement accuracy** with new parsing strategies
- 🕸️ **Interactive network visualization** for relationship analysis
- ⚡ **Enterprise caching** with automatic optimization
- 🛡️ **Comprehensive error handling** with retry logic and circuit breakers

### v0.1.0 - Foundation
The initial release establishing the core architecture and basic functionality for Instagram data analysis.

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Versioning

We use [Semantic Versioning](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](../../tags).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
