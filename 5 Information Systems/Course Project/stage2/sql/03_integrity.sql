-- A single transaction advisory lock serializes business writes in the teaching version.
-- All tables acquire it BEFORE STATEMENT, before row locks. Reads remain concurrent.
CREATE FUNCTION beauty.lock_writes() RETURNS void LANGUAGE plpgsql VOLATILE
SET search_path=pg_catalog,beauty AS $$
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' THEN
  RAISE EXCEPTION 'Business writes require READ COMMITTED' USING ERRCODE='25000';
 END IF;
 PERFORM pg_advisory_xact_lock(407960,409297);
END $$;
CREATE FUNCTION beauty.trg_lock() RETURNS trigger LANGUAGE plpgsql
SET search_path=pg_catalog,beauty AS $$ BEGIN PERFORM beauty.lock_writes(); RETURN NULL; END $$;
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['user_account','district','salon','service_type','salon_service','master',
  'master_service','work_interval','appointment','salon_photo','master_photo','review','moderation_decision','master_invitation']
 LOOP EXECUTE format('CREATE TRIGGER a_lock BEFORE INSERT OR UPDATE OR DELETE ON beauty.%I FOR EACH STATEMENT EXECUTE FUNCTION beauty.trg_lock()',t); END LOOP;
END $$;

CREATE FUNCTION beauty.require_actor(p_id bigint,p_roles text[]) RETURNS beauty.user_account LANGUAGE plpgsql
SET search_path=pg_catalog,beauty AS $$ DECLARE u beauty.user_account; BEGIN
 SELECT * INTO u FROM beauty.user_account WHERE user_id=p_id;
 IF NOT FOUND OR u.account_status<>'ACTIVE' OR NOT(u.role=ANY(p_roles)) THEN
  RAISE EXCEPTION 'Actor has no permission' USING ERRCODE='42501';
 END IF; RETURN u;
END $$;
CREATE FUNCTION beauty.trg_identity() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$
BEGIN
 IF TG_TABLE_NAME='user_account' THEN
  IF NEW.user_id<>OLD.user_id OR NEW.role<>OLD.role THEN RAISE EXCEPTION 'User identity and role are immutable' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='salon' THEN
  IF NEW.salon_id<>OLD.salon_id OR NEW.owner_user_id<>OLD.owner_user_id THEN RAISE EXCEPTION 'Salon identity is immutable' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='master' THEN
  IF NEW.master_id<>OLD.master_id OR NEW.user_id<>OLD.user_id OR NEW.salon_id<>OLD.salon_id THEN RAISE EXCEPTION 'Master identity is immutable' USING ERRCODE='23514'; END IF;
 ELSE
  IF NEW.salon_service_id<>OLD.salon_service_id OR NEW.salon_id<>OLD.salon_id THEN RAISE EXCEPTION 'Service identity is immutable' USING ERRCODE='23514'; END IF;
 END IF;
 RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN FOREACH t IN ARRAY ARRAY['user_account','salon','master','salon_service'] LOOP
 EXECUTE format('CREATE TRIGGER b_identity BEFORE UPDATE ON beauty.%I FOR EACH ROW EXECUTE FUNCTION beauty.trg_identity()',t);
END LOOP; END $$;

