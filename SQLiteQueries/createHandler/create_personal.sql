CREATE TABLE IF NOT EXISTS personal (
personal_id  INTEGER PRIMARY KEY AUTOINCREMENT,
user_id   INTEGER UNIQUE,
address    TEXT NOT NULL DEFAULT 'Unknown',
number    TEXT NOT NULL DEFAULT 'NA',
floor     TEXT NOT NULL DEFAULT 'NA',
door     TEXT NOT NULL DEFAULT 'NA',
notes    TEXT,
zip_code1  INTEGER        ,-- CHECK (zip_code1  > 0 AND zip_code1 <= 9999),
zip_code2  INTEGER        ,-- CHECK (zip_code2  > 0 AND zip_code2 <= 999),
cell_phone INTEGER UNIQUE ,-- CHECK (cell_phone > 910000000 AND cell_phone <= 999999999),
nfiscal    INTEGER UNIQUE ,-- CHECK (nfiscal   > 100000000 AND nfiscal <= 999999999),
FOREIGN KEY (user_id) REFERENCES users(user_id)
);
