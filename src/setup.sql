-- Only run these lines if you have NOT already created the user and database
CREATE DATABASE yourdb;
CREATE USER youruser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE yourdb TO youruser;
