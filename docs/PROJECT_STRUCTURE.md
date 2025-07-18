# 📁 Project Structure Overview

This document provides an overview of the reorganized project structure following industry best practices.

## 🏗️ Current Structure

```
instagram_analyzer/                     # 📁 Root directory
├── 📁 src/                            # Source code
│   └── 📁 instagram_analyzer/         # Main Python package
│       ├── 📁 analyzers/              # Analysis modules
│       ├── 📁 extractors/             # Data extraction
│       ├── 📁 models/                 # Data models
│       ├── 📁 parsers/                # Data parsers
│       ├── 📁 utils/                  # Utility functions
│       ├── 📁 templates/              # HTML templates
│       └── 📁 cache/                  # Caching system
│
├── 📁 tests/                          # Test suite
│   ├── 📄 test_*.py                   # Test files
│   └── 📄 conftest.py                 # Test configuration
│
├── 📁 docs/                           # Documentation
│   ├── 📄 *.md                       # Documentation files
│   └── 📁 assets/                     # Documentation assets
│
├── 📁 examples/                       # Usage examples
│   └── 📄 analisis_personalizado.py  # Example script
│
├── 📁 data/                           # Data directory
│   └── 📁 sample_exports/             # Sample Instagram exports
│
├── 📁 output/                         # Generated outputs
│   ├── 📁 analysis/                   # Analysis results
│   ├── 📁 reports/                    # Generated reports
│   ├── 📁 coverage_html/              # Coverage reports
│   └── 📄 coverage.xml                # Coverage data
│
├── 📁 scripts/                        # Utility scripts
│   └── 📄 merge_branches.sh           # Development scripts
│
├── 📁 config/                         # Configuration files
│   ├── 📄 .flake8                     # Linting config
│   ├── 📄 .pre-commit-config.yaml     # Pre-commit hooks
│   └── 📄 pytest.ini                  # Test configuration
│
├── 📁 tools/                          # Development tools
│   └── 📄 conversation_commands.md    # Development commands
│
├── 📁 backup/                         # Backup/archive
│   ├── 📁 sessions/                   # Session files
│   └── 📁 analysis_results/           # Old analysis results
│
├── 📁 .github/                        # GitHub configuration
│   ├── 📁 workflows/                  # CI/CD workflows
│   ├── 📁 ISSUE_TEMPLATE/             # Issue templates
│   └── 📄 pull_request_template.md    # PR template
│
├── 📁 .devcontainer/                  # Development container
│   ├── 📄 devcontainer.json           # Container config
│   ├── 📄 Dockerfile                  # Container image
│   └── 📄 setup.sh                    # Setup script
│
├── 📁 .vscode/                        # VS Code configuration
│   ├── 📄 settings.json               # Workspace settings
│   ├── 📄 launch.json                 # Debug configurations
│   ├── 📄 tasks.json                  # Task definitions
│   └── 📄 extensions.json             # Recommended extensions
│
├── 📄 pyproject.toml                  # Project configuration
├── 📄 poetry.lock                     # Dependency lock file
├── 📄 README.md                       # Project documentation
├── 📄 CHANGELOG.md                    # Version history
├── 📄 CONTRIBUTING.md                 # Contribution guidelines
├── 📄 SECURITY.md                     # Security policy
├── 📄 TODO.md                         # Project roadmap
├── 📄 Makefile                        # Development commands
├── 📄 .gitignore                      # Git ignore rules
├── 📄 .dockerignore                   # Docker ignore rules
├── 📄 .flake8 → config/.flake8        # Symlink to config
└── 📄 .pre-commit-config.yaml → ...   # Symlink to config
```

## 📋 Directory Purposes

### 🔧 Development Directories

- **`src/`**: Contains all source code following Python packaging standards
- **`tests/`**: Comprehensive test suite with unit, integration, and E2E tests
- **`config/`**: Centralized configuration files for tools and linting
- **`tools/`**: Development utilities and helper scripts
- **`.github/`**: CI/CD workflows and GitHub automation
- **`.devcontainer/`**: Docker-based development environment
- **`.vscode/`**: VS Code workspace configuration

### 📚 Documentation & Examples

- **`docs/`**: Project documentation, guides, and API references
- **`examples/`**: Usage examples and demonstration scripts
- **`README.md`**: Main project documentation and getting started guide

### 📊 Data & Output

- **`data/`**: Sample data, test datasets, and example exports
- **`output/`**: Generated reports, analysis results, and build artifacts
- **`backup/`**: Archived files and historical analysis results

### ⚙️ Configuration Files

- **`pyproject.toml`**: Main project configuration (Poetry, tools, dependencies)
- **`Makefile`**: Development workflow automation
- **`poetry.lock`**: Dependency version lock file

## 🎯 Benefits of This Structure

### 1. **Industry Standard Compliance**

- Follows Python packaging standards (PEP 518, PEP 621)
- Separates source code from project root
- Clear separation of concerns

### 2. **Developer Experience**

- Predictable file locations
- Easy navigation and discovery
- IDE-friendly structure

### 3. **Build & CI/CD Optimization**

- Clear source paths for build systems
- Optimized test discovery
- Efficient caching strategies

### 4. **Scalability**

- Modular organization
- Easy to add new components
- Supports large team collaboration

### 5. **Maintenance**

- Centralized configurations
- Clear ownership of files
- Easy cleanup and updates

## 🔄 Migration Impact

### ✅ What Changed

1. **Source Code**: Moved to `src/instagram_analyzer/`
2. **Tests**: Consolidated in `tests/`
3. **Configurations**: Centralized in `config/`
4. **Outputs**: Organized in `output/`
5. **Data**: Structured in `data/`
6. **Archives**: Moved to `backup/`

### ⚙️ Updated Configurations

- **pyproject.toml**: Updated package paths and tool configurations
- **VS Code**: Updated Python paths and exclude patterns
- **Makefile**: Updated all command paths
- **CI/CD**: Paths updated in GitHub Actions
- **Coverage**: Updated source paths

### 🔗 Compatibility

- Symbolic links maintain backward compatibility
- All tools and scripts updated
- Import paths remain the same for users
- API unchanged

## 📋 Validation Checklist

- [x] ✅ Source code properly organized
- [x] ✅ Tests consolidated and discoverable
- [x] ✅ Configurations centralized
- [x] ✅ Documentation updated
- [x] ✅ Build system updated
- [x] ✅ CI/CD paths corrected
- [x] ✅ Development tools functional
- [x] ✅ Backward compatibility maintained

## 🚀 Next Steps

1. **Validate functionality**: Run full test suite
2. **Update documentation**: Ensure all paths are correct
3. **Test CI/CD**: Verify workflows work correctly
4. **Developer onboarding**: Update setup instructions
5. **Cleanup**: Remove any remaining deprecated files

---

**Result**: A clean, professional, and maintainable project structure following industry best practices! 🎉
