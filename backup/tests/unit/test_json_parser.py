import datetime

from instagram_analyzer.parsers.json_parser import JSONParser


def test_parse_single_post_counts_with_empty_arrays():
    parser = JSONParser()
    data = {
        "media": [{"uri": "img.jpg", "creation_timestamp": 1609459200}],
        "creation_timestamp": 1609459200,
        "likes": [],
        "comments": [],
        "like_count": 5,
        "comment_count": 3,
    }

    post = parser._parse_single_post(data)

    assert post is not None
    assert post.likes_count == 5
    assert post.comments_count == 3
