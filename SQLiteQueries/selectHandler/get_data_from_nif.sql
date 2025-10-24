SELECT u.email, c.createdatts
FROM users u
JOIN personal p
ON p.user_id = u.user_id
JOIN connection c
ON c.user_id = u.user_id
WHERE nfiscal = (?)