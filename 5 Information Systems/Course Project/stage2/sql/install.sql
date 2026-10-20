\set ON_ERROR_STOP on
\if :{?with_demo_data}
\else
  \set with_demo_data false
\endif
BEGIN;
SET LOCAL TIME ZONE 'Europe/Moscow';
\ir 01_tables.sql
\if :with_demo_data
  -- Historical fixtures are imported before business triggers are installed.
  -- Declarative constraints remain enabled; this path is only for a fresh database.
  \ir 02_seed.sql
\endif
\ir 03_integrity.sql
\ir 04_routines.sql
\ir 05_indexes.sql
REVOKE ALL ON ALL TABLES IN SCHEMA beauty FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA beauty FROM PUBLIC;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA beauty FROM PUBLIC;
REVOKE EXECUTE ON ALL PROCEDURES IN SCHEMA beauty FROM PUBLIC;
COMMIT;
ANALYZE;
