#!/usr/bin/env python3
"""Example: Compact HTML Export for Large Instagram Datasets.

This example demonstrates how to generate smaller HTML reports
for large Instagram datasets using the compact export feature.
"""

from pathlib import Path

from instagram_analyzer import InstagramAnalyzer


def main():
    # Path to your Instagram data export
    data_path = Path("path/to/your/instagram/data")
    output_path = Path("output/compact_reports")

    print("🚀 Instagram Analyzer - Compact Export Example")
    print("=" * 50)

    # Initialize analyzer
    analyzer = InstagramAnalyzer(data_path)

    # Load data
    print("📊 Loading Instagram data...")
    analyzer.load_data()

    # Check dataset size
    total_posts = len(analyzer.posts)
    total_stories = len(analyzer.stories)
    total_reels = len(analyzer.reels)

    print(
        f"Dataset size: {total_posts} posts, {total_stories} stories, {total_reels} reels"
    )

    # Regular export (could be 20MB+ for large datasets)
    print("\n📄 Generating regular HTML report...")
    regular_report = analyzer.export_html(output_path / "regular", show_progress=True)
    regular_size = regular_report.stat().st_size / (1024 * 1024)  # MB
    print(f"Regular report size: {regular_size:.1f} MB")

    # Compact export (much smaller)
    print("\n📦 Generating compact HTML report...")
    compact_report = analyzer.export_html(
        output_path / "compact",
        compact=True,
        max_items=50,  # Only include top 50 items per section
        show_progress=True,
    )
    compact_size = compact_report.stat().st_size / (1024 * 1024)  # MB
    print(f"Compact report size: {compact_size:.1f} MB")

    # Size comparison
    reduction = ((regular_size - compact_size) / regular_size) * 100
    print(
        f"\n✅ Size reduction: {reduction:.1f}% ({regular_size:.1f}MB → {compact_size:.1f}MB)"
    )

    print("\n🎉 Reports generated successfully!")
    print(f"Regular report: {regular_report}")
    print(f"Compact report: {compact_report}")


if __name__ == "__main__":
    main()
