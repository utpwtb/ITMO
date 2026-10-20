-- Actor IDs are supplied only by the authenticated trusted backend.
-- SECURITY DEFINER APIs expose no table DML to that backend; search_path is fixed.
CREATE FUNCTION beauty.register_user(p_email text,p_name text,p_password text,p_role text) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE id bigint; BEGIN
 PERFORM beauty.lock_writes();
 IF p_role NOT IN ('CLIENT','OWNER') OR p_role IS NULL THEN RAISE EXCEPTION 'Public registration supports CLIENT or OWNER' USING ERRCODE='42501'; END IF;
 IF p_password IS NULL OR octet_length(p_password) NOT BETWEEN 12 AND 72 THEN RAISE EXCEPTION 'Password length must be 12..72 bytes' USING ERRCODE='22023'; END IF;
 INSERT INTO beauty.user_account(email,display_name,password_hash,role) VALUES(lower(btrim(p_email)),p_name,public.crypt(p_password,public.gen_salt('bf',12)),p_role) RETURNING user_id INTO id; RETURN id;
END $$;
CREATE FUNCTION beauty.authenticate(p_email text,p_password text) RETURNS TABLE(user_id bigint,role text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 RETURN QUERY SELECT u.user_id,u.role FROM beauty.user_account u WHERE u.email=lower(btrim(p_email)) AND u.account_status='ACTIVE' AND u.password_hash=public.crypt(p_password,u.password_hash);
 IF NOT FOUND THEN RAISE EXCEPTION 'Invalid credentials' USING ERRCODE='42501'; END IF;
END $$;

CREATE FUNCTION beauty.available_slots(p_master bigint,p_service bigint,p_date date)
RETURNS TABLE(start_at timestamp,end_at timestamp,price numeric,duration_minutes integer)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$
 SELECT g.t,g.t+make_interval(mins=>s.duration_minutes),s.price,s.duration_minutes
 FROM beauty.master m JOIN beauty.user_account u ON u.user_id=m.user_id
 JOIN beauty.master_service ms ON ms.master_id=m.master_id AND ms.is_active
 JOIN beauty.salon_service s ON s.salon_service_id=ms.salon_service_id AND s.salon_id=m.salon_id AND s.is_active
 JOIN beauty.salon sl ON sl.salon_id=m.salon_id AND sl.publication_status='PUBLISHED'
 CROSS JOIN generate_series(p_date::timestamp,p_date::timestamp+interval '23 hours 45 minutes',interval '15 minutes') g(t)
 WHERE m.master_id=p_master AND s.salon_service_id=p_service AND m.is_active AND u.account_status='ACTIVE'
  AND p_date>=beauty.local_now()::date AND p_date<beauty.local_now()::date+30 AND g.t>=beauty.local_now()
  AND EXISTS(SELECT FROM beauty.work_interval w WHERE w.master_id=m.master_id AND w.work_date=p_date AND w.slot @> tsrange(g.t,g.t+make_interval(mins=>s.duration_minutes),'[)'))
  AND NOT EXISTS(SELECT FROM beauty.appointment a WHERE a.master_id=m.master_id AND a.status='CONFIRMED' AND a.slot && tsrange(g.t,g.t+make_interval(mins=>s.duration_minutes),'[)'))
 ORDER BY g.t
$$;
CREATE FUNCTION beauty.book_appointment(p_client bigint,p_master bigint,p_service bigint,p_start timestamp,p_expected_price numeric,p_expected_duration integer) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE s beauty.salon_service; id bigint; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_client,ARRAY['CLIENT']);
 SELECT * INTO s FROM beauty.salon_service WHERE salon_service_id=p_service;
 IF NOT FOUND THEN RAISE EXCEPTION 'Service does not exist' USING ERRCODE='23503'; END IF;
 IF s.price IS DISTINCT FROM p_expected_price OR s.duration_minutes IS DISTINCT FROM p_expected_duration THEN
  RAISE EXCEPTION 'Service terms changed; confirm again' USING ERRCODE='22023'; END IF;
 INSERT INTO beauty.appointment(client_user_id,master_id,salon_service_id,start_at,service_name_snapshot,price_snapshot,duration_snapshot)
 VALUES(p_client,p_master,p_service,p_start,s.name,s.price,s.duration_minutes) RETURNING appointment_id INTO id; RETURN id;
