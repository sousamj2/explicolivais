CREATE TABLE IF NOT EXISTS classes (
classes_id   INTEGER PRIMARY KEY,
user_id INTEGER,
year INTEGER NOT NULL,
childName TEXT NOT NULL,
firstClass TEXT,
firstContact TEXT,
disciplina TEXT NOT NULL DEFAULT 'Matematica'
)