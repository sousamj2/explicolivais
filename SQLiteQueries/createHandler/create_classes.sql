CREATE TABLE IF NOT EXISTS classes (
classes_id   INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
year INTEGER NOT NULL,
child_name TEXT NOT NULL,
first_class TEXT DEFAULT NULL,
first_contact TEXT DEFAULT NULL,
course TEXT NOT NULL DEFAULT 'Matematica',
FOREIGN KEY (user_id) REFERENCES users(user_id)
)