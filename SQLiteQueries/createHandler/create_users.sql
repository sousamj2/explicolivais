CREATE TABLE IF NOT EXISTS users (
user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
first_name TEXT NOT NULL,
last_name  TEXT NOT NULL,
email      TEXT NOT NULL,
username   TEXT NOT NULL,
h_password TEXT,
g_token    INTEGER DEFAULT 1
);