END $$;
CREATE FUNCTION beauty.cancel_appointment(p_actor bigint,p_appointment bigint,p_reason text DEFAULT NULL) RETURNS text
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE a beauty.appointment; u beauty.user_account; m beauty.master; s beauty.salon; BEGIN
 PERFORM beauty.lock_writes(); u:=beauty.require_actor(p_actor,ARRAY['CLIENT','MASTER','OWNER','ADMIN']);
 SELECT * INTO a FROM beauty.appointment WHERE appointment_id=p_appointment;
 IF NOT FOUND THEN RAISE EXCEPTION 'Appointment not found' USING ERRCODE='23503'; END IF;
 SELECT * INTO m FROM beauty.master WHERE master_id=a.master_id; SELECT * INTO s FROM beauty.salon WHERE salon_id=m.salon_id;
 IF NOT ((u.role='CLIENT' AND u.user_id=a.client_user_id) OR (u.role='MASTER' AND u.user_id=m.user_id) OR (u.role='OWNER' AND u.user_id=s.owner_user_id)
  OR (u.role='ADMIN' AND EXISTS(SELECT FROM beauty.user_account WHERE user_id=s.owner_user_id AND account_status='BLOCKED'))) THEN RAISE EXCEPTION 'Appointment belongs to another actor' USING ERRCODE='42501'; END IF;
 IF a.status='CANCELLED' THEN RETURN a.status; END IF;
 UPDATE beauty.appointment SET status='CANCELLED',cancelled_at=beauty.local_now(),cancelled_by_user_id=p_actor,cancellation_reason=p_reason WHERE appointment_id=p_appointment;
 RETURN 'CANCELLED'; END $$;
CREATE PROCEDURE beauty.mark_visit(p_actor bigint,p_appointment bigint,p_result text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_actor,ARRAY['MASTER','OWNER']);
 IF p_result NOT IN ('COMPLETED','NO_SHOW') OR p_result IS NULL THEN RAISE EXCEPTION 'Invalid visit result' USING ERRCODE='22023'; END IF;
 UPDATE beauty.appointment SET status=p_result,result_marked_at=beauty.local_now(),result_marked_by_user_id=p_actor WHERE appointment_id=p_appointment;
 IF NOT FOUND THEN RAISE EXCEPTION 'Appointment not found' USING ERRCODE='23503'; END IF;
END $$;
CREATE FUNCTION beauty.add_review(p_client bigint,p_appointment bigint,p_target text,p_rating smallint,p_text text DEFAULT NULL) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE id bigint; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_client,ARRAY['CLIENT']);
 IF NOT EXISTS(SELECT FROM beauty.appointment WHERE appointment_id=p_appointment AND client_user_id=p_client) THEN RAISE EXCEPTION 'Visit belongs to another client' USING ERRCODE='42501'; END IF;
 INSERT INTO beauty.review(appointment_id,target_type,rating,text) VALUES(p_appointment,p_target,p_rating,p_text) RETURNING review_id INTO id; RETURN id;
END $$;
CREATE FUNCTION beauty.moderate(p_admin bigint,p_kind text,p_target bigint,p_action text,p_reason text,p_photo_path text DEFAULT NULL) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE id bigint; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_admin,ARRAY['ADMIN']);
 IF p_kind NOT IN ('USER','SALON','MASTER','REVIEW') OR p_kind IS NULL THEN RAISE EXCEPTION 'Invalid moderation kind' USING ERRCODE='22023'; END IF;
 INSERT INTO beauty.moderation_decision(admin_user_id,target_user_id,target_salon_id,target_master_id,target_review_id,photo_path,action,reason)
 VALUES(p_admin,CASE WHEN p_kind='USER' THEN p_target END,CASE WHEN p_kind='SALON' THEN p_target END,
 CASE WHEN p_kind='MASTER' THEN p_target END,CASE WHEN p_kind='REVIEW' THEN p_target END,p_photo_path,p_action,p_reason) RETURNING decision_id INTO id; RETURN id;
END $$;

