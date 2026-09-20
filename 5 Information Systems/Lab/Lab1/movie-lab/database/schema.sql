-- PostgreSQL 17. Run once in a dedicated database/schema; no destructive reset.
CREATE TABLE coordinates (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 x integer NOT NULL CHECK(x<=826), y integer NOT NULL);
CREATE TABLE location (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 x bigint NOT NULL, y double precision NOT NULL CHECK(y > '-Infinity'::float8 AND y < 'Infinity'::float8), name text NOT NULL);
CREATE TABLE person (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 name text NOT NULL CHECK(length(name)>0),
 eyecolor varchar(20) CHECK(eyecolor IN ('GREEN','BLACK','ORANGE','WHITE','BROWN')),
 haircolor varchar(20) CHECK(haircolor IN ('GREEN','BLACK','ORANGE','WHITE','BROWN')),
 location_id bigint REFERENCES location(id) ON DELETE CASCADE,
 birthday text NOT NULL CHECK(birthday ~ '^\d{4}-\d{2}-\d{2}T.*(Z|[+-]\d{2}:\d{2})(\[.*\])?$') CHECK(split_part(birthday,'[',1)::timestamptz IS NOT NULL),
 height real CHECK(height>0 AND height<'Infinity'::real), weight real CHECK(weight>0 AND weight<'Infinity'::real),
 passportid text NOT NULL UNIQUE);
CREATE TABLE movie (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0), version bigint NOT NULL DEFAULT 0,
 name text NOT NULL CHECK(length(name)>0), coordinates_id bigint NOT NULL REFERENCES coordinates(id) ON DELETE CASCADE,
 creationdate date NOT NULL DEFAULT CURRENT_DATE, oscarscount integer NOT NULL CHECK(oscarscount>0),
 budget bigint NOT NULL CHECK(budget>0), totalboxoffice double precision CHECK(totalboxoffice>0 AND totalboxoffice<'Infinity'::float8),
 mpaarating varchar(20) NOT NULL CHECK(mpaarating IN ('G','PG','PG_13','R','NC_17')),
 director_id bigint REFERENCES person(id) ON DELETE CASCADE,
 screenwriter_id bigint REFERENCES person(id) ON DELETE CASCADE,
 operator_id bigint REFERENCES person(id) ON DELETE CASCADE,
 length integer NOT NULL CHECK(length>0), goldenpalmcount bigint CHECK(goldenpalmcount>0),
 usaboxoffice integer NOT NULL CHECK(usaboxoffice>0), tagline text NOT NULL,
 genre varchar(20) CHECK(genre IN ('WESTERN','COMEDY','TRAGEDY','HORROR')));
CREATE INDEX movie_name_idx ON movie(name);
CREATE INDEX movie_genre_idx ON movie(genre);
CREATE INDEX movie_coordinates_idx ON movie(coordinates_id);
CREATE INDEX movie_director_idx ON movie(director_id);
CREATE INDEX movie_screenwriter_idx ON movie(screenwriter_id);
CREATE INDEX movie_operator_idx ON movie(operator_id);
CREATE INDEX person_location_idx ON person(location_id);
CREATE TABLE app_state (id bigint PRIMARY KEY CHECK(id=1), revision bigint NOT NULL DEFAULT 0);
INSERT INTO app_state(id,revision) VALUES(1,0);
