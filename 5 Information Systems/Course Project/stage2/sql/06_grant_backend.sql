\set ON_ERROR_STOP on
-- Role must already exist; this file never creates a cluster-wide login.
-- Its credentials belong only to the trusted server, not to end users.
\if :{?backend_role}
\else
  \echo 'Pass -v backend_role=your_existing_server_role'
  \quit 1
\endif
GRANT USAGE ON SCHEMA beauty TO :"backend_role";
SELECT format('GRANT EXECUTE ON %s %s TO %I',CASE WHEN p.prokind='p' THEN 'PROCEDURE' ELSE 'FUNCTION' END,p.oid::regprocedure,:'backend_role')
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='beauty' AND p.proname IN
 ('register_user','authenticate','available_slots','book_appointment','cancel_appointment','mark_visit','add_review','moderate',
 'invite_master','reissue_invitation','accept_invitation','set_master_service','save_work_interval','delete_work_interval',
 'save_service','save_master_profile','create_salon','resubmit_salon','put_photo','archive_photo','search_salons','appointment_journal')
\gexec
