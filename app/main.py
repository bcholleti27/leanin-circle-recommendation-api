
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from app.data_loader import load_all_data
from app.recommendations import recommend_circles

app = FastAPI(
    title="Lean In Circle Recommendation API",
    description="Explainable recommendations for Lean In Circles",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/users/{user_id}/recommendations")
def get_recommendations(
    user_id: int,
    limit: int = Query(default=5, ge=1, le=20),
):
    """Return ranked Circle recommendations for a user."""
    data = load_all_data()

    # Fixed snapshot date for reproducible seed-data results.
    reference_date = datetime(
        2026, 9, 21, tzinfo=UTC
    )

    try:
        recommendations = recommend_circles(
            user_id=user_id,
            data=data,
            limit=limit,
            as_of=reference_date,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return {
        "user_id": user_id,
        "count": len(recommendations),
        "recommendations": recommendations,
    }


@app.get("/", include_in_schema=False)
def home():
    """Serve the Circle Discovery dashboard."""
    website = (
        Path(__file__).resolve().parent.parent
        / "static"
        / "index.html"
    )
    return FileResponse(website)


@app.get("/circles/{circle_id}")
def get_circle_details(circle_id: int):
    """Return read-only details for a Circle."""
    data = load_all_data()

    circle = next(
        (item for item in data["circles"] if item["id"] == circle_id),
        None,
    )

    if circle is None:
        raise HTTPException(
            status_code=404,
            detail="Circle not found",
        )

    return {
        "id": circle["id"],
        "name": circle["name"],
        "description": circle["description"],
        "topic": circle["topic"],
        "tags": circle["tags"],
        "format": circle["format"],
        "join_policy": circle["join_policy"],
        "member_count": circle["member_count"],
        "max_members": circle["max_members"],
        "feed_posts_30d": circle["feed_posts_30d"],
        "chat_messages_30d": circle["chat_messages_30d"],
        "last_activity_at": circle["last_activity_at"],
    }


@app.get("/users/{user_id}/profile")
def get_member_profile(user_id: int):
    """Return member information used for Circle discovery."""
    data = load_all_data()

    user = next(
        (item for item in data["users"] if item["id"] == user_id),
        None,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    memberships = [
        membership
        for membership in data["memberships"]
        if membership["user_id"] == user_id
    ]

    return {
        "id": user["id"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "job_title": user.get("job_title"),
        "industry": user.get("industry"),
        "location": user.get("location"),
        "topic_interests": user.get("topic_interests", []),
        "joined_circle_count": len(memberships),
        "profile_completeness": user.get("profile_completeness"),
    }
