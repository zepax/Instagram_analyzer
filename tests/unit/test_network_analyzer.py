from datetime import datetime, timezone

import pytest

from instagram_analyzer.analyzers.network_analysis import NetworkAnalyzer
from instagram_analyzer.models import Like, Media, MediaType, Post, User


@pytest.fixture
def sample_posts():
    # Create minimal Media objects for posts
    media = Media(
        uri="test.jpg",
        media_type=MediaType.IMAGE,
        creation_timestamp=datetime.now(timezone.utc),
    )

    # Create Like objects with proper structure
    like_bob = Like(user=User(username="bob"), timestamp=datetime.now(timezone.utc))
    like_alice = Like(user=User(username="alice"), timestamp=datetime.now(timezone.utc))

    # Minimal mock posts for network analysis
    return [
        Post(
            media=[media],
            timestamp=datetime.now(timezone.utc),
            likes=[like_bob],
            comments=[],
        ),
        Post(
            media=[media],
            timestamp=datetime.now(timezone.utc),
            likes=[like_alice],
            comments=[],
        ),
        Post(
            media=[media],
            timestamp=datetime.now(timezone.utc),
            likes=[like_alice, like_bob],
            comments=[],
        ),
    ]


def test_network_analyzer_basic(sample_posts):
    analyzer = NetworkAnalyzer(owner_username="alice")
    result = analyzer.analyze(sample_posts)
    assert isinstance(result, dict)
    assert "nodes" in result
    assert "links" in result  # NetworkAnalyzer returns "links", not "edges"
    assert any(node["id"] == "alice" for node in result["nodes"])
    assert any(
        link["source"] == "alice" or link["target"] == "alice" for link in result["links"]
    )
