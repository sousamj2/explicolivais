SELECT 
u.first_name, u.last_name, u.email,u.tier,
co.lastloginip, co.lastlogints, co.vpn_check
from users u
join connection co
on u.user_id = co.user_id
WHERE u.email = ?
