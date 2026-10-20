\set ON_ERROR_STOP on
\if :{?db_name}
\else
  \set db_name beauty_course
\endif
-- Run against postgres. Deliberately fails if the database already exists.
CREATE DATABASE :"db_name" WITH TEMPLATE template0 ENCODING 'UTF8';
