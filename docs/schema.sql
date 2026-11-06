
-- Lean In Circle Recommendation API
-- Proposed SQLite database schema.
-- The current API reads JSON seed data.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    bio TEXT,
    job_title TEXT,
    industry TEXT,
    location TEXT,
    profile_completeness REAL
);

CREATE TABLE IF NOT EXISTS topics (
    slug TEXT PRIMARY KEY,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_interests (
    user_id INTEGER NOT NULL,
    topic_slug TEXT NOT NULL,
    PRIMARY KEY (user_id, topic_slug),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (topic_slug) REFERENCES topics(slug)
);

CREATE TABLE IF NOT EXISTS circles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    topic TEXT,
    format TEXT NOT NULL,
    access TEXT NOT NULL,
    join_policy TEXT NOT NULL,
    max_members INTEGER,
    member_count INTEGER NOT NULL DEFAULT 0,
    last_activity_at TEXT,
    feed_posts_30d INTEGER NOT NULL DEFAULT 0,
    chat_messages_30d INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (topic) REFERENCES topics(slug)
);

CREATE TABLE IF NOT EXISTS circle_tags (
    circle_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (circle_id, tag),
    FOREIGN KEY (circle_id) REFERENCES circles(id)
);

CREATE TABLE IF NOT EXISTS memberships (
    user_id INTEGER NOT NULL,
    circle_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    joined_at TEXT NOT NULL,
    PRIMARY KEY (user_id, circle_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (circle_id) REFERENCES circles(id)
);

CREATE TABLE IF NOT EXISTS activity (
    id INTEGER PRIMARY KEY,
    circle_id INTEGER NOT NULL,
    author_user_id INTEGER NOT NULL,
    body TEXT,
    reaction_count INTEGER NOT NULL DEFAULT 0,
    comment_count INTEGER NOT NULL DEFAULT 0,
    save_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (circle_id) REFERENCES circles(id),
    FOREIGN KEY (author_user_id) REFERENCES users(id)
);

-- Indexes supporting recommendation queries.

CREATE INDEX IF NOT EXISTS idx_circles_discovery
ON circles(access, topic);

CREATE INDEX IF NOT EXISTS idx_circles_last_activity
ON circles(last_activity_at);

CREATE INDEX IF NOT EXISTS idx_memberships_circle
ON memberships(circle_id);

CREATE INDEX IF NOT EXISTS idx_activity_circle_created
ON activity(circle_id, created_at);
