#!/usr/bin/env python3
"""
Git Automation Script for Instagram Analyzer

This script automates Git branch creation and management for major changes,
following the project's development guidelines and TODO.md structure.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()

# Configuration based on TODO.md phases
CHANGE_TYPES = {
    "feature": {
        "prefix": "feat",
        "description": "New feature implementation",
        "phases": [
            "foundation",
            "performance",
            "ml",
            "ui",
            "extensibility",
            "security",
            "enterprise",
        ],
    },
    "bugfix": {
        "prefix": "fix",
        "description": "Bug fix or correction",
        "phases": ["critical", "high", "medium", "low"],
    },
    "optimization": {
        "prefix": "perf",
        "description": "Performance optimization",
        "phases": ["memory", "speed", "caching", "parallel"],
    },
    "documentation": {
        "prefix": "docs",
        "description": "Documentation updates",
        "phases": ["api", "guides", "examples", "readme"],
    },
    "testing": {
        "prefix": "test",
        "description": "Testing improvements",
        "phases": ["unit", "integration", "e2e", "coverage"],
    },
    "infrastructure": {
        "prefix": "infra",
        "description": "Infrastructure and tooling",
        "phases": ["ci", "dev-env", "build", "deploy"],
    },
}

# Version increment patterns
VERSION_PATTERNS = {
    "major": ["breaking", "architecture", "ml-framework", "complete-rewrite"],
    "minor": ["feature", "enhancement", "new-data-types", "export-format"],
    "patch": ["bugfix", "optimization", "documentation", "testing"],
}


class GitAutomation:
    """Git automation for branch management and versioning."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / ".git-automation.json"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load automation configuration."""
        default_config = {
            "base_branch": "main",
            "auto_version": True,
            "auto_commit": False,
            "require_tests": True,
            "branch_history": [],
            "version_history": [],
        }

        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")

        return default_config

    def _save_config(self) -> None:
        """Save automation configuration."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")

    def _run_git_command(self, command: list[str]) -> tuple[bool, str]:
        """Execute git command and return success status and output."""
        try:
            result = subprocess.run(
                ["git"] + command, capture_output=True, text=True, cwd=self.project_root
            )
            return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
        except Exception as e:
            return False, str(e)

    def _get_current_branch(self) -> str:
        """Get current Git branch."""
        success, branch = self._run_git_command(["branch", "--show-current"])
        return branch if success else "main"

    def _get_current_version(self) -> str:
        """Get current version from pyproject.toml."""
        try:
            pyproject_path = self.project_root / "pyproject.toml"
            with open(pyproject_path) as f:
                for line in f:
                    if line.startswith("version ="):
                        return line.split('"')[1]
        except (FileNotFoundError, OSError, IndexError) as e:
            print(f"Warning: Could not read version from pyproject.toml: {e}")
        return "0.1.0"

    def _increment_version(self, current_version: str, increment_type: str) -> str:
        """Increment version based on change type."""
        parts = current_version.split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        return f"{major}.{minor}.{patch}"

    def _determine_version_increment(self, change_type: str, description: str) -> str:
        """Determine version increment type based on change description."""
        description_lower = description.lower()

        for increment_type, keywords in VERSION_PATTERNS.items():
            if any(keyword in description_lower for keyword in keywords):
                return increment_type

        # Default based on change type
        if change_type in ["feature", "optimization"]:
            return "minor"
        else:
            return "patch"

    def _update_version_files(self, new_version: str) -> None:
        """Update version in all relevant files."""
        files_to_update = [
            ("pyproject.toml", f'version = "{new_version}"'),
            ("src/instagram_analyzer/__init__.py", f'__version__ = "{new_version}"'),
            (
                "src/instagram_analyzer/cli.py",
                f'@click.version_option(version="{new_version}")',
            ),
        ]

        for file_path, version_pattern in files_to_update:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path) as f:
                        content = f.read()

                    # Update version line
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if "version" in line and ("=" in line or "(" in line):
                            if "pyproject.toml" in file_path and line.startswith(
                                "version ="
                            ):
                                lines[i] = f'version = "{new_version}"'
                            elif "__init__.py" in file_path and line.startswith(
                                "__version__ ="
                            ):
                                lines[i] = f'__version__ = "{new_version}"'
                            elif (
                                "cli.py" in file_path and "@click.version_option" in line
                            ):
                                lines[i] = (
                                    f'@click.version_option(version="{new_version}")'
                                )
                            break

                    with open(full_path, "w") as f:
                        f.write("\n".join(lines))

                    console.print(f"[green]✓[/green] Updated version in {file_path}")

                except Exception as e:
                    console.print(f"[red]✗[/red] Failed to update {file_path}: {e}")

    def create_feature_branch(
        self, change_type: str, description: str, phase: Optional[str] = None
    ) -> str:
        """Create a new feature branch with automatic naming."""
        # Generate branch name
        timestamp = datetime.now().strftime("%Y%m%d")
        clean_description = description.lower().replace(" ", "-").replace("_", "-")
        clean_description = "".join(
            c for c in clean_description if c.isalnum() or c == "-"
        )

        prefix = CHANGE_TYPES[change_type]["prefix"]
        if phase:
            branch_name = f"{prefix}/{phase}-{clean_description}-{timestamp}"
        else:
            branch_name = f"{prefix}/{clean_description}-{timestamp}"

        # Check if branch already exists
        success, _ = self._run_git_command(["rev-parse", "--verify", branch_name])
        if success:
            console.print(f"[yellow]Branch {branch_name} already exists[/yellow]")
            return branch_name

        # Create and switch to new branch
        success, output = self._run_git_command(["checkout", "-b", branch_name])
        if not success:
            console.print(f"[red]Failed to create branch: {output}[/red]")
            return ""

        # Update config
        self.config["branch_history"].append(
            {
                "branch": branch_name,
                "type": change_type,
                "description": description,
                "phase": phase,
                "created_at": datetime.now().isoformat(),
                "status": "active",
            }
        )
        self._save_config()

        console.print(
            f"[green]✓[/green] Created and switched to branch: [bold]{branch_name}[/bold]"
        )
        return branch_name

    def auto_version_and_commit(
        self, change_type: str, description: str, files: Optional[list[str]] = None
    ) -> None:
        """Automatically version and commit changes."""
        if not self.config["auto_version"]:
            return

        # Get current version and increment
        current_version = self._get_current_version()
        increment_type = self._determine_version_increment(change_type, description)
        new_version = self._increment_version(current_version, increment_type)

        console.print(
            f"[blue]Version update: {current_version} → {new_version} ({increment_type})[/blue]"
        )

        # Update version files
        self._update_version_files(new_version)

        # Update version history
        self.config["version_history"].append(
            {
                "version": new_version,
                "previous": current_version,
                "type": increment_type,
                "description": description,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self._save_config()

        # Auto-commit if enabled
        if self.config["auto_commit"]:
            version_files = [
                "pyproject.toml",
                "src/instagram_analyzer/__init__.py",
                "src/instagram_analyzer/cli.py",
            ]
            all_files = (files or []) + version_files
            self._commit_changes(description, all_files)

    def _commit_changes(
        self, description: str, files: Optional[list[str]] = None
    ) -> None:
        """Commit changes with standardized message."""
        if files:
            for file in files:
                self._run_git_command(["add", file])
        else:
            self._run_git_command(["add", "."])

        commit_message = f"{description}\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"

        success, output = self._run_git_command(["commit", "-m", commit_message])
        if success:
            console.print(f"[green]✓[/green] Committed changes: {description}")
        else:
            console.print(f"[red]✗[/red] Failed to commit: {output}")

    def show_branch_history(self) -> None:
        """Display branch history."""
        if not self.config["branch_history"]:
            console.print("[yellow]No branch history available[/yellow]")
            return

        table = Table(title="Git Branch History")
        table.add_column("Branch", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Phase", style="blue")
        table.add_column("Created", style="dim")
        table.add_column("Status", style="yellow")

        for branch_info in self.config["branch_history"][-10:]:  # Show last 10
            table.add_row(
                branch_info["branch"],
                branch_info["type"],
                (
                    branch_info["description"][:50] + "..."
                    if len(branch_info["description"]) > 50
                    else branch_info["description"]
                ),
                branch_info.get("phase", ""),
                branch_info["created_at"][:10],
                branch_info["status"],
            )

        console.print(table)

    def interactive_branch_creation(self) -> None:
        """Interactive branch creation workflow."""
        console.print(
            "\n[bold blue]🚀 Git Automation - Create Feature Branch[/bold blue]"
        )

        # Select change type
        console.print("\n[bold]Select change type:[/bold]")
        for i, (key, value) in enumerate(CHANGE_TYPES.items(), 1):
            console.print(f"  {i}. {key} - {value['description']}")

        while True:
            try:
                choice = int(Prompt.ask("Enter choice (1-6)"))
                if 1 <= choice <= len(CHANGE_TYPES):
                    change_type = list(CHANGE_TYPES.keys())[choice - 1]
                    break
                else:
                    console.print("[red]Invalid choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a number.[/red]")

        # Select phase (optional)
        phases = CHANGE_TYPES[change_type]["phases"]
        console.print(f"\n[bold]Select phase for {change_type}:[/bold]")
        for i, phase in enumerate(phases, 1):
            console.print(f"  {i}. {phase}")

        phase_choice = Prompt.ask(
            "Enter phase choice (or press Enter to skip)", default=""
        )
        selected_phase: Optional[str] = (
            phases[int(phase_choice) - 1]
            if phase_choice.isdigit() and 1 <= int(phase_choice) <= len(phases)
            else None
        )

        # Get description
        description = Prompt.ask("\n[bold]Enter feature description[/bold]")

        # Create branch
        branch_name = self.create_feature_branch(change_type, description, selected_phase)

        if branch_name:
            # Ask about version increment
            if Confirm.ask(
                f"\n[bold]Auto-increment version for this {change_type}?[/bold]"
            ):
                self.auto_version_and_commit(change_type, description)

            console.print(f"\n[green]✅ Ready to work on: {branch_name}[/green]")
            console.print(
                f"[dim]When finished, create a PR to merge back to {self.config['base_branch']}[/dim]"
            )


@click.command()
@click.option("--interactive", "-i", is_flag=True, help="Interactive branch creation")
@click.option(
    "--type", "-t", type=click.Choice(list(CHANGE_TYPES.keys())), help="Change type"
)
@click.option("--description", "-d", help="Change description")
@click.option("--phase", "-p", help="Development phase")
@click.option("--history", "-h", is_flag=True, help="Show branch history")
@click.option("--config", "-c", is_flag=True, help="Show current configuration")
def main(
    interactive: bool,
    type: str,
    description: str,
    phase: str,
    history: bool,
    config: bool,
) -> None:
    """Git automation tool for Instagram Analyzer project."""
    project_root = Path.cwd()
    automation = GitAutomation(project_root)

    if history:
        automation.show_branch_history()
        return

    if config:
        console.print_json(data=automation.config)
        return

    if interactive:
        automation.interactive_branch_creation()
        return

    if type and description:
        branch_name = automation.create_feature_branch(type, description, phase)
        if branch_name:
            automation.auto_version_and_commit(type, description)
    else:
        console.print(
            "[red]Please provide --type and --description, or use --interactive[/red]"
        )
        console.print(
            "Example: python scripts/git-automation.py --type feature --description 'Add compact HTML reports'"
        )


if __name__ == "__main__":
    main()