CREATE FUNCTION beauty.trg_membership() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$
DECLARE r text; sid bigint; BEGIN
 IF TG_TABLE_NAME='salon' THEN
  SELECT role INTO r FROM beauty.user_account WHERE user_id=NEW.owner_user_id;
  IF r IS DISTINCT FROM 'OWNER' THEN RAISE EXCEPTION 'Salon owner must have OWNER role' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='master' THEN
  SELECT role INTO r FROM beauty.user_account WHERE user_id=NEW.user_id;
  IF r IS DISTINCT FROM 'MASTER' THEN RAISE EXCEPTION 'Profile requires MASTER role' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='master_service' THEN
  IF TG_OP='UPDATE' AND (NEW.master_id<>OLD.master_id OR NEW.salon_service_id<>OLD.salon_service_id) THEN
   RAISE EXCEPTION 'Assignment key is immutable' USING ERRCODE='23514'; END IF;
  SELECT salon_id INTO sid FROM beauty.master WHERE master_id=NEW.master_id;
  IF sid IS DISTINCT FROM (SELECT salon_id FROM beauty.salon_service WHERE salon_service_id=NEW.salon_service_id) THEN
   RAISE EXCEPTION 'Master and service must belong to the same salon' USING ERRCODE='23514'; END IF;
 ELSIF TG_TABLE_NAME='master_invitation' THEN
  PERFORM beauty.require_actor(NEW.created_by_user_id,ARRAY['OWNER']);
  IF NEW.created_by_user_id IS DISTINCT FROM (SELECT s.owner_user_id FROM beauty.master m JOIN beauty.salon s USING(salon_id) WHERE m.master_id=NEW.master_id) THEN
   RAISE EXCEPTION 'Invitation belongs to another salon' USING ERRCODE='42501'; END IF;
  IF TG_OP='INSERT' THEN
   IF NOT EXISTS(SELECT FROM beauty.master m JOIN beauty.user_account u ON u.user_id=m.user_id WHERE m.master_id=NEW.master_id AND u.account_status='INVITED') THEN
    RAISE EXCEPTION 'A new invitation requires a pending master account' USING ERRCODE='23514'; END IF;
  END IF;
 END IF; RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN FOREACH t IN ARRAY ARRAY['salon','master','master_service','master_invitation'] LOOP
 EXECUTE format('CREATE TRIGGER c_membership BEFORE INSERT OR UPDATE ON beauty.%I FOR EACH ROW EXECUTE FUNCTION beauty.trg_membership()',t);
END LOOP; END $$;

CREATE FUNCTION beauty.trg_future_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$
DECLARE bad boolean; BEGIN
 IF TG_TABLE_NAME='master' THEN
  IF OLD.is_active AND NOT NEW.is_active THEN SELECT EXISTS(SELECT FROM beauty.appointment WHERE master_id=OLD.master_id AND status='CONFIRMED' AND end_at>beauty.local_now()) INTO bad; END IF;
 ELSIF TG_TABLE_NAME='salon_service' THEN
  IF OLD.is_active AND NOT NEW.is_active THEN SELECT EXISTS(SELECT FROM beauty.appointment WHERE salon_service_id=OLD.salon_service_id AND status='CONFIRMED' AND end_at>beauty.local_now()) INTO bad; END IF;
 ELSIF TG_TABLE_NAME='master_service' THEN
  IF TG_OP='DELETE' OR (OLD.is_active AND NOT NEW.is_active) THEN SELECT EXISTS(SELECT FROM beauty.appointment WHERE master_id=OLD.master_id AND salon_service_id=OLD.salon_service_id AND status='CONFIRMED' AND end_at>beauty.local_now()) INTO bad; END IF;
 ELSIF TG_TABLE_NAME='work_interval' THEN
  IF TG_OP='UPDATE' AND NEW.master_id<>OLD.master_id THEN RAISE EXCEPTION 'Work interval master is immutable' USING ERRCODE='23514'; END IF;
  SELECT EXISTS(SELECT FROM beauty.appointment a WHERE a.master_id=OLD.master_id AND a.status='CONFIRMED' AND a.end_at>beauty.local_now()
   AND NOT EXISTS(SELECT FROM beauty.work_interval w WHERE w.master_id=a.master_id AND w.work_interval_id<>OLD.work_interval_id AND w.slot @> a.slot)
   AND NOT (TG_OP='UPDATE' AND NEW.master_id=a.master_id AND tsrange(NEW.work_date+NEW.start_time,NEW.work_date+NEW.end_time,'[)') @> a.slot)) INTO bad;
 END IF;
 IF coalesce(bad,false) THEN RAISE EXCEPTION 'Change would invalidate a future appointment' USING ERRCODE='23514'; END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
