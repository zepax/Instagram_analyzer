import types
import pytest
from instagram_analyzer.core.analyzer import InstagramAnalyzer


def test_generate_html_report_uses_html_escape(monkeypatch):
    analyzer = types.SimpleNamespace()
    analyzer.posts = [1, 2, 3]
    analyzer.stories = [1]
    analyzer.reels = [1, 2]

    escaped_values = []

    def fake_escape(value: str) -> str:
        escaped_values.append(value)
        return f"ESCAPED({value})"

    monkeypatch.setattr(
        "instagram_analyzer.core.analyzer.html.escape",
        fake_escape,
    )

    report = InstagramAnalyzer._generate_html_report(analyzer)

    assert "ESCAPED(3)" in report
    assert "ESCAPED(1)" in report
    assert "ESCAPED(2)" in report
    assert escaped_values == ["3", "1", "2"]
