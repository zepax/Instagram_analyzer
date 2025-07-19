"""Edge case tests for the NetworkAnalyzer class."""

from datetime import datetime, timezone

import pytest

from instagram_analyzer.analyzers.network_analysis import NetworkAnalyzer
from instagram_analyzer.models import Comment, Like, Media, MediaType, Post, User


@pytest.fixture
def user_owner():
    """Fixture for the owner user."""
    return "owner_user"


@pytest.fixture
def follower_users():
    """Fixture for followers."""
    return ["follower1", "follower2", "follower3"]


@pytest.fixture
def following_users():
    """Fixture for following."""
    return ["following1", "following2"]


@pytest.fixture
def post_with_mentions():
    """Create a post with mentions in the caption."""
    # Create media
    media = Media(
        uri="test_mention.jpg",
        media_type=MediaType.IMAGE,
        creation_timestamp=datetime.now(timezone.utc),
    )

    # Create a post with mentions in caption
    return Post(
        media=[media],
        timestamp=datetime.now(timezone.utc),
        likes=[],
        comments=[],
        mentions=["mentioned1", "mentioned2"],  # Mentions in post caption
    )


@pytest.fixture
def post_with_comment_mentions():
    """Create a post with mentions in comments."""
    # Create media
    media = Media(
        uri="test_comment_mention.jpg",
        media_type=MediaType.IMAGE,
        creation_timestamp=datetime.now(timezone.utc),
    )

    # Create comments with mentions
    comment1 = Comment(
        text="Nice post @mentioned3!",
        timestamp=datetime.now(timezone.utc),
        author=User(username="commenter1"),
        mentions=["mentioned3"],
    )

    comment2 = Comment(
        text="I agree with @mentioned4 and @mentioned5",
        timestamp=datetime.now(timezone.utc),
        author=User(username="commenter2"),
        mentions=["mentioned4", "mentioned5"],
    )

    # Create post with comments containing mentions
    return Post(
        media=[media],
        timestamp=datetime.now(timezone.utc),
        likes=[],
        comments=[comment1, comment2],
        mentions=[],  # No mentions in caption
    )


@pytest.fixture
def post_with_likes():
    """Create a post with likes."""
    # Create media
    media = Media(
        uri="test_likes.jpg",
        media_type=MediaType.IMAGE,
        creation_timestamp=datetime.now(timezone.utc),
    )

    # Create likes
    like1 = Like(user=User(username="liker1"), timestamp=datetime.now(timezone.utc))
    like2 = Like(user=User(username="liker2"), timestamp=datetime.now(timezone.utc))

    # Create post with likes
    return Post(
        media=[media],
        timestamp=datetime.now(timezone.utc),
        likes=[like1, like2],
        comments=[],
        mentions=[],
    )


@pytest.fixture
def empty_post():
    """Create an empty post with no interactions."""
    # Create media
    media = Media(
        uri="empty.jpg",
        media_type=MediaType.IMAGE,
        creation_timestamp=datetime.now(timezone.utc),
    )

    # Create an empty post
    return Post(
        media=[media],
        timestamp=datetime.now(timezone.utc),
        likes=[],
        comments=[],
        mentions=[],
    )


def test_network_analyzer_with_mentions(user_owner, post_with_mentions):
    """Test NetworkAnalyzer with mentions in post captions."""
    analyzer = NetworkAnalyzer(owner_username=user_owner)
    result = analyzer.analyze([post_with_mentions])

    # Check that nodes include owner and mentioned users
    node_ids = [node["id"] for node in result["nodes"]]
    assert user_owner in node_ids
    assert "mentioned1" in node_ids
    assert "mentioned2" in node_ids

    # Check that edges exist from owner to mentioned users
    edges = [(link["source"], link["target"]) for link in result["links"]]
    assert (user_owner, "mentioned1") in edges
    assert (user_owner, "mentioned2") in edges


