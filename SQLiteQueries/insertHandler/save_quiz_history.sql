INSERT INTO qresults (
    q_uuid,
    user_id,
    q_score,
    q_year,
    q_percent,
    n_correct,
    n_wrong,
    n_skip,
    q_resp
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);