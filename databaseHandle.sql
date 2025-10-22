---- SQL commands for managing the users table ----

--- This commands update information in the users table ---

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


---- SQL commands for managing user_files table ----

-- Create the user_files table
CREATE TABLE IF NOT EXISTS user_files (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_location VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Retrieve all files for a specific user email
SELECT file_name, file_location, upload_date FROM user_files WHERE user_email = 'email001@mail.com';

-- Add a new file for a specific user email
INSERT INTO user_files (user_email, file_name, file_location) VALUES ('email001@mail.com', 'example.txt', '/path/to/example.txt');


---- SQL commands for managing user_known_ips table ----

-- Create the user_known_ips table
CREATE TABLE IF NOT EXISTS user_known_ips (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    UNIQUE (user_email, ip_address)
);

-- Retrieve all known IPs for a specific user email
SELECT ip_address FROM user_known_ips WHERE user_email = 'email001@mail.com';

-- Add a new known IP for a specific user email (only if not already present)
INSERT INTO user_known_ips (user_email, ip_address)
SELECT 'email001@mail.com', '1.1.1.1'::inet
WHERE NOT EXISTS (
    SELECT 1 FROM user_known_ips WHERE user_email = 'email001@mail.com' AND ip_address = '1.1.1.1'::inet
);


---- SQL commands for managing user_blocked_ips table ----

-- Create the user_blocked_ips table
CREATE TABLE IF NOT EXISTS user_blocked_ips (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL REFERENCES users(email) ON DELETE CASCADE,
    ip_address INET NOT NULL,
    reason TEXT,
    UNIQUE (user_email, ip_address)
);

-- Retrieve all blocked IPs and their reasons for a specific user email
SELECT ip_address, reason FROM user_blocked_ips WHERE user_email = 'email001@mail.com';

-- Add a new blocked IP with a reason for a specific user email
INSERT INTO user_blocked_ips (user_email, ip_address, reason) VALUES ('email001@mail.1.1.1.1'::inet, 'Suspicious activity');


---- SQL commands for managing user_preferences table ----

-- Create the user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL UNIQUE REFERENCES users(email) ON DELETE CASCADE,
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Retrieve preferences for a specific user email
SELECT preferences FROM user_preferences WHERE user_email = 'email001@mail.com';

-- Update preferences for a specific user email
UPDATE user_preferences SET preferences = jsonb_set(preferences, '{theme}', '"dark"') WHERE user_email = 'email001@mail.com';

-- Insert initial preferences for a user (if not already present)
INSERT INTO user_preferences (user_email, preferences)
VALUES ('email001@mail.com', '{"theme": "light", "notifications": true}'::jsonb)
ON CONFLICT (user_email) DO NOTHING;

------------------------------------------------------------------------------
