#!/usr/bin/env python3
"""
Test Chart.js inclusion in HTML exporter
"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import after path setup
from instagram_analyzer.exporters.html_exporter import HTMLExporter  # noqa: E402


def test_chart_js():
    """Test that Chart.js is properly included in the HTML template"""

    print("🧪 Testing Chart.js inclusion...")

    try:
        # Create exporter
        exporter = HTMLExporter()

        # Test template loading
        template = exporter.template
        print(f"✅ Template loaded: {len(template)} characters")

        # Generate some test data
        test_data = {
            "overview": {"total_posts": 5, "total_likes": 100},
            "charts_data": {
                "temporal_analysis": {"labels": ["Jan", "Feb", "Mar"], "data": [1, 2, 2]},
                "engagement_analysis": {
                    "labels": ["Post 1", "Post 2", "Post 3"],
                    "data": [10, 20, 15],
                },
            },
            "posts": [
                {"timestamp": "2024-01-01", "caption": "Test post 1"},
                {"timestamp": "2024-01-02", "caption": "Test post 2"},
            ],
        }

        # Render template
        html_content = exporter._render_template(test_data)
        print(f"✅ Template rendered: {len(html_content)} characters")

        # Check for Chart.js
        chart_js_checks = [
            ("chart.js", "Chart.js library reference"),
            ("cdn.jsdelivr.net/npm/chart.js", "Chart.js CDN URL"),
            ("d3js.org/d3.v7.min.js", "D3.js CDN URL"),
            ("new Chart(", "Chart.js usage"),
            ("temporalChart", "Temporal chart element"),
            ("engagementChart", "Engagement chart element"),
        ]

        print("\n🔍 Checking Chart.js inclusion:")
        all_checks_passed = True
        for check, description in chart_js_checks:
            if check in html_content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_checks_passed = False

        # Save test output
        output_file = project_root / "test_chart_output.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\n📄 Test HTML saved to: {output_file}")

        return all_checks_passed

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_chart_js()
    if success:
        print("\n🎉 All Chart.js checks passed!")
    else:
        print("\n💥 Some Chart.js checks failed!")

    sys.exit(0 if success else 1)
