import pytest

from instagram_analyzer.analyzers.network_analysis import NetworkAnalyzer
from instagram_analyzer.models import Post, User


@pytest.fixture
def sample_posts():
    # Minimal mock posts for network analysis
    return [
        Post(
            id=1, user=User(username="alice"), likes=[User(username="bob")], comments=[]
        ),
        Post(
            id=2, user=User(username="bob"), likes=[User(username="alice")], comments=[]
        ),
        Post(
            id=3,
            user=User(username="carol"),
            likes=[User(username="alice"), User(username="bob")],
            comments=[],
        ),
    ]


def test_network_analyzer_basic(sample_posts):
    analyzer = NetworkAnalyzer(owner_username="alice")
    result = analyzer.analyze(sample_posts)
    assert isinstance(result, dict)
    assert "nodes" in result
    assert "edges" in result
    assert any(node["id"] == "alice" for node in result["nodes"])
    assert any(
        edge["source"] == "alice" or edge["target"] == "alice"
        for edge in result["edges"]
    )
