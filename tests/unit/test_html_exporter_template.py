from importlib import resources


def test_template_contains_nav_and_hourly_chart():
    template = (
        resources.files("instagram_analyzer.templates")
        .joinpath("report.html")
        .read_text()
    )
    assert "nav-menu" in template
    assert "hourly-chart" in template
