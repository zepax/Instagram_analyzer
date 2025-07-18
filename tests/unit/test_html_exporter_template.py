import json
from importlib import resources

from instagram_analyzer.exporters import HTMLExporter


def test_template_contains_nav_and_hourly_chart():
    template = (
        resources.files("instagram_analyzer.templates")
        .joinpath("report.html")
        .read_text()
    )
    assert "nav-menu" in template
    assert "hourly-chart" in template
    assert "network-graph" in template


def test_template_contains_key_placeholders():
    """Verify essential placeholder elements exist in the HTML template."""
    template = (
        resources.files("instagram_analyzer.templates")
        .joinpath("report.html")
        .read_text()
    )

    placeholders = [
        "overview-stats",
        "temporal-analysis",
        "engagement-analysis",
        "content-analysis",
        "posts-gallery",
        "network-graph",
    ]

    for name in placeholders:
        assert name in template


def test_render_template_injects_json():
    """Ensure _render_template embeds JSON data correctly."""
    exporter = HTMLExporter()
    data = {
        "metadata": {"generated_at": "2023-01-01"},
        "overview": {"posts": 1},
        "temporal_analysis": {"by_month": {"2023-01": 1}},
        "engagement_analysis": {"top_posts": []},
        "content_analysis": {"hashtags": {"total_unique": 0}},
        "posts": [],
        "charts_data": {},
        "network_graph": {"nodes": [], "links": []},
    }

    rendered = exporter._render_template(data)

    assert json.dumps(data["metadata"], default=str) in rendered
    assert json.dumps(data["overview"], default=str) in rendered
    assert json.dumps(data["temporal_analysis"], default=str) in rendered
    assert json.dumps(data["engagement_analysis"], default=str) in rendered
    assert json.dumps(data["network_graph"], default=str) in rendered
