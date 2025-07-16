from instagram_analyzer.exporters import HTMLExporter


def test_template_contains_nav_and_hourly_chart():
    exporter = HTMLExporter()
    template = exporter.template
    assert "nav-menu" in template
    assert "hourly-chart" in template
