#!/usr/bin/env python3
"""Workflow Validation Script.

This script validates that the project follows the established Git workflow
and coding standards. It's designed to help AI assistants and developers
ensure they're following the correct procedures.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


class WorkflowValidator:
    """Validates project workflow compliance."""

    def __init__(self, project_root: Path):
        """Initialize the validator."""
        self.project_root = project_root
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        console.print(
            Panel(
                "🔍 [bold blue]Instagram Analyzer - Workflow Validation[/bold blue]",
                subtitle="Ensuring workflow compliance",
            )
        )

        checks = [
            ("Git Branch Structure", self.validate_git_branches),
            ("Code Quality Setup", self.validate_code_quality),
            ("Documentation", self.validate_documentation),
            ("Project Structure", self.validate_project_structure),
            ("Development Tools", self.validate_dev_tools),
            ("Workflow Scripts", self.validate_workflow_scripts),
        ]

        all_passed = True
        for check_name, check_func in checks:
            console.print(f"\n🔍 [bold]Checking {check_name}...[/bold]")
            try:
                passed = check_func()
                if passed:
                    console.print(f"✅ {check_name} - [green]PASSED[/green]")
                else:
                    console.print(f"❌ {check_name} - [red]FAILED[/red]")
                    all_passed = False
            except Exception as e:
                console.print(f"💥 {check_name} - [red]ERROR: {e}[/red]")
                all_passed = False

        self.print_summary()
        return all_passed

    def validate_git_branches(self) -> bool:
        """Validate Git branch structure."""
        try:
            # Check current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            current_branch = result.stdout.strip()

            # Check if we're on a valid working branch
            valid_branches = ["v0.2.05", "main"]
            if current_branch.startswith(("feature/", "bugfix/", "hotfix/")):
                valid_branches.append(current_branch)

            if current_branch not in valid_branches and not current_branch.startswith(
                ("feature/", "bugfix/", "hotfix/")
            ):
                self.errors.append(
                    f"Invalid branch: {current_branch}. Should be v0.2.05 or feature/bugfix/hotfix branch"
                )
                return False

            # Check if v0.2.05 exists
            result = subprocess.run(
                ["git", "branch", "--list", "v0.2.05"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if not result.stdout.strip():
                self.errors.append("v0.2.05 branch does not exist")
                return False

            self.info.append(f"Current branch: {current_branch}")
            return True

        except Exception as e:
            self.errors.append(f"Git validation failed: {e}")
            return False

    def validate_code_quality(self) -> bool:
        """Validate code quality tools setup."""
        required_tools = [
            ("poetry", "Poetry dependency manager"),
            ("black", "Code formatter"),
            ("flake8", "Code linter"),
            ("mypy", "Type checker"),
            ("pytest", "Testing framework"),
        ]

        missing_tools = []
        for tool, description in required_tools:
            try:
                result = subprocess.run(["which", tool], capture_output=True, text=True)
                if result.returncode != 0:
                    # Try with poetry run
                    result = subprocess.run(
                        ["poetry", "run", tool, "--version"],
                        capture_output=True,
                        text=True,
                        cwd=self.project_root,
                    )
                    if result.returncode != 0:
                        missing_tools.append(f"{tool} ({description})")
            except Exception:
                missing_tools.append(f"{tool} ({description})")

        if missing_tools:
            self.errors.append(f"Missing tools: {', '.join(missing_tools)}")
            return False

        # Check for pre-commit hooks
        pre_commit_config = self.project_root / ".pre-commit-config.yaml"
        if not pre_commit_config.exists():
            self.warnings.append("No pre-commit configuration found")

        return True

    def validate_documentation(self) -> bool:
        """Validate documentation files."""
        required_docs = [
            ("README.md", "Project overview"),
            ("CLAUDE.md", "AI assistant instructions"),
            ("docs/WORKFLOW.md", "Git workflow guide"),
            (".github/copilot-instructions.md", "AI workflow guidelines"),
        ]

        missing_docs = []
        for doc_path, description in required_docs:
            full_path = self.project_root / doc_path
            if not full_path.exists():
                missing_docs.append(f"{doc_path} ({description})")
            else:
                # Check if file is not empty
                if full_path.stat().st_size == 0:
                    missing_docs.append(f"{doc_path} (empty file)")

        if missing_docs:
            self.errors.append(f"Missing documentation: {', '.join(missing_docs)}")
            return False

        return True

    def validate_project_structure(self) -> bool:
        """Validate project structure."""
        required_dirs = [
            "src/instagram_analyzer",
            "tests",
            "scripts",
            "docs",
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            self.errors.append(f"Missing directories: {', '.join(missing_dirs)}")
            return False

        # Check for legacy structure warning
        legacy_dir = self.project_root / "instagram_analyzer"
        if legacy_dir.exists():
            self.warnings.append(
                "Legacy instagram_analyzer/ directory found. Use src/instagram_analyzer/"
            )

        return True

    def validate_dev_tools(self) -> bool:
        """Validate development tools."""
        # Check Makefile
        makefile = self.project_root / "Makefile"
        if not makefile.exists():
            self.errors.append("Makefile not found")
            return False

        # Check pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if not pyproject.exists():
            self.errors.append("pyproject.toml not found")
            return False

        # Check for quality targets in Makefile
        makefile_content = makefile.read_text()
        required_targets = ["quality", "test", "format", "lint", "type-check"]
        missing_targets = []
        for target in required_targets:
            if f".PHONY: {target}" not in makefile_content:
                missing_targets.append(target)

        if missing_targets:
            self.warnings.append(
                f"Missing Makefile targets: {', '.join(missing_targets)}"
            )

        return True

    def validate_workflow_scripts(self) -> bool:
        """Validate workflow automation scripts."""
        required_scripts = [
            "scripts/git-automation.py",
            "scripts/setup-git-automation.sh",
        ]

        missing_scripts = []
        for script_path in required_scripts:
            full_path = self.project_root / script_path
            if not full_path.exists():
                missing_scripts.append(script_path)
            elif not os.access(full_path, os.X_OK):
                self.warnings.append(f"{script_path} is not executable")

        if missing_scripts:
            self.errors.append(f"Missing scripts: {', '.join(missing_scripts)}")
            return False

        return True

    def print_summary(self) -> None:
        """Print validation summary."""
        console.print("\n" + "=" * 60)
        console.print("[bold blue]📋 WORKFLOW VALIDATION SUMMARY[/bold blue]")
        console.print("=" * 60)

        if self.errors:
            console.print(f"\n❌ [red]ERRORS ({len(self.errors)})[/red]:")
            for error in self.errors:
                console.print(f"  • {error}")

        if self.warnings:
            console.print(f"\n⚠️  [yellow]WARNINGS ({len(self.warnings)})[/yellow]:")
            for warning in self.warnings:
                console.print(f"  • {warning}")

        if self.info:
            console.print(f"\n📢 [blue]INFO ({len(self.info)})[/blue]:")
            for info in self.info:
                console.print(f"  • {info}")

        # Overall status
        if not self.errors:
            console.print("\n✅ [green]WORKFLOW VALIDATION PASSED[/green]")
            console.print("🎉 Project follows the established workflow guidelines!")
        else:
            console.print("\n❌ [red]WORKFLOW VALIDATION FAILED[/red]")
            console.print("🔧 Please fix the errors above before continuing development.")

        # Quick fix suggestions
        if self.errors or self.warnings:
            console.print("\n🔧 [bold]QUICK FIXES[/bold]:")
            console.print("  • Run: make setup-dev")
            console.print("  • Run: make git-setup")
            console.print("  • Check: git branch (should be v0.2.05 or feature branch)")
            console.print("  • Run: make quality")


def main() -> None:
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    validator = WorkflowValidator(project_root)

    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
