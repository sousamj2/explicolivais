SELECT u.email
FROM users u
JOIN personal p
ON p.user_id = u.user_id
WHERE cell_phone = (?)