END $$;
CREATE TRIGGER d_future BEFORE UPDATE ON beauty.master FOR EACH ROW EXECUTE FUNCTION beauty.trg_future_guard();
CREATE TRIGGER d_future BEFORE UPDATE ON beauty.salon_service FOR EACH ROW EXECUTE FUNCTION beauty.trg_future_guard();
CREATE TRIGGER d_future BEFORE UPDATE OR DELETE ON beauty.master_service FOR EACH ROW EXECUTE FUNCTION beauty.trg_future_guard();
CREATE TRIGGER d_future BEFORE UPDATE OR DELETE ON beauty.work_interval FOR EACH ROW EXECUTE FUNCTION beauty.trg_future_guard();

CREATE FUNCTION beauty.trg_appointment() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$
DECLARE v_service beauty.salon_service; v_master beauty.master; v_salon beauty.salon; u beauty.user_account; v_slot tsrange; v_end timestamp;
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Appointments are historical records' USING ERRCODE='23514'; END IF;
 SELECT * INTO v_service FROM beauty.salon_service WHERE salon_service_id=NEW.salon_service_id;
 SELECT * INTO v_master FROM beauty.master WHERE master_id=NEW.master_id;
 SELECT * INTO v_salon FROM beauty.salon WHERE salon_id=v_service.salon_id;
 IF TG_OP='INSERT' THEN
  PERFORM beauty.require_actor(NEW.client_user_id,ARRAY['CLIENT']);
  IF NEW.status<>'CONFIRMED' THEN RAISE EXCEPTION 'A new appointment must be CONFIRMED' USING ERRCODE='23514'; END IF;
  IF v_salon.publication_status IS DISTINCT FROM 'PUBLISHED' OR NOT coalesce(v_service.is_active,false)
   OR NOT coalesce(v_master.is_active,false) OR v_master.salon_id IS DISTINCT FROM v_service.salon_id
   OR NOT EXISTS(SELECT FROM beauty.master_service WHERE master_id=NEW.master_id AND salon_service_id=NEW.salon_service_id AND is_active)
   OR NOT EXISTS(SELECT FROM beauty.user_account WHERE user_id=v_master.user_id AND account_status='ACTIVE') THEN
   RAISE EXCEPTION 'Salon, master or service is unavailable' USING ERRCODE='23514'; END IF;
  IF NEW.start_at<beauty.local_now() OR NEW.start_at::date >= beauty.local_now()::date+30 THEN
   RAISE EXCEPTION 'Appointment is outside the 30-day horizon' USING ERRCODE='23514'; END IF;
  NEW.service_name_snapshot:=v_service.name; NEW.price_snapshot:=v_service.price; NEW.duration_snapshot:=v_service.duration_minutes;
  v_slot:=tsrange(NEW.start_at,NEW.start_at+make_interval(mins=>NEW.duration_snapshot),'[)');
  IF NOT EXISTS(SELECT FROM beauty.work_interval WHERE master_id=NEW.master_id AND slot @> v_slot) THEN
   RAISE EXCEPTION 'Appointment does not fit one working interval' USING ERRCODE='23514'; END IF;
 ELSE
  IF ROW(NEW.appointment_id,NEW.client_user_id,NEW.master_id,NEW.salon_service_id,NEW.start_at,NEW.service_name_snapshot,NEW.price_snapshot,NEW.duration_snapshot,NEW.created_at)
   IS DISTINCT FROM ROW(OLD.appointment_id,OLD.client_user_id,OLD.master_id,OLD.salon_service_id,OLD.start_at,OLD.service_name_snapshot,OLD.price_snapshot,OLD.duration_snapshot,OLD.created_at) THEN
   RAISE EXCEPTION 'Confirmed appointment terms are immutable' USING ERRCODE='23514'; END IF;
  IF OLD.status<>'CONFIRMED' OR NEW.status='CONFIRMED' THEN
   IF ROW(NEW.status,NEW.cancelled_at,NEW.cancelled_by_user_id,NEW.cancellation_reason,NEW.result_marked_at,NEW.result_marked_by_user_id)
    IS DISTINCT FROM ROW(OLD.status,OLD.cancelled_at,OLD.cancelled_by_user_id,OLD.cancellation_reason,OLD.result_marked_at,OLD.result_marked_by_user_id)
    THEN RAISE EXCEPTION 'Invalid or terminal status transition' USING ERRCODE='23514'; END IF;
   RETURN NEW;
  END IF;
  v_end:=OLD.end_at;
  IF NEW.status='CANCELLED' THEN
   u:=beauty.require_actor(NEW.cancelled_by_user_id,ARRAY['CLIENT','MASTER','OWNER','ADMIN']);
   IF OLD.start_at<=beauty.local_now() THEN RAISE EXCEPTION 'A started appointment cannot be cancelled' USING ERRCODE='23514'; END IF;
   IF NOT ((u.role='CLIENT' AND u.user_id=OLD.client_user_id) OR (u.role='MASTER' AND u.user_id=v_master.user_id)
    OR (u.role='OWNER' AND u.user_id=v_salon.owner_user_id)
    OR (u.role='ADMIN' AND EXISTS(SELECT FROM beauty.user_account WHERE user_id=v_salon.owner_user_id AND account_status='BLOCKED'))) THEN
    RAISE EXCEPTION 'Appointment belongs to another actor' USING ERRCODE='42501'; END IF;
   IF u.role<>'CLIENT' AND coalesce(btrim(NEW.cancellation_reason),'')='' THEN RAISE EXCEPTION 'Cancellation reason is required' USING ERRCODE='23514'; END IF;
   NEW.cancelled_at:=beauty.local_now();
  ELSIF NEW.status IN ('COMPLETED','NO_SHOW') THEN
   u:=beauty.require_actor(NEW.result_marked_by_user_id,ARRAY['MASTER','OWNER']);
   IF v_end>beauty.local_now() THEN RAISE EXCEPTION 'Appointment has not ended' USING ERRCODE='23514'; END IF;
   IF NOT ((u.role='MASTER' AND u.user_id=v_master.user_id) OR (u.role='OWNER' AND u.user_id=v_salon.owner_user_id)) THEN
    RAISE EXCEPTION 'Appointment belongs to another actor' USING ERRCODE='42501'; END IF;
   NEW.result_marked_at:=beauty.local_now();
  ELSE RAISE EXCEPTION 'Invalid status' USING ERRCODE='23514'; END IF;
 END IF; RETURN NEW;
