SELECT
    qr.q_uuid,
    qr.q_resp as answers,
    qr.q_score,
    qr.q_year,
    qr.n_correct,
    qr.n_wrong,
    qr.n_skip,
    qr.start_ts as quiz_date,
    (qr.n_correct + qr.n_wrong + qr.n_skip) as total_questions,
    -- Calculate percentage, preventing division by zero.
    -- Assumes max score is total_questions * 5. This is a simplification.
    CASE
        WHEN (qr.n_correct + qr.n_wrong + qr.n_skip) > 0 THEN (qr.q_score / ((qr.n_correct + qr.n_wrong + qr.n_skip) * 5.0)) * 100
        ELSE 0
    END as score_perc
FROM qresults qr
JOIN users u ON qr.user_id = u.user_id
WHERE u.email = ?
ORDER BY qr.start_ts DESC;