UPDATE connection SET
lastlogints = thislogints,
lastloginip = thisloginip,
thislogints = ?,
thisloginip = ?
WHERE user_id = ?;