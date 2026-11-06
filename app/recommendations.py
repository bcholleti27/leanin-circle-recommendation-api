
from datetime import UTC, datetime, timedelta

from app.data_loader import load_all_data
from app.scoring import explain_circle, score_circle

INACTIVE_DAYS = 90


def parse_datetime(value: str) -> datetime:
    """Convert an ISO timestamp into a timezone-aware datetime."""
    return datetime.fromisoformat(value)
    


def get_eligible_circles(
    user_id: int,
    data: dict,
    as_of: datetime | None = None,
) -> list[dict]:
    """Return Circles that are eligible for recommendation."""
    if as_of is None:
        as_of = datetime.now(UTC)

    users = {user["id"] for user in data["users"]}

    if user_id not in users:
        raise ValueError(f"User {user_id} not found")

    joined_circle_ids = {
        membership["circle_id"]
        for membership in data["memberships"]
        if membership["user_id"] == user_id
    }

    cutoff = as_of - timedelta(days=INACTIVE_DAYS)
    eligible = []

    for circle in data["circles"]:
        # Do not recommend a Circle the member already joined.
        if circle["id"] in joined_circle_ids:
            continue

        # Unlisted Circles should not appear in public discovery.
        if circle["access"] != "public":
            continue

        # Null capacity means there is no membership limit.
        max_members = circle["max_members"]
        if (
            max_members is not None
            and circle["member_count"] >= max_members
        ):
            continue

        # Exclude Circles that have been inactive for too long.
        last_activity = circle.get("last_activity_at")
        if (
            not last_activity
            or parse_datetime(last_activity) < cutoff
        ):
            continue

        eligible.append(circle)

    return eligible

def recommend_circles(
    user_id: int,
    data: dict,
    limit: int = 5,
    as_of: datetime | None = None,
) -> list[dict]:
    """Return the highest-scoring eligible Circles."""
    if not 1 <= limit <= 20:
        raise ValueError("Limit must be between 1 and 20")

    users = {
        user["id"]: user
        for user in data["users"]
    }

    if user_id not in users:
        raise ValueError(f"User {user_id} not found")

    user = users[user_id]

    eligible = get_eligible_circles(
        user_id=user_id,
        data=data,
        as_of=as_of,
    )

    ranked = []

    for circle in eligible:
        
        ranked.append({
            "circle_id": circle["id"],
            "name": circle["name"],
            "topic": circle.get("topic"),
            "score": score_circle(user, circle),
            "join_policy": circle["join_policy"],
            "reason": explain_circle(user, circle),
        })


    
    ranked.sort(
        key=lambda item: (-item["score"], item["circle_id"])
    )

        
    # Diversify results and suppress near-duplicate Circles.
    diversified = []
    topic_counts = {}
    seen_descriptions = set()

    descriptions_by_id = {
        circle["id"]: (circle.get("description") or "").strip().casefold()
        for circle in eligible
    }

    for circle in ranked:
        topic = circle["topic"]

        # Suppress Circles with the same topic and description.
        description = descriptions_by_id.get(circle["circle_id"], "")
        duplicate_key = (topic, description)

        if description and duplicate_key in seen_descriptions:
            continue

        # Prevent one topic from dominating recommendations.
        if topic is not None:
            if topic_counts.get(topic, 0) >= 2:
                continue

            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        diversified.append(circle)

        if description:
            seen_descriptions.add(duplicate_key)

        if len(diversified) == limit:
            break

    return diversified




if __name__ == "__main__":
    data = load_all_data()

    # The synthetic dataset is anchored around September 2026.
    # Using a fixed date makes this example reproducible.
    reference_date = datetime(
        2026, 9, 21, tzinfo=UTC
    )

    for user_id in (42, 7, 15, 23):
        circles = get_eligible_circles(
            user_id,
            data,
            as_of=reference_date,
        )

        print(
            f"User {user_id}: "
            f"{len(circles)} eligible Circles"
        )