CREATE FUNCTION beauty.invite_master(p_owner bigint,p_salon bigint,p_email text,p_name text) RETURNS TABLE(master_id bigint,token text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE uid bigint; mid bigint; raw text; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 IF NOT EXISTS(SELECT FROM beauty.salon WHERE salon_id=p_salon AND owner_user_id=p_owner AND publication_status<>'ARCHIVED') THEN RAISE EXCEPTION 'Salon belongs to another owner' USING ERRCODE='42501'; END IF;
 INSERT INTO beauty.user_account(email,display_name,role,account_status) VALUES(lower(btrim(p_email)),p_name,'MASTER','INVITED') RETURNING user_id INTO uid;
 INSERT INTO beauty.master(user_id,salon_id,is_active) VALUES(uid,p_salon,false) RETURNING beauty.master.master_id INTO mid;
 raw:=encode(public.gen_random_bytes(32),'hex');
 INSERT INTO beauty.master_invitation(master_id,created_by_user_id,token_hash,expires_at)
 VALUES(mid,p_owner,encode(public.digest(raw,'sha256'),'hex'),beauty.local_now()+interval '2 days');
 RETURN QUERY SELECT mid,raw;
END $$;
CREATE FUNCTION beauty.reissue_invitation(p_owner bigint,p_master bigint) RETURNS text
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE raw text; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 IF NOT EXISTS(SELECT FROM beauty.master m JOIN beauty.salon s USING(salon_id) JOIN beauty.user_account u ON u.user_id=m.user_id
  WHERE m.master_id=p_master AND s.owner_user_id=p_owner AND u.account_status='INVITED') THEN RAISE EXCEPTION 'Master is not awaiting activation in this salon' USING ERRCODE='42501'; END IF;
 UPDATE beauty.master_invitation SET revoked_at=beauty.local_now() WHERE master_id=p_master AND used_at IS NULL AND revoked_at IS NULL;
 raw:=encode(public.gen_random_bytes(32),'hex');
 INSERT INTO beauty.master_invitation(master_id,created_by_user_id,token_hash,expires_at) VALUES(p_master,p_owner,encode(public.digest(raw,'sha256'),'hex'),beauty.local_now()+interval '2 days'); RETURN raw;
END $$;
CREATE FUNCTION beauty.accept_invitation(p_token text,p_password text) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE i beauty.master_invitation; uid bigint; BEGIN
 PERFORM beauty.lock_writes();
 IF p_password IS NULL OR octet_length(p_password) NOT BETWEEN 12 AND 72 THEN RAISE EXCEPTION 'Password length must be 12..72 bytes' USING ERRCODE='22023'; END IF;
 SELECT * INTO i FROM beauty.master_invitation WHERE token_hash=encode(public.digest(p_token,'sha256'),'hex') AND used_at IS NULL AND revoked_at IS NULL AND expires_at>beauty.local_now();
 IF NOT FOUND THEN RAISE EXCEPTION 'Invitation is invalid or expired' USING ERRCODE='22023'; END IF;
 SELECT user_id INTO uid FROM beauty.master WHERE master_id=i.master_id;
 IF NOT EXISTS(SELECT FROM beauty.user_account WHERE user_id=uid AND account_status='INVITED') THEN RAISE EXCEPTION 'Account is not awaiting activation' USING ERRCODE='23514'; END IF;
 UPDATE beauty.user_account SET password_hash=public.crypt(p_password,public.gen_salt('bf',12)),account_status='ACTIVE' WHERE user_id=uid;
 UPDATE beauty.master SET is_active=true WHERE master_id=i.master_id;
 UPDATE beauty.master_invitation SET used_at=beauty.local_now() WHERE invitation_id=i.invitation_id;
 RETURN uid;
END $$;

CREATE PROCEDURE beauty.set_master_service(p_owner bigint,p_master bigint,p_service bigint,p_active boolean)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 IF NOT EXISTS(SELECT FROM beauty.master m JOIN beauty.salon s USING(salon_id) WHERE m.master_id=p_master AND s.owner_user_id=p_owner) THEN RAISE EXCEPTION 'Master belongs to another salon' USING ERRCODE='42501'; END IF;
 INSERT INTO beauty.master_service(master_id,salon_service_id,is_active) VALUES(p_master,p_service,p_active)
 ON CONFLICT(master_id,salon_service_id) DO UPDATE SET is_active=excluded.is_active;
END $$;
CREATE FUNCTION beauty.save_work_interval(p_owner bigint,p_master bigint,p_date date,p_start time,p_end time,p_id bigint DEFAULT NULL) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE id bigint; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 IF NOT EXISTS(SELECT FROM beauty.master m JOIN beauty.salon s USING(salon_id) WHERE m.master_id=p_master AND s.owner_user_id=p_owner) THEN RAISE EXCEPTION 'Master belongs to another salon' USING ERRCODE='42501'; END IF;
 IF p_id IS NULL THEN INSERT INTO beauty.work_interval(master_id,work_date,start_time,end_time) VALUES(p_master,p_date,p_start,p_end) RETURNING work_interval_id INTO id;
 ELSE UPDATE beauty.work_interval SET work_date=p_date,start_time=p_start,end_time=p_end WHERE work_interval_id=p_id AND master_id=p_master RETURNING work_interval_id INTO id;
  IF NOT FOUND THEN RAISE EXCEPTION 'Working interval not found' USING ERRCODE='23503'; END IF; END IF; RETURN id;
END $$;
CREATE PROCEDURE beauty.delete_work_interval(p_owner bigint,p_id bigint)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 IF NOT EXISTS(SELECT FROM beauty.work_interval w JOIN beauty.master m USING(master_id) JOIN beauty.salon s USING(salon_id) WHERE w.work_interval_id=p_id AND s.owner_user_id=p_owner) THEN RAISE EXCEPTION 'Working interval belongs to another salon' USING ERRCODE='42501'; END IF;
 DELETE FROM beauty.work_interval WHERE work_interval_id=p_id;
END $$;
CREATE FUNCTION beauty.save_service(p_owner bigint,p_salon bigint,p_type bigint,p_name text,p_price numeric,p_minutes integer,p_active boolean DEFAULT true,p_id bigint DEFAULT NULL) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE id bigint; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 IF NOT EXISTS(SELECT FROM beauty.salon WHERE salon_id=p_salon AND owner_user_id=p_owner) THEN RAISE EXCEPTION 'Salon belongs to another owner' USING ERRCODE='42501'; END IF;
 IF p_id IS NULL THEN INSERT INTO beauty.salon_service(salon_id,service_type_id,name,price,duration_minutes,is_active) VALUES(p_salon,p_type,p_name,p_price,p_minutes,p_active) RETURNING salon_service_id INTO id;
 ELSE UPDATE beauty.salon_service SET service_type_id=p_type,name=p_name,price=p_price,duration_minutes=p_minutes,is_active=p_active WHERE salon_service_id=p_id AND salon_id=p_salon RETURNING salon_service_id INTO id;
  IF NOT FOUND THEN RAISE EXCEPTION 'Service not found in salon' USING ERRCODE='23503'; END IF; END IF; RETURN id;
END $$;
CREATE PROCEDURE beauty.save_master_profile(p_actor bigint,p_master bigint,p_specialization text,p_experience text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_actor,ARRAY['MASTER','OWNER']);
 IF NOT EXISTS(SELECT FROM beauty.master m JOIN beauty.salon s USING(salon_id) WHERE m.master_id=p_master AND (m.user_id=p_actor OR s.owner_user_id=p_actor)) THEN RAISE EXCEPTION 'Profile belongs to another actor' USING ERRCODE='42501'; END IF;
 UPDATE beauty.master SET specialization=p_specialization,experience_description=p_experience WHERE master_id=p_master;
END $$;
CREATE FUNCTION beauty.create_salon(p_owner bigint,p_district bigint,p_name text,p_address text,p_lat numeric,p_lon numeric,p_phone text,p_hours text) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE id bigint; BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 INSERT INTO beauty.salon(owner_user_id,district_id,name,address,latitude,longitude,phone,opening_hours)
 VALUES(p_owner,p_district,p_name,p_address,p_lat,p_lon,p_phone,p_hours) RETURNING salon_id INTO id; RETURN id;
END $$;
CREATE PROCEDURE beauty.resubmit_salon(p_owner bigint,p_salon bigint)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_owner,ARRAY['OWNER']);
 UPDATE beauty.salon SET publication_status='PENDING' WHERE salon_id=p_salon AND owner_user_id=p_owner AND publication_status='RETURNED';
 IF NOT FOUND THEN RAISE EXCEPTION 'Salon cannot be resubmitted' USING ERRCODE='23514'; END IF;