def test_network_analyzer_with_comment_mentions(user_owner, post_with_comment_mentions):
    """Test NetworkAnalyzer with mentions in comments."""
    analyzer = NetworkAnalyzer(owner_username=user_owner)
    result = analyzer.analyze([post_with_comment_mentions])

    # Check that nodes include owner, commenters and mentioned users
    node_ids = [node["id"] for node in result["nodes"]]
    assert user_owner in node_ids
    assert "commenter1" in node_ids
    assert "commenter2" in node_ids
    assert "mentioned3" in node_ids
    assert "mentioned4" in node_ids
    assert "mentioned5" in node_ids

    # Check that edges exist from commenters to owner
    edges = [(link["source"], link["target"]) for link in result["links"]]
    assert ("commenter1", user_owner) in edges
    assert ("commenter2", user_owner) in edges

    # Check that edges exist from commenters to mentioned users
    assert ("commenter1", "mentioned3") in edges
    assert ("commenter2", "mentioned4") in edges
    assert ("commenter2", "mentioned5") in edges


def test_network_analyzer_with_followers_following(
    user_owner, follower_users, following_users
):
    """Test NetworkAnalyzer with followers and following lists."""
    analyzer = NetworkAnalyzer(
        owner_username=user_owner, followers=follower_users, following=following_users
    )
    result = analyzer.analyze([])  # No posts, just testing follower/following

    # Check that nodes include owner, followers, and following
    node_ids = [node["id"] for node in result["nodes"]]
    assert user_owner in node_ids
    for follower in follower_users:
        assert follower in node_ids
    for following in following_users:
        assert following in node_ids

    # Check that edges exist from followers to owner
    edges = [(link["source"], link["target"]) for link in result["links"]]
    for follower in follower_users:
        assert (follower, user_owner) in edges

    # Check that edges exist from owner to following
    for follow in following_users:
        assert (user_owner, follow) in edges


def test_network_analyzer_empty_posts(user_owner):
    """Test NetworkAnalyzer with empty posts."""
    analyzer = NetworkAnalyzer(owner_username=user_owner)
    result = analyzer.analyze([])

    # Check that only the owner node exists
    assert len(result["nodes"]) == 1
    assert result["nodes"][0]["id"] == user_owner

    # Check that there are no edges
    assert len(result["links"]) == 0


def test_network_analyzer_combined_data(
    user_owner,
    follower_users,
    following_users,
    post_with_mentions,
    post_with_comment_mentions,
    post_with_likes,
    empty_post,
):
    """Test NetworkAnalyzer with all data types combined."""
    analyzer = NetworkAnalyzer(
        owner_username=user_owner, followers=follower_users, following=following_users
    )
    result = analyzer.analyze(
        [post_with_mentions, post_with_comment_mentions, post_with_likes, empty_post]
    )

    # Check for presence of all nodes
    node_ids = [node["id"] for node in result["nodes"]]

    # Owner
    assert user_owner in node_ids

    # Followers and following
    for follower in follower_users:
        assert follower in node_ids
    for following in following_users:
        assert following in node_ids

    # Post mentions
    assert "mentioned1" in node_ids
    assert "mentioned2" in node_ids

    # Comment authors and mentions
    assert "commenter1" in node_ids
    assert "commenter2" in node_ids
    assert "mentioned3" in node_ids
    assert "mentioned4" in node_ids
    assert "mentioned5" in node_ids

    # Likes
    assert "liker1" in node_ids
    assert "liker2" in node_ids

    # Check that all expected edges exist
    edges = [(link["source"], link["target"]) for link in result["links"]]

    # Follower -> Owner edges
    for follower in follower_users:
        assert (follower, user_owner) in edges

    # Owner -> Following edges
    for follow in following_users:
        assert (user_owner, follow) in edges

    # Owner -> Mentioned edges (from post captions)
    assert (user_owner, "mentioned1") in edges
    assert (user_owner, "mentioned2") in edges

    # Commenter -> Owner edges
    assert ("commenter1", user_owner) in edges
    assert ("commenter2", user_owner) in edges

    # Commenter -> Mentioned edges (from comments)
    assert ("commenter1", "mentioned3") in edges
    assert ("commenter2", "mentioned4") in edges
    assert ("commenter2", "mentioned5") in edges

    # Liker -> Owner edges
    assert ("liker1", user_owner) in edges
    assert ("liker2", user_owner) in edges