END $$;
CREATE TRIGGER b_appointment BEFORE INSERT OR UPDATE OR DELETE ON beauty.appointment FOR EACH ROW EXECUTE FUNCTION beauty.trg_appointment();

CREATE FUNCTION beauty.trg_review() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$
BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Reviews cannot be deleted' USING ERRCODE='23514'; END IF;
 IF TG_OP='UPDATE' AND ROW(NEW.review_id,NEW.appointment_id,NEW.target_type,NEW.rating,NEW.text,NEW.created_at)
  IS DISTINCT FROM ROW(OLD.review_id,OLD.appointment_id,OLD.target_type,OLD.rating,OLD.text,OLD.created_at) THEN
  RAISE EXCEPTION 'Review content is immutable' USING ERRCODE='23514'; END IF;
 IF NOT EXISTS(SELECT FROM beauty.appointment WHERE appointment_id=NEW.appointment_id AND status='COMPLETED') THEN
  RAISE EXCEPTION 'Review requires a completed visit' USING ERRCODE='23514'; END IF; RETURN NEW;
END $$;
CREATE TRIGGER b_review BEFORE INSERT OR UPDATE OR DELETE ON beauty.review FOR EACH ROW EXECUTE FUNCTION beauty.trg_review();

CREATE FUNCTION beauty.trg_photo() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$
DECLARE n bigint; BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Archive a photo instead of deleting it' USING ERRCODE='23514'; END IF;
 IF TG_OP='UPDATE' THEN
  IF NEW.file_path<>OLD.file_path THEN RAISE EXCEPTION 'Photo identity is immutable' USING ERRCODE='23514'; END IF;
  IF TG_TABLE_NAME='salon_photo' THEN
   IF NEW.salon_id<>OLD.salon_id THEN RAISE EXCEPTION 'Photo owner is immutable' USING ERRCODE='23514'; END IF;
  ELSE IF NEW.master_id<>OLD.master_id THEN RAISE EXCEPTION 'Photo owner is immutable' USING ERRCODE='23514'; END IF; END IF;
 END IF;
 IF NEW.visibility<>'ARCHIVED' THEN
  IF TG_TABLE_NAME='salon_photo' THEN SELECT count(*) INTO n FROM beauty.salon_photo WHERE salon_id=NEW.salon_id AND visibility<>'ARCHIVED' AND file_path<>NEW.file_path;
  ELSE SELECT count(*) INTO n FROM beauty.master_photo WHERE master_id=NEW.master_id AND visibility<>'ARCHIVED' AND file_path<>NEW.file_path; END IF;
  IF n>=20 THEN RAISE EXCEPTION 'Photo limit is 20' USING ERRCODE='23514'; END IF;
 END IF; RETURN NEW;
