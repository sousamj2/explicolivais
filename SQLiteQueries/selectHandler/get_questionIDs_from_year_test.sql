WITH questaula AS (
    SELECT r.rowid,r.ano,a.due_date FROM responses r JOIN aulas a ON a.num_aula = r.aula
)
SELECT rowid,due_date FROM questaula
WHERE rowid IN (SELECT rowid FROM questaula WHERE ano = 7 AND due_date < DATE('now') ORDER BY RANDOM() LIMIT 10 OFFSET 0)
UNION
SELECT rowid,due_date FROM questaula
WHERE rowid IN (SELECT rowid FROM questaula WHERE ano < 7 ORDER BY RANDOM() LIMIT 10);
