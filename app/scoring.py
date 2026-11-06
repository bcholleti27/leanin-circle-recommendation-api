
def score_circle(user: dict, circle: dict) -> float:
    """Score a Circle using interests and activity signals."""
    score = 0.0

    interests = set(user.get("topic_interests") or [])
    circle_topic = circle.get("topic")
    circle_tags = set(circle.get("tags") or [])

    # Strong preference for matching the primary topic.
    if circle_topic in interests:
        score += 60

    # Reward matching secondary tags, with a fixed cap.
    matching_tags = interests & circle_tags
    score += min(len(matching_tags) * 10, 20)

    # Activity signals are capped so volume cannot dominate.
    posts = max(0, circle.get("feed_posts_30d") or 0)
    messages = max(0, circle.get("chat_messages_30d") or 0)

    score += min(posts, 15)
    score += min(messages / 20, 5)

    return round(score, 2)


def explain_circle(user: dict, circle: dict) -> str:
    """Generate a short explanation from real Circle signals."""
    interests = set(user.get("topic_interests") or [])
    topic = circle.get("topic")
    tags = set(circle.get("tags") or [])

    if topic and topic in interests:
        readable_topic = topic.replace("-", " ")
        return (
            f"Matches your interest in {readable_topic} "
            "and has recent community activity."
        )

    matching_tags = interests & tags
    if matching_tags:
        readable_tag = min(matching_tags).replace("-", " ")
        return (
            f"Connects with your interest in {readable_tag} "
            "and has recent community activity."
        )

    posts = circle.get("feed_posts_30d") or 0
    messages = circle.get("chat_messages_30d") or 0

    if posts > 0 or messages > 0:
        return (
            "An active community with recent discussions "
            "that you may enjoy exploring."
        )

    return "A community you may want to explore."
