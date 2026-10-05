-- Add persistent accounts to an existing installation; preserve all movie data.
CREATE TABLE IF NOT EXISTS app_user (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0),
 username varchar(64) NOT NULL UNIQUE CHECK(length(username) BETWEEN 3 AND 64),
 password_hash varchar(64) NOT NULL, salt varchar(32) NOT NULL,
 iterations integer NOT NULL CHECK(iterations>=600000));
