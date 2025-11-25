
SELECT rowid FROM responses
WHERE rowid IN (SELECT rowid FROM responses WHERE ano = ? ORDER BY rowid LIMIT ? OFFSET ?)
UNION
SELECT rowid FROM responses
WHERE rowid IN (SELECT rowid FROM responses WHERE ano < ? ORDER BY rowid LIMIT ?);
