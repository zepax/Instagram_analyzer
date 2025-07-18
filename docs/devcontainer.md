# VS Code Development Container

This project includes a complete VS Code development container configuration that provides a consistent, reproducible development environment.

## Features

- **Python 3.11** with Poetry for dependency management
- **Pre-configured extensions** for Python development, testing, and Git
- **Automated setup** with post-creation script
- **Development tools** including linting, formatting, and testing
- **Debug configurations** for various scenarios
- **Task runners** for common development tasks

## Quick Start

### Prerequisites

- [VS Code](https://code.visualstudio.com/)
- [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://www.docker.com/get-started)

### Using the Dev Container

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd Instagram_analyzer
   ```

2. **Open in VS Code**:

   ```bash
   code .
   ```

3. **Reopen in Container**:

   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Remote-Containers: Reopen in Container"
   - Select the command and wait for the container to build

4. **Start developing**:
   - The container will automatically run the setup script
   - All dependencies will be installed
   - Pre-commit hooks will be configured
   - You're ready to start coding!

## What's Included

### Development Environment

- **Python 3.11** with Poetry virtual environment
- **Git** with safe directory configuration
- **Oh My Zsh** for enhanced terminal experience
- **Development dependencies** automatically installed

### VS Code Extensions

#### Python Development

- Python extension with IntelliSense and debugging
- Black formatter for code formatting
- isort for import sorting
- Flake8 for linting
- MyPy for type checking
- Pytest for testing

#### Code Quality

- Ruff for fast Python linting
- Code spell checker
- Security extension

#### Version Control

- GitLens for enhanced Git capabilities
- GitHub Pull Requests and Issues
- GitHub Copilot (if available)

#### Utilities

- Jupyter support for notebooks
- Markdown support with preview
- TOML support for configuration files
- Makefile support

### Debug Configurations

Pre-configured launch configurations for:

- **Current File**: Debug the currently open Python file
- **CLI**: Debug the Instagram Analyzer CLI
- **Tests**: Run and debug tests
- **Specific Test**: Debug a specific test file
- **Analysis Example**: Run example analysis scripts

### Tasks

Common development tasks available via `Ctrl+Shift+P` → "Tasks: Run Task":

- **Install Dependencies**: Install all project dependencies
- **Run Tests**: Execute the test suite
- **Run Tests with Coverage**: Run tests with coverage reporting
- **Lint Code**: Run all linting tools
- **Format Code**: Auto-format all Python files
- **Security Check**: Run security analysis
- **Clean Cache**: Clean Python cache files
- **Build Package**: Build the Python package
- **Pre-commit All Files**: Run pre-commit hooks on all files

## Container Configuration

### File Structure

```
.devcontainer/
├── devcontainer.json    # Main container configuration
├── Dockerfile          # Container image definition
└── setup.sh           # Post-creation setup script

.vscode/
├── settings.json       # VS Code workspace settings
├── launch.json        # Debug configurations
├── tasks.json         # Task definitions
└── extensions.json    # Recommended extensions
```

### Environment Variables

The container sets up the following environment:

- `PYTHONPATH`: Set to workspace folder
- `POETRY_VENV_IN_PROJECT`: false (global venv)
- Poetry virtual environment in `/opt/poetry/venv`

### Port Forwarding

The following ports are forwarded for development:

- **8000**: Development server
- **8080**: Alternative server
- **3000**: Frontend server (if needed)

## Customization

### Adding Extensions

Edit `.devcontainer/devcontainer.json`:

```json
"customizations": {
    "vscode": {
        "extensions": [
            "existing.extension",
            "new.extension.id"
        ]
    }
}
```

### Modifying Settings

Edit `.vscode/settings.json` to customize VS Code behavior:

```json
{
  "python.defaultInterpreterPath": "/opt/poetry/venv/bin/python",
  "editor.formatOnSave": true
  // Add your custom settings
}
```

### Adding Tasks

Edit `.vscode/tasks.json` to add new development tasks:

```json
{
  "label": "My Custom Task",
  "type": "shell",
  "command": "poetry",
  "args": ["run", "my-command"],
  "group": "build"
}
```

## Troubleshooting

### Container Build Issues

1. **Docker not running**: Ensure Docker is running
2. **Permission issues**: Check Docker permissions
3. **Build failures**: Check Docker logs for specific errors

### Python Environment Issues

1. **Import errors**: Ensure Poetry environment is activated
2. **Missing dependencies**: Run "Install Dependencies" task
3. **Path issues**: Check PYTHONPATH is set correctly

### Extension Issues

1. **Extensions not loading**: Reload window (`Ctrl+Shift+P` → "Developer: Reload Window")
2. **Python extension not working**: Check interpreter path in status bar
3. **Linting not working**: Verify tools are installed in Poetry environment

### Common Commands

```bash
# Rebuild container
Ctrl+Shift+P → "Remote-Containers: Rebuild Container"

# Show container logs
Ctrl+Shift+P → "Remote-Containers: Show Container Log"

# Open new terminal in container
Ctrl+` (backtick)

# Install dependencies manually
poetry install --with dev

# Activate Poetry shell
poetry shell
```

## Performance Tips

1. **Use bind mounts** for better file performance (already configured)
2. **Exclude unnecessary files** from sync (configured in .dockerignore)
3. **Cache Poetry dependencies** (configured in Dockerfile)
4. **Use multi-stage builds** for smaller images

## Security

The development container:

- Runs as non-root user (`vscode`)
- Has limited sudo access for development needs
- Includes security scanning tools
- Follows Docker security best practices

## Contributing

When contributing to the dev container configuration:

1. Test changes locally
2. Update documentation
3. Ensure backward compatibility
4. Test on different platforms (Windows/Mac/Linux)

## Support

For issues with the development container:

1. Check this documentation
2. Review container logs
3. Open an issue with container configuration details
4. Include VS Code and Docker versions
