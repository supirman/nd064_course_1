DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS count;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE count (
    key TEXT PRIMARY KEY NOT NULL,
    value INTEGER
);