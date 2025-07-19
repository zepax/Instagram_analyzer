from collections import defaultdict
from typing import Any, Optional

from ..models import Post


class NetworkAnalyzer:
    """Build a simple interaction graph from posts, followers, and following."""

    def __init__(
        self,
        owner_username: str,
        followers: Optional[list[str]] = None,
        following: Optional[list[str]] = None,
    ) -> None:
        self.owner = owner_username
        self.followers = followers if followers is not None else []
        self.following = following if following is not None else []

    def analyze(self, posts: list[Post]) -> dict[str, Any]:
        """
        Generate graph data from mentions, likes, comments, followers, and following.
        """
        nodes = set()
        edges: defaultdict[tuple[str, str], int] = defaultdict(int)

        nodes.add(self.owner)

        # Add followers and following as nodes and edges
        for follower in self.followers:
            nodes.add(follower)
            edges[(follower, self.owner)] += 1  # Follower -> owner

        for followee in self.following:
            nodes.add(followee)
            edges[(self.owner, followee)] += 1  # Owner -> following

        for post in posts:
            # Mentions in post caption
            for mention in post.mentions:
                nodes.add(mention)
                edges[(self.owner, mention)] += 1

            # Likes
            for like in post.likes:
                username = like.user.username
                nodes.add(username)
                edges[(username, self.owner)] += 1

            # Comments and mentions in comments
            for comment in post.comments:
                author = comment.author.username
                nodes.add(author)
                edges[(author, self.owner)] += 1
                for mention in comment.mentions:
                    nodes.add(mention)
                    edges[(author, mention)] += 1

        return {
            "nodes": [{"id": n} for n in nodes],
            "links": [
                {"source": s, "target": t, "value": w} for (s, t), w in edges.items()
            ],
        }
