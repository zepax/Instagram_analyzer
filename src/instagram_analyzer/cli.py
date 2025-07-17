"""Command Line Interface for Instagram Analyzer."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .core import InstagramAnalyzer
from .exceptions import InstagramAnalyzerError
from .logging_config import get_logger, setup_logging
from .utils import validate_path

console = Console()


@click.group()
@click.version_option(version="0.2.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--log-level",
    default="INFO",
    help="Set logging level (DEBUG, INFO, WARNING, ERROR)",
)
@click.option("--log-file", help="Enable file logging to specified directory")
@click.pass_context
def main(
    ctx: click.Context, verbose: bool, log_level: str, log_file: Optional[str]
) -> None:
    """Instagram Analyzer - Advanced Instagram data analysis tool.

    Analyze your Instagram data export to generate insights, statistics,
    and visualizations about your Instagram activity.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # Setup logging
    log_dir = Path(log_file) if log_file else None
    setup_logging(
        level=log_level.upper(),
        log_dir=log_dir,
        enable_file_logging=log_file is not None,
        enable_structured_logging=True,
        enable_performance_logging=verbose,
    )

    logger = get_logger("cli")
    logger.info(f"Starting Instagram Analyzer v0.2.0 with log level: {log_level}")

    if verbose:
        console.print("[bold blue]Instagram Analyzer v0.2.0[/bold blue]")
        console.print("Advanced Instagram data analysis tool\n")


@main.command()
@click.argument("data_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for analysis results",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["html", "json", "pdf"]),
    default="html",
    help="Output format for reports",
)
@click.option("--include-media", is_flag=True, help="Include media analysis (slower)")
@click.option("--anonymize", is_flag=True, help="Anonymize sensitive data in reports")
@click.pass_context
def analyze(
    ctx: click.Context,
    data_path: Path,
    output: Optional[Path],
    format: str,
    include_media: bool,
    anonymize: bool,
) -> None:
    """Analyze Instagram data export and generate comprehensive reports.

    DATA_PATH: Path to your Instagram data export directory
    """
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        console.print(f"[bold]Analyzing Instagram data at:[/bold] {data_path}")
        console.print(f"[bold]Output format:[/bold] {format}")
        console.print(f"[bold]Include media analysis:[/bold] {include_media}")
        console.print(f"[bold]Anonymize data:[/bold] {anonymize}\n")

    logger = get_logger("cli.analyze")

    try:
        # Validate input path
        if not validate_path(data_path):
            error_msg = "Invalid data path provided"
            logger.error(error_msg, extra={"data_path": str(data_path)})
            console.print(f"[red]Error: {error_msg}[/red]")
            sys.exit(1)

        logger.info(f"Starting analysis of data at: {data_path}")

        # Initialize analyzer
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Load data
            task = progress.add_task("Loading Instagram data...", total=None)
            analyzer = InstagramAnalyzer(data_path)
            analyzer.load_data()
            progress.update(task, description="Data loaded successfully")

            # Run analysis
            progress.update(task, description="Running analysis...")
            results = analyzer.analyze(include_media=include_media)

            # Generate report
            progress.update(task, description="Generating report...")
            if output is None:
                output = Path.cwd() / "instagram_analysis"

            output.mkdir(exist_ok=True)

            if format == "html":
                report_path = analyzer.export_html(output, anonymize=anonymize)
            elif format == "json":
                report_path = analyzer.export_json(output, anonymize=anonymize)
            elif format == "pdf":
                report_path = analyzer.export_pdf(output, anonymize=anonymize)

            progress.update(task, description="Analysis complete!")

        # Display results summary
        _display_summary(results)
        console.print(f"\n[green]✓[/green] Report generated: [bold]{report_path}[/bold]")
        logger.info(f"Analysis completed successfully. Report saved to: {report_path}")

    except InstagramAnalyzerError as e:
        # Handle custom application errors
        logger.error(f"Analysis failed: {e}", extra=e.context)
        console.print(f"[red]Analysis Error: {e.message}[/red]")
        if verbose and e.context:
            console.print(f"[yellow]Context: {e.context}[/yellow]")
        sys.exit(1)

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
        console.print(f"[red]Unexpected error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("data_path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def validate(ctx: click.Context, data_path: Path) -> None:
    """Validate Instagram data export structure and integrity.

    DATA_PATH: Path to your Instagram data export directory
    """
    verbose = ctx.obj.get("verbose", False)

    if verbose:
        console.print(f"[bold]Validating Instagram data at:[/bold] {data_path}\n")

    try:
        analyzer = InstagramAnalyzer(data_path)
        validation_results = analyzer.validate_data()

        # Display validation results
        table = Table(title="Data Validation Results")
        table.add_column("Check", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Details", style="green")

        for check, result in validation_results.items():
            status = "✓ Pass" if result["valid"] else "✗ Fail"
            details = result.get("details", "")
            table.add_row(check, status, details)

        console.print(table)

        # Overall result
        all_valid = all(r["valid"] for r in validation_results.values())
        if all_valid:
            console.print("\n[green]✓ All validation checks passed![/green]")
        else:
            console.print("\n[red]✗ Some validation checks failed[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("data_path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def info(ctx: click.Context, data_path: Path) -> None:
    """Display basic information about Instagram data export.

    DATA_PATH: Path to your Instagram data export directory
    """
    verbose = ctx.obj.get("verbose", False)

    try:
        analyzer = InstagramAnalyzer(data_path)
        info_data = analyzer.get_basic_info()

        # Display info in a table
        table = Table(title="Instagram Data Export Information")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        for key, value in info_data.items():
            table.add_row(key.replace("_", " ").title(), str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error getting info: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


def _display_summary(results: dict) -> None:
    """Display analysis results summary."""
    table = Table(title="Analysis Summary")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    # Basic stats
    table.add_row("Total Posts", str(results.get("total_posts", 0)))
    table.add_row("Total Stories", str(results.get("total_stories", 0)))
    table.add_row("Total Comments", str(results.get("total_comments", 0)))
    table.add_row("Total Likes", str(results.get("total_likes", 0)))
    table.add_row("Date Range", results.get("date_range", "Unknown"))

    console.print(table)


if __name__ == "__main__":
    main()
