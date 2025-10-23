DELETE from users;
DELETE from personal;
DELETE from connection;
DELETE from iplist;
DELETE from classes;
DELETE from documents;

DELETE FROM sqlite_sequence WHERE name ='users';
DELETE FROM sqlite_sequence WHERE name ='personal';
DELETE FROM sqlite_sequence WHERE name ='connections';
DELETE FROM sqlite_sequence WHERE name ='iplist';
DELETE FROM sqlite_sequence WHERE name ='classes';
DELETE FROM sqlite_sequence WHERE name ='documents';
