SELECT u.email, c.createdatts
FROM users u
JOIN connection c
ON c.user_id = u.user_id
WHERE c.createdatip = (?)