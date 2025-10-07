---- SQL commands for managing the users table ----

--- This commands update information in the users table ---

-- Retrieve the documents->files for user with specific email
SELECT documents->'files' FROM users WHERE email = 'email001@mail.com';

-- To a user with specific email, ad in the documents->'files' array a dictionary element with file name, file location and upload date
UPDATE users 
SET documents = jsonb_set(documents, '{files}', (documents->'files')::jsonb || to_jsonb('{"file_name": "example.txt", "file_location": "/path/to/example.txt", "upload_date": "' || NOW() || '"}'::jsonb))
WHERE email = 'email001@mail.com';

-- Check if the ip_last_login is already in the documents->'know_ip' array for user with specific email
SELECT '1.1.1.1'::inet = ANY (SELECT jsonb_array_elements_text(documents->'know_ip')::inet FROM users WHERE email = 'email001@mail.com');

-- Check if the ip_last_login is already in the documents->'know_ip' array for user with specific email and only add it if it is not already present
DO $$
DECLARE
    ip_address inet := '1.1.1.1';
    email_address varchar := 'email001@mail.com';
    ip_exists boolean;
BEGIN
    SELECT ip_address = ANY (SELECT jsonb_array_elements_text(documents->'know_ip')::inet FROM users WHERE email = email_address) INTO ip_exists;
    IF NOT ip_exists THEN
        UPDATE users 
        SET documents = jsonb_set(documents, '{know_ip}', (documents->'know_ip')::jsonb || to_jsonb(ip_address))
        WHERE email = email_address;
    END IF;
END $$;

-- Check if an ip address is in the documents->'block_ip' object for user with specific email
SELECT '1.1.1.1'::inet = ANY (SELECT jsonb_object_keys(documents->'block_ip')::inet FROM users WHERE email = 'email001@mail.com');

-- Add an ip address to the documents->'block_ip' object with a reason for user with specific email
UPDATE users 
SET documents = jsonb_set(documents, '{block_ip,1.1.1.1}', to_jsonb('Suspicious activity'))
WHERE email = 'email001@mail.com';

-- Extract email and created_at if ip address matches ip_created
SELECT email, created_at
FROM users
WHERE '1.1.1.1'::inet = ip_created;


-- Updates last login time to current time for user with specific email
UPDATE users SET last_login = NOW() WHERE email = 'email001@mail.com';

-- Update morada for user with specific email
UPDATE users SET morada = 'New Address 123' WHERE email = 'email001@mail.com';

-- Update codigo_postal for user with specific email
UPDATE users SET codigo_postal = '1234-567' WHERE email = 'email001@mail.com';

-- Update telemovel for user with specific email
UPDATE users SET telemovel = 912345678 WHERE email = 'email001@mail.com';

-- Update nif for user with specific email
UPDATE users SET nif = 123456789 WHERE email = 'email001@mail.com';




--- This commands retrieve information from the users table ---

-- Retrieve nif for user with specific email or zero if nif is larger than 123456789
SELECT COALESCE(NULLIF(nif, 123456789), 0) AS nif
FROM users
WHERE email = 'email001@mail.com'; 

-- Retrieves last login time and ip address for user with specific email
SELECT last_login, ip_created FROM users WHERE email = 'email001@mail.com';

-- Retrieves all records from the users table
SELECT * FROM users;

-- Retrieves specific fields for a user with id 1
SELECT id, nome, email FROM users WHERE id = 1;

-- Counts the total number of users
SELECT COUNT(*) FROM users;

-- Retrives specific fields for a user with a specific email
SELECT id, nome, email FROM users WHERE email = 'email001@mail.com'

-- Retrives all fields for a user with a specific email
SELECT * FROM users WHERE email = 'email001@mail.com';

-- Retrives all column names from the users table
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'users';

--- This Creates the users table with all necessary fields ---

--  Nome
ALTER TABLE users
ADD COLUMN nome SET NOT NULL DEFAULT 'Unknown';

--  Email
ALTER TABLE users
ADD COLUMN email varchar(255) NOT NULL UNIQUE ;

--  Morada
ALTER TABLE users
ADD COLUMN morada SET NOT NULL DEFAULT 'Unknown';

--  Código Postal
ALTER TABLE users
ADD COLUMN codigo_postal varchar(10) NOT NULL DEFAULT '0000-000';

-- Telemóvel
ALTER TABLE users
ADD COLUMN telemovel bigint NOT NULL UNIQUE DEFAULT (floor(random() * 900000000 + 100000000)::bigint);

--  NIF
ALTER TABLE users
ADD COLUMN nif bigint NOT NULL UNIQUE DEFAULT (floor(random() * 9000000000 + 1000000000)::bigint);

-- IP Address at creation: for development purposes, we generate a random IP address and allow not unique values
ALTER TABLE users
ADD COLUMN ip_created inet NOT NULL 
-- UNIQUE
 DEFAULT (
  (
    trunc(random() * 256)::int || '.' ||
    trunc(random() * 256)::int || '.' ||
    trunc(random() * 256)::int || '.' ||
    trunc(random() * 256)::int
  )::inet
);
-- Timestamp
ALTER TABLE users ADD COLUMN this_login SET DEFAULT NOW();
ALTER TABLE users ADD COLUMN last_login SET DEFAULT NOW();
ALTER TABLE users ADD COLUMN created_at SET DEFAULT NOW();

-- IP address at the last login. At the moment, we copy the creation IP address
ALTER TABLE users
ADD COLUMN ip_last_login inet NOT NULL 
-- UNIQUE
 DEFAULT ip_created;

-- Documents as a dictionary to store additional information with the keys "files", "know_ip" and "preferences". The "files" key stores an array of text values, the "know_ip" key stores an array of inet values, and the "preferences" key stores a JSONB object.
-- The default value is an empty dictionary with empty arrays for "files" and "know_ip", and an empty JSONB object for "preferences".
ALTER TABLE users
ADD COLUMN documents JSONB NOT NULL DEFAULT '{"files": [], "know_ip": [], "block_ip": {}, "preferences": {}}'::jsonb;

-- Add iterator to how many times the user logged in. Default is 1 at creation
ALTER TABLE users
ADD COLUMN login_count integer NOT NULL DEFAULT 1;

-- Add 4 boolean fields: vpn_check, vpn_valid, first_contact_completed, first_lesson_completed
ALTER TABLE users
ADD COLUMN vpn_check boolean NOT NULL DEFAULT false;  -- Indicates if VPN check has been performed
ALTER TABLE users
ADD COLUMN vpn_valid boolean NOT NULL DEFAULT false;  -- Indicates if the VPN is valid
ALTER TABLE users
ADD COLUMN first_contact_completed boolean NOT NULL DEFAULT false;  -- Indicates if the first contact has been completed
ALTER TABLE users
ADD COLUMN first_lesson_completed boolean NOT NULL DEFAULT false;  -- Indicates if the first lesson has been completed


-- Increment login_count by 1 for user with specific email
UPDATE users SET login_count = login_count + 1 WHERE email = 'email001@mail.com';


--- This creates the users empty table to add fields later ---
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY
);


--- This resets the users table but keeps its structure ---
TRUNCATE TABLE users RESTART IDENTITY;

--- This resets the users table but keeps the structure and the id counter ---
DELETE FROM users;


--- This drops the users table if it exists ---
DROP TABLE IF EXISTS users;
