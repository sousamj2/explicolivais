SELECT 
u.first_name, u.last_name, u.email,
p.address, p.number, p.floor, p.door, p.zip_code1, p.zip_code2, p.cell_phone, p.nfiscal, p.notes,
co.lastloginip, co.lastlogints, co.vpn_check
-- cl.course, cl.child_name, cl.year, cl.first_contact, cl.first_class,
-- d.created_at, d.docname, d.docu_id, d.docurl
from users u
JOIN personal p
on u.user_id = p.user_id
join connection co
on u.user_id = co.user_id
-- join classes cl
-- on u.user_id = cl.user_id
-- JOIN documents d
-- ON d.user_id = u.user_id
WHERE u.email = ?
