WITH questaula AS (
    SELECT r.rowid,r.ano,a.due_date FROM responses r JOIN aulas a ON a.num_aula = r.aula
)
SELECT rowid FROM questaula
WHERE rowid IN (SELECT rowid FROM questaula WHERE ano = ? AND due_date < DATE('now') ORDER BY RANDOM() LIMIT ? OFFSET ?)
UNION
SELECT rowid FROM questaula
WHERE rowid IN (SELECT rowid FROM questaula WHERE ano < ? ORDER BY RANDOM() LIMIT ?);
