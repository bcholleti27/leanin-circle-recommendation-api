# Technical Design — Lean In Circle Recommendation API

## 1. Overview

The recommendation service helps Lean In members discover relevant Circles using their selected interests and Circle activity. It supports members with limited profile information and avoids recommending Circles that are unavailable, inactive, or already joined.

The implementation uses Python, FastAPI, and deterministic, explainable ranking rules. The current prototype reads the provided synthetic JSON datasets. A proposed SQLite schema is included in `docs/schema.sql`.

## 2. Recommendation Pipeline

**Candidate filtering:** Exclude Circles that are already joined, unlisted, full, or inactive for more than 90 days. Circles requiring approval remain eligible because members can request to join.

**Relevance scoring:** Award 60 points for a matching primary topic and up to 20 points for matching tags. Add up to 15 points for recent posts and 5 points for chat activity. Activity scores are capped to prevent high-volume Circles from overwhelming relevance.


**Diversification and near-duplicate handling:** Sort candidates by score, breaking ties by Circle ID for deterministic results. Limit the final results to two Circles per primary topic. Additionally, suppress Circles with the same primary topic and normalized description, retaining the higher-ranked Circle. This prevents repetitive recommendations while preserving a simple, explainable approach.


**Explanations:** Generate short, data-grounded reasons using matching interests or community activity. Avoid claiming personalized relevance for members without selected interests.

## 3. Cold-Start Handling

Members without interests or memberships receive recommendations based on Circle activity. This allows new members to discover communities without completing their profiles first.

The current implementation does not personalize recommendations using location. Geographic suitability is an area for improvement, particularly for in-person Circles.

## 4. Data Model and Indexing

The proposed SQLite schema contains `users`, `topics`, `user_interests`, `circles`, `circle_tags`, `memberships`, and `activity`.

Indexes support public Circle discovery, recent-activity filtering, membership lookups, and activity retrieval by Circle and date. Composite primary keys prevent duplicate user-interest and membership relationships.

The SQL schema has been validated against an in-memory SQLite database. The running API currently uses JSON files rather than SQLite persistence.

## 5. API and Testing

**Endpoint:** `GET /users/{user_id}/recommendations?limit=5`

The response includes Circle ID, name, topic, score, join policy, and a short explanation. Invalid limits return HTTP 422; unknown users return HTTP 404.

Nine automated pytest tests cover filtering, cold-start behavior, topic diversity, joined-Circle exclusion, invalid users, and HTTP endpoint responses.

## 6. Trade-offs and Future Improvements

The scoring weights and two-per-topic diversity limit are initial heuristics, not learned or experimentally validated parameters. A topic cap reduces repetition but can introduce lower-relevance recommendations.

The prototype loads JSON on each request, which is acceptable for a small synthetic dataset but not ideal for production. A production version would use indexed database queries, caching where appropriate, and incremental activity updates.

Further improvements include geographic compatibility, semantic near-duplicate detection, richer engagement signals, pagination, authentication, structured response models, and evaluation using engagement or join outcomes.

**Key design principle:** Prioritize relevant, available, diverse, and explainable recommendations over unnecessary algorithmic complexity.