# Lean In Circle Recommendation API

A member-focused, explainable recommendation service that helps Lean In members discover relevant, active, and available Circles.

## Overview

This project implements a REST API using Python and FastAPI. It uses the provided synthetic datasets to recommend Circles based on member interests, community activity, availability, and recommendation diversity.

The system uses transparent, deterministic ranking rules rather than a machine-learning model, making the results reproducible and easy to explain.

## Features

- Personalized recommendations using member interests and Circle tags
- Cold-start recommendations for members without selected interests
- Filtering of already-joined, full, unlisted, and inactive Circles
- Activity-aware scoring
- Topic diversification to reduce repetitive recommendations
- Short, data-grounded explanations
- Interactive Swagger API documentation
- Automated unit and API tests

## Technology Stack

- Python 3.14
- FastAPI and Uvicorn
- pytest and HTTPX
- JSON seed datasets
- SQLite schema design (proposed persistence layer)

## Getting Started

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Run the API

```powershell
python -m uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

### Health Check

`GET /health`

Returns:

```json
{
  "status": "ok"
}
```

### Circle Recommendations

`GET /users/{user_id}/recommendations?limit=5`

Example:

`GET /users/23/recommendations?limit=5`

Sample response (abbreviated):

```json
{
  "user_id": 23,
  "count": 5,
  "recommendations": [
    {
      "circle_id": 22,
      "name": "Level Up Collective",
      "topic": "getting-promoted",
      "score": 83,
      "join_policy": "request",
      "reason": "Matches your interest in getting promoted and has recent community activity."
    }
  ]
}
```

The actual response includes up to the requested number of recommendations.

The `limit` parameter supports values from 1 to 20. Unknown users return HTTP 404, while invalid limits return HTTP 422.

## Recommendation Strategy

The recommendation process follows four stages:

1. **Eligibility:** Exclude Circles that are already joined, unlisted, full, or inactive.
2. **Scoring:** Rank eligible Circles using topic relevance, matching tags, and community activity.

3. **Diversification and near-duplicate handling:** Limit recommendations to two Circles per primary topic and suppress Circles with the same topic and normalized description. Higher-scoring Circles are retained first.

4. **Explanations:** Provide short reasons grounded in member interests and Circle data.

The synthetic dataset is evaluated against a fixed reference date of September 21, 2026, to make activity-based results reproducible.

## Key Assignment Scenarios

| User ID | Scenario | Expected behavior |
|---|---|---|
| 7 | Topic matching | Recommend leadership and public-speaking Circles |
| 15 | Similar Circles | Avoid excessive negotiation recommendations |
| 23 | Full and inactive Circles | Prefer eligible alternatives |
| 42 | Cold start | Return useful recommendations without selected interests |


## Testing

Run automated tests:

```powershell
python -m pytest -v
```

Check code quality:

```powershell
python -m ruff check .
```

The project currently contains nine passing automated tests covering recommendation logic and API behavior.


## Database Design

The proposed SQLite schema is available in `docs/schema.sql`.

It contains seven tables and four explicitly defined indexes. The schema has been validated against an in-memory SQLite database.

The current API reads the provided JSON datasets; SQLite persistence is not yet implemented.

## Technical Design

See [Technical Design](docs/technical-design.md) for architectural decisions, ranking rationale, indexing, trade-offs, and future improvements.

## Current Limitations

- Scoring weights are heuristic, not trained on member behavior.

- Near-duplicate detection uses matching topics and normalized descriptions; it does not detect all semantically similar Circles.

- Geographic compatibility is not yet incorporated.
- The API reads JSON files on each request.
- Authentication and production database integration are outside the current prototype.

## Data

All supplied seed data is synthetic and used for this assignment.