END $$;
CREATE TRIGGER b_photo BEFORE INSERT OR UPDATE OR DELETE ON beauty.salon_photo FOR EACH ROW EXECUTE FUNCTION beauty.trg_photo();
CREATE TRIGGER b_photo BEFORE INSERT OR UPDATE OR DELETE ON beauty.master_photo FOR EACH ROW EXECUTE FUNCTION beauty.trg_photo();

CREATE FUNCTION beauty.trg_moderation() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$
DECLARE cur text; nxt text; BEGIN
 IF TG_OP<>'INSERT' THEN RAISE EXCEPTION 'Moderation decisions are append-only' USING ERRCODE='23514'; END IF;
 PERFORM beauty.require_actor(NEW.admin_user_id,ARRAY['ADMIN']);
 IF NEW.photo_path IS NOT NULL THEN
  IF NEW.target_salon_id IS NOT NULL THEN SELECT visibility INTO cur FROM beauty.salon_photo WHERE salon_id=NEW.target_salon_id AND file_path=NEW.photo_path;
  ELSE SELECT visibility INTO cur FROM beauty.master_photo WHERE master_id=NEW.target_master_id AND file_path=NEW.photo_path; END IF;
 ELSIF NEW.target_review_id IS NOT NULL THEN SELECT visibility INTO cur FROM beauty.review WHERE review_id=NEW.target_review_id;
 ELSIF NEW.target_user_id IS NOT NULL THEN SELECT account_status INTO cur FROM beauty.user_account WHERE user_id=NEW.target_user_id;
 ELSIF NEW.target_master_id IS NOT NULL THEN SELECT u.account_status INTO cur FROM beauty.master m JOIN beauty.user_account u ON u.user_id=m.user_id WHERE m.master_id=NEW.target_master_id;
 ELSE SELECT publication_status INTO cur FROM beauty.salon WHERE salon_id=NEW.target_salon_id; END IF;
 nxt:=CASE
  WHEN NEW.action='HIDE' AND cur='PUBLISHED' AND (NEW.photo_path IS NOT NULL OR NEW.target_review_id IS NOT NULL) THEN 'HIDDEN'
  WHEN NEW.action='RESTORE' AND cur='HIDDEN' AND (NEW.photo_path IS NOT NULL OR NEW.target_review_id IS NOT NULL) THEN 'PUBLISHED'
  WHEN NEW.action='BLOCK' AND cur='ACTIVE' AND (NEW.target_user_id IS NOT NULL OR NEW.target_master_id IS NOT NULL) THEN 'BLOCKED'
  WHEN NEW.action='UNBLOCK' AND cur='BLOCKED' AND (NEW.target_user_id IS NOT NULL OR NEW.target_master_id IS NOT NULL) THEN 'ACTIVE'
  WHEN NEW.action='APPROVE' AND cur='PENDING' AND NEW.target_salon_id IS NOT NULL THEN 'PUBLISHED'
  WHEN NEW.action='RETURN' AND cur='PENDING' AND NEW.target_salon_id IS NOT NULL THEN 'RETURNED'
  WHEN NEW.action='UNPUBLISH' AND cur='PUBLISHED' AND NEW.target_salon_id IS NOT NULL THEN 'UNPUBLISHED'
  WHEN NEW.action='PUBLISH' AND cur='UNPUBLISHED' AND NEW.target_salon_id IS NOT NULL THEN 'PUBLISHED'
  WHEN NEW.action='BLOCK' AND cur IN ('PUBLISHED','UNPUBLISHED') AND NEW.target_salon_id IS NOT NULL THEN 'BLOCKED'
  WHEN NEW.action='UNBLOCK' AND cur='BLOCKED' AND NEW.target_salon_id IS NOT NULL THEN 'UNPUBLISHED' END;
 IF nxt IS NULL THEN RAISE EXCEPTION 'Invalid moderation target/action/state' USING ERRCODE='23514'; END IF;
 IF NEW.photo_path IS NOT NULL THEN
  IF NEW.target_salon_id IS NOT NULL THEN UPDATE beauty.salon_photo SET visibility=nxt WHERE salon_id=NEW.target_salon_id AND file_path=NEW.photo_path;
  ELSE UPDATE beauty.master_photo SET visibility=nxt WHERE master_id=NEW.target_master_id AND file_path=NEW.photo_path; END IF;
 ELSIF NEW.target_review_id IS NOT NULL THEN UPDATE beauty.review SET visibility=nxt WHERE review_id=NEW.target_review_id;
 ELSIF NEW.target_user_id IS NOT NULL THEN UPDATE beauty.user_account SET account_status=nxt WHERE user_id=NEW.target_user_id;
 ELSIF NEW.target_master_id IS NOT NULL THEN
  -- Administrative blocking uses the account state: existing appointments stay for the owner to resolve.
  UPDATE beauty.user_account SET account_status=nxt WHERE user_id=(SELECT user_id FROM beauty.master WHERE master_id=NEW.target_master_id);
 ELSE UPDATE beauty.salon SET publication_status=nxt WHERE salon_id=NEW.target_salon_id; END IF;
 NEW.created_at:=beauty.local_now(); RETURN NEW;
