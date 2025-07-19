import json
import os

import pytest

from instagram_analyzer.analyzers.network_analysis import NetworkAnalyzer
from instagram_analyzer.parsers.json_parser import JSONParser


@pytest.fixture(scope="module")
def real_owner_username():
    # Anonymized username for privacy
    return "anon_user_123"


@pytest.fixture(scope="module")
def real_posts():
    parser = JSONParser()
    # Use real Instagram export data
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    file_path = os.path.join(
        project_root,
        "data/sample_exports/instagram-pcFuHXmB/your_instagram_activity/media/posts_1.json",
    )
    posts = parser.parse_posts_from_file(file_path)
    return posts


@pytest.fixture(scope="module")
def real_followers():
    # Load followers from real export and anonymize them
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    file_path = os.path.join(
        project_root,
        "data/sample_exports/instagram-pcFuHXmB/connections/followers_and_following/followers_1.json",
    )
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Anonymize follower usernames
    followers = []
    for i, entry in enumerate(data[:20]):  # Limit to first 20 for test performance
        for s in entry.get("string_list_data", []):
            # Use anonymous identifiers instead of real usernames
            followers.append(f"anon_follower_{i}")
    return followers


@pytest.fixture(scope="module")
def real_following():
    # Load following from real export and anonymize them
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    file_path = os.path.join(
        project_root,
        "data/sample_exports/instagram-pcFuHXmB/connections/followers_and_following/following.json",
    )
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Anonymize following usernames
    following = []
    for i, entry in enumerate(
        data.get("relationships_following", [])[:20]
    ):  # Limit to first 20
        for s in entry.get("string_list_data", []):
            # Use anonymous identifiers instead of real usernames
            following.append(f"anon_following_{i}")
    return following


def test_network_analyzer_with_real_data(
    real_posts, real_owner_username, real_followers, real_following
):
    analyzer = NetworkAnalyzer(
        owner_username=real_owner_username,
        followers=real_followers,
        following=real_following,
    )
    result = analyzer.analyze(real_posts)
    assert isinstance(result, dict)
    assert "nodes" in result
    assert "links" in result
    # Owner should be present
    assert any(node["id"] == real_owner_username for node in result["nodes"])
    # There should be at least one link (real data)
    assert len(result["links"]) > 0
    # All nodes should have string IDs
    for node in result["nodes"]:
        assert isinstance(node["id"], str)
    # All links should have source/target
    for link in result["links"]:
        assert "source" in link and "target" in link
