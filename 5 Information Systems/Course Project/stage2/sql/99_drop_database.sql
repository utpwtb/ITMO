\set ON_ERROR_STOP on
\if :{?db_name}
\else
  \set db_name beauty_course
\endif
-- Run against postgres; no FORCE and no termination of other sessions.
DROP DATABASE IF EXISTS :"db_name";
