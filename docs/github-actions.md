# GitHub Actions Configuration Guide

This document explains the GitHub Actions workflows configured for the Instagram Analyzer project.

## Overview

The project uses GitHub Actions for continuous integration, security scanning, and automated releases. All workflows are located in `.github/workflows/`.

## Workflows

### 1. Main CI Pipeline (`ci.yml`)

**Trigger**: Push to `main` and pull requests

**What it does**:
- Tests across Python 3.9, 3.10, 3.11, and 3.12
- Runs on Ubuntu, Windows, and macOS
- Code quality checks (black, isort, flake8, mypy)
- Security scanning (bandit, safety)
- Test execution with coverage reporting
- Dependency validation

**Key features**:
- Matrix testing across multiple Python versions and OS
- Poetry caching for faster builds
- Coverage reporting to GitHub
- Fails fast on critical errors

### 2. Security Analysis (`codeql.yml`)

**Trigger**: Push to `main`, pull requests, and weekly schedule

**What it does**:
- GitHub's CodeQL security analysis
- Scans for common vulnerabilities
- Generates security alerts
- Supports Python language analysis

**Key features**:
- Automated security scanning
- Weekly scheduled runs
- Integration with GitHub Security tab

### 3. Dependency Review (`dependency-review.yml`)

**Trigger**: Pull requests only

**What it does**:
- Reviews new dependencies for vulnerabilities
- Checks license compatibility
- Prevents insecure dependencies from being merged

**Key features**:
- Automated dependency security checking
- Blocks PRs with vulnerable dependencies
- License compliance validation

### 4. Release Pipeline (`release.yml`)

**Trigger**: Tags matching `v*.*.*` pattern

**What it does**:
- Creates GitHub releases with changelog
- Builds and publishes to PyPI (when configured)
- Generates release artifacts

**Key features**:
- Automated version releases
- PyPI publishing capability
- Changelog generation from commits

## Configuration

### Secrets Required

For full functionality, configure these GitHub secrets:

```bash
# For PyPI publishing (optional)
PYPI_API_TOKEN=your_pypi_token

# For enhanced security scanning (optional)
CODECOV_TOKEN=your_codecov_token
```

### Environment Variables

The workflows use these environment variables:

- `PYTHON_VERSION`: Default Python version (3.11)
- `POETRY_VERSION`: Poetry version to use
- `COVERAGE_THRESHOLD`: Minimum coverage percentage

## Customization

### Adding New Python Versions

Edit the matrix in `ci.yml`:

```yaml
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]  # Add new versions
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### Modifying Code Quality Checks

Edit the code quality section in `ci.yml`:

```yaml
- name: Run linting
  run: |
    poetry run black --check .
    poetry run isort --check-only .
    poetry run flake8 .
    poetry run mypy .
    # Add new tools here
```

### Custom Security Scanning

Modify `codeql.yml` to add custom queries:

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: python
    queries: security-extended,security-and-quality  # Add custom queries
```

## Status Badges

Add these badges to your README:

```markdown
[![CI](https://github.com/yourusername/instagram-analyzer/workflows/CI/badge.svg)](https://github.com/yourusername/instagram-analyzer/actions/workflows/ci.yml)
[![Security](https://github.com/yourusername/instagram-analyzer/workflows/CodeQL/badge.svg)](https://github.com/yourusername/instagram-analyzer/actions/workflows/codeql.yml)
```

## Troubleshooting

### Common Issues

1. **Poetry Installation Fails**
   - Check Poetry version compatibility
   - Verify Python version support

2. **Tests Fail on Specific OS**
   - Check for OS-specific path issues
   - Verify cross-platform compatibility

3. **Security Scan Failures**
   - Review CodeQL results in Security tab
   - Update dependencies with vulnerabilities

4. **Release Pipeline Issues**
   - Verify tag format matches `v*.*.*`
   - Check PyPI token configuration

### Debug Steps

1. Check workflow logs in GitHub Actions tab
2. Verify secret configuration
3. Test locally with same Python versions
4. Review dependency versions

## Best Practices

1. **Commit Messages**: Use conventional commits for better release notes
2. **Version Tags**: Follow semantic versioning
3. **Security**: Regularly update dependencies
4. **Testing**: Maintain high test coverage
5. **Documentation**: Update this guide when adding new workflows

## Local Development

To run the same checks locally:

```bash
# Install dependencies
poetry install

# Run code quality checks
make lint

# Run tests
make test

# Run security checks
make security

# Full CI simulation
make ci
```