END $$;
CREATE TRIGGER b_moderation BEFORE INSERT OR UPDATE OR DELETE ON beauty.moderation_decision FOR EACH ROW EXECUTE FUNCTION beauty.trg_moderation();

CREATE UNIQUE INDEX uq_invitation_open ON beauty.master_invitation(master_id) WHERE used_at IS NULL AND revoked_at IS NULL;
-- An expired token is still an open row; reissuing first revokes it, then inserts the next token.
CREATE FUNCTION beauty.trg_invitation_history() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,beauty AS $$ BEGIN
 IF TG_OP='DELETE' THEN RAISE EXCEPTION 'Invitation history cannot be deleted' USING ERRCODE='23514'; END IF;
 IF ROW(NEW.invitation_id,NEW.master_id,NEW.created_by_user_id,NEW.token_hash,NEW.created_at,NEW.expires_at)
  IS DISTINCT FROM ROW(OLD.invitation_id,OLD.master_id,OLD.created_by_user_id,OLD.token_hash,OLD.created_at,OLD.expires_at)
  OR OLD.used_at IS NOT NULL OR OLD.revoked_at IS NOT NULL THEN
  RAISE EXCEPTION 'Invitation identity or terminal state is immutable' USING ERRCODE='23514'; END IF;
 RETURN NEW; END $$;
CREATE TRIGGER b_history BEFORE UPDATE OR DELETE ON beauty.master_invitation FOR EACH ROW EXECUTE FUNCTION beauty.trg_invitation_history();