END $$;
CREATE PROCEDURE beauty.put_photo(p_actor bigint,p_kind text,p_target bigint,p_path text,p_caption text,p_order integer,p_mime text,p_bytes integer)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_actor,ARRAY['OWNER','MASTER']);
 IF p_kind='SALON' THEN
  IF NOT EXISTS(SELECT FROM beauty.salon WHERE salon_id=p_target AND owner_user_id=p_actor) THEN RAISE EXCEPTION 'Photo belongs to another salon' USING ERRCODE='42501'; END IF;
  INSERT INTO beauty.salon_photo(salon_id,file_path,caption,sort_order,mime_type,byte_size) VALUES(p_target,p_path,p_caption,p_order,p_mime,p_bytes);
 ELSIF p_kind='MASTER' THEN
  IF NOT EXISTS(SELECT FROM beauty.master m JOIN beauty.salon s USING(salon_id) WHERE m.master_id=p_target AND (m.user_id=p_actor OR s.owner_user_id=p_actor)) THEN RAISE EXCEPTION 'Work belongs to another actor' USING ERRCODE='42501'; END IF;
  INSERT INTO beauty.master_photo(master_id,file_path,caption,sort_order,mime_type,byte_size) VALUES(p_target,p_path,p_caption,p_order,p_mime,p_bytes);
 ELSE RAISE EXCEPTION 'Invalid photo kind' USING ERRCODE='22023'; END IF;
