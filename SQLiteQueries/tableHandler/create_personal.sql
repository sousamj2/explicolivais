CREATE TABLE IF NOT EXISTS personal (
personal_id  INTEGER PRIMARY KEY,
user_id   INTEGER,
morada    TEXT NOT NULL DEFAULT 'Unknown',
numero    TEXT NOT NULL DEFAULT 'NA',
andar     TEXT NOT NULL DEFAULT 'NA',
porta     TEXT NOT NULL DEFAULT 'NA',
observacoes TEXT,
cpostal1  INTEGER        CHECK (cpostal1  > 0 AND cpostal1 <= 9999),
cpostal2  INTEGER        CHECK (cpostal2  > 0 AND cpostal2 <= 999),
telemovel INTEGER UNIQUE CHECK (telemovel > 910000000 AND telemovel <= 999999999),
nfiscal   INTEGER UNIQUE CHECK (nfiscal   > 100000000 AND nfiscal <= 999999999)
);