END $$;
CREATE PROCEDURE beauty.archive_photo(p_actor bigint,p_kind text,p_target bigint,p_path text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 PERFORM beauty.lock_writes(); PERFORM beauty.require_actor(p_actor,ARRAY['OWNER','MASTER']);
 IF p_kind='SALON' THEN
  IF NOT EXISTS(SELECT FROM beauty.salon WHERE salon_id=p_target AND owner_user_id=p_actor) THEN RAISE EXCEPTION 'Photo belongs to another salon' USING ERRCODE='42501'; END IF;
  UPDATE beauty.salon_photo SET visibility='ARCHIVED' WHERE salon_id=p_target AND file_path=p_path;
 ELSIF p_kind='MASTER' THEN
  IF NOT EXISTS(SELECT FROM beauty.master m JOIN beauty.salon s USING(salon_id) WHERE m.master_id=p_target AND (m.user_id=p_actor OR s.owner_user_id=p_actor)) THEN RAISE EXCEPTION 'Work belongs to another actor' USING ERRCODE='42501'; END IF;
  UPDATE beauty.master_photo SET visibility='ARCHIVED' WHERE master_id=p_target AND file_path=p_path;
 ELSE RAISE EXCEPTION 'Invalid photo kind' USING ERRCODE='22023'; END IF;
 IF NOT FOUND THEN RAISE EXCEPTION 'Photo not found' USING ERRCODE='23503'; END IF;
END $$;

CREATE VIEW beauty.salon_rating AS SELECT ss.salon_id,avg(r.rating)::numeric(3,2) AS rating,count(*) AS review_count
 FROM beauty.review r JOIN beauty.appointment a USING(appointment_id) JOIN beauty.salon_service ss USING(salon_service_id)
 WHERE r.target_type='SALON' AND r.visibility='PUBLISHED' GROUP BY ss.salon_id;
CREATE VIEW beauty.master_rating AS SELECT a.master_id,avg(r.rating)::numeric(3,2) AS rating,count(*) AS review_count
 FROM beauty.review r JOIN beauty.appointment a USING(appointment_id) WHERE r.target_type='MASTER' AND r.visibility='PUBLISHED' GROUP BY a.master_id;
CREATE FUNCTION beauty.distance_km(a numeric,b numeric,c numeric,d numeric) RETURNS double precision LANGUAGE sql IMMUTABLE STRICT SET search_path=pg_catalog AS $$
 SELECT 12742*asin(least(1.0,sqrt(power(sin(radians((c-a)::double precision)/2),2)+cos(radians(a::double precision))*cos(radians(c::double precision))*power(sin(radians((d-b)::double precision)/2),2)))) $$;
CREATE FUNCTION beauty.search_salons(p_district bigint DEFAULT NULL,p_type bigint DEFAULT NULL,p_min_price numeric DEFAULT NULL,p_max_price numeric DEFAULT NULL,
 p_date date DEFAULT NULL,p_lat numeric DEFAULT NULL,p_lon numeric DEFAULT NULL,p_radius numeric DEFAULT NULL,
 p_south numeric DEFAULT NULL,p_west numeric DEFAULT NULL,p_north numeric DEFAULT NULL,p_east numeric DEFAULT NULL,p_sort text DEFAULT 'PRICE')
RETURNS TABLE(salon_id bigint,name text,address text,latitude numeric,longitude numeric,min_price numeric,distance_km double precision,rating numeric,review_count bigint)
LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ BEGIN
 IF num_nonnulls(p_lat,p_lon,p_radius) NOT IN (0,3) OR num_nonnulls(p_south,p_west,p_north,p_east) NOT IN (0,4)
  OR num_nonnulls(p_district,p_lat,p_south)>1 OR p_radius<=0 OR p_lat NOT BETWEEN -90 AND 90 OR p_lon NOT BETWEEN -180 AND 180
  OR p_south>p_north OR p_west>p_east OR p_south NOT BETWEEN -90 AND 90 OR p_north NOT BETWEEN -90 AND 90
  OR p_west NOT BETWEEN -180 AND 180 OR p_east NOT BETWEEN -180 AND 180
  OR p_min_price<0 OR p_max_price<0 OR p_min_price>p_max_price OR p_sort NOT IN ('PRICE','DISTANCE') OR p_sort IS NULL
  OR (p_sort='DISTANCE' AND p_lat IS NULL) THEN RAISE EXCEPTION 'Invalid search parameters' USING ERRCODE='22023'; END IF;
 RETURN QUERY SELECT s.salon_id,s.name,s.address,s.latitude,s.longitude,svc.min_price,
  beauty.distance_km(p_lat,p_lon,s.latitude,s.longitude),rt.rating,coalesce(rt.review_count,0)
 FROM beauty.salon s LEFT JOIN beauty.salon_rating rt USING(salon_id)
 LEFT JOIN LATERAL(SELECT min(ss.price) AS min_price FROM beauty.salon_service ss WHERE ss.salon_id=s.salon_id AND ss.is_active
  AND (p_type IS NULL OR ss.service_type_id=p_type) AND (p_min_price IS NULL OR ss.price>=p_min_price) AND (p_max_price IS NULL OR ss.price<=p_max_price)
  AND (p_date IS NULL OR EXISTS(SELECT FROM beauty.master_service ms WHERE ms.salon_service_id=ss.salon_service_id AND ms.is_active
    AND EXISTS(SELECT FROM beauty.available_slots(ms.master_id,ss.salon_service_id,p_date) LIMIT 1)))) svc ON true
 WHERE s.publication_status='PUBLISHED' AND (p_district IS NULL OR s.district_id=p_district)
  AND (p_south IS NULL OR (s.latitude BETWEEN p_south AND p_north AND s.longitude BETWEEN p_west AND p_east))
  AND (p_lat IS NULL OR beauty.distance_km(p_lat,p_lon,s.latitude,s.longitude)<=p_radius)
  AND (num_nonnulls(p_type,p_min_price,p_max_price,p_date)=0 OR svc.min_price IS NOT NULL)
 ORDER BY CASE WHEN p_sort='PRICE' THEN svc.min_price END NULLS LAST,
  CASE WHEN p_sort='DISTANCE' THEN beauty.distance_km(p_lat,p_lon,s.latitude,s.longitude) END NULLS LAST,s.salon_id;
END $$;
CREATE FUNCTION beauty.appointment_journal(p_actor bigint,p_date date DEFAULT NULL,p_status text DEFAULT NULL)
RETURNS TABLE(appointment_id bigint,salon_id bigint,master_id bigint,client_name text,master_name text,service_name text,start_at timestamp,end_at timestamp,price numeric,status text)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,beauty,pg_temp AS $$ DECLARE u beauty.user_account; BEGIN
 u:=beauty.require_actor(p_actor,ARRAY['CLIENT','MASTER','OWNER']);
 RETURN QUERY SELECT a.appointment_id,s.salon_id,m.master_id,cu.display_name,mu.display_name,a.service_name_snapshot,a.start_at,a.end_at,a.price_snapshot,a.status
 FROM beauty.appointment a JOIN beauty.master m USING(master_id) JOIN beauty.salon s USING(salon_id)
 JOIN beauty.user_account cu ON cu.user_id=a.client_user_id JOIN beauty.user_account mu ON mu.user_id=m.user_id
 WHERE ((u.role='CLIENT' AND a.client_user_id=p_actor) OR (u.role='MASTER' AND m.user_id=p_actor) OR (u.role='OWNER' AND s.owner_user_id=p_actor))
 AND (p_date IS NULL OR (a.start_at>=p_date::timestamp AND a.start_at<p_date::timestamp+interval '1 day')) AND (p_status IS NULL OR a.status=p_status)
 ORDER BY a.start_at,a.appointment_id;
END $$;
