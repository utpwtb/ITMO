"""Each case runs in its own transaction and rolls back. Expected SQLSTATE is explicit."""
CASES = [
 ('fourteen physical tables',"DO $$ BEGIN ASSERT (SELECT count(*)=14 FROM information_schema.tables WHERE table_schema='beauty' AND table_type='BASE TABLE'); ASSERT (SELECT count(*)=50005 FROM beauty.appointment); END $$;",None),
 ('35-minute duration with 15-minute start grid',"DO $$ BEGIN ASSERT (SELECT count(*)=28 FROM beauty.available_slots(3,3,beauty.local_now()::date+1)); END $$;",None),
 ('adjacent appointments accepted',"SELECT beauty.book_appointment(10001,1,1,beauty.local_now()::date+1+time '09:45',725,45);",None),
 ('overlapping appointment rejected',"SELECT beauty.book_appointment(10001,1,1,beauty.local_now()::date+1+time '09:15',725,45);",'23P01'),
 ('appointment crossing lunch gap rejected',"SELECT beauty.book_appointment(10001,3,3,beauty.local_now()::date+1+time '12:45',1125,35);",'23514'),
 ('start outside 15-minute grid rejected',"SELECT beauty.book_appointment(10001,3,3,beauty.local_now()::date+1+time '10:05',1125,35);",'23514'),
 ('past appointment rejected',"SELECT beauty.book_appointment(10001,3,3,beauty.local_now()::date-1+time '14:00',1125,35);",'23514'),
 ('day thirty outside horizon rejected',"SELECT beauty.book_appointment(10001,3,3,beauty.local_now()::date+30+time '10:00',1125,35);",'23514'),
 ('non-client cannot book',"SELECT beauty.book_appointment(1001,3,3,beauty.local_now()::date+1+time '10:00',1125,35);",'42501'),
 ('blocked master unavailable',"SELECT beauty.book_appointment(10001,500,595,beauty.local_now()::date+1+time '10:00',700,45);",'23514'),
 ('wrong client cannot cancel',"SELECT beauty.cancel_appointment(10002,50003);",'42501'),
 ('wrong owner cannot cancel',"SELECT beauty.cancel_appointment(1002,50003,'reason');",'42501'),
 ('master cancellation needs reason',"SELECT beauty.cancel_appointment(2001,50003);",'23514'),
 ('started appointment cannot be cancelled',"SELECT beauty.cancel_appointment(1001,50001,'reason');",'23514'),
 ('cancellation idempotence and slot release',"""DO $$ DECLARE t timestamp; BEGIN
 PERFORM beauty.cancel_appointment(10001,50003); SELECT cancelled_at INTO t FROM beauty.appointment WHERE appointment_id=50003;
 PERFORM beauty.cancel_appointment(10001,50003,'second'); ASSERT (SELECT cancelled_at=t AND cancellation_reason IS NULL FROM beauty.appointment WHERE appointment_id=50003);
 ASSERT (SELECT count(*)=28 FROM beauty.available_slots(1,1,beauty.local_now()::date+1)); END $$;""",None),
 ('completion before planned end rejected',"CALL beauty.mark_visit(2001,50003,'COMPLETED');",'23514'),
 ('completed visit enables two independent reviews',"""CALL beauty.mark_visit(2001,50001,'COMPLETED');
 SELECT beauty.add_review(10001,50001,'SALON',4::smallint,'salon'); SELECT beauty.add_review(10001,50001,'MASTER',5::smallint,'master');
 DO $$ BEGIN ASSERT (SELECT count(*)=2 FROM beauty.review WHERE appointment_id=50001); END $$;""",None),
 ('no-show gives no right to review',"CALL beauty.mark_visit(1001,50002,'NO_SHOW'); SELECT beauty.add_review(10001,50002,'SALON',4::smallint);",'23514'),
 ('terminal visit result immutable',"CALL beauty.mark_visit(2001,501,'NO_SHOW');",'23514'),
 ('snapshots survive catalog edits',"""UPDATE beauty.salon_service SET price=999,duration_minutes=70,name='Updated' WHERE salon_service_id=1;
 DO $$ BEGIN ASSERT (SELECT price_snapshot=725 AND duration_snapshot=45 AND service_name_snapshot='Маникюр базовый' FROM beauty.appointment WHERE appointment_id=50003); END $$;
 SELECT beauty.book_appointment(10001,1,1,beauty.local_now()::date+1+time '10:00',999,70);""",None),
 ('changed terms require reconfirmation',"UPDATE beauty.salon_service SET price=999 WHERE salon_service_id=1; SELECT beauty.book_appointment(10001,1,1,beauty.local_now()::date+1+time '10:00',725,45);",'22023'),
 ('future booking protects master deactivation',"UPDATE beauty.master SET is_active=false WHERE master_id=1;",'23514'),
 ('future booking protects service deactivation',"UPDATE beauty.salon_service SET is_active=false WHERE salon_service_id=1;",'23514'),
 ('future booking protects assignment deactivation',"CALL beauty.set_master_service(1001,1,1,false);",'23514'),
 ('future booking protects schedule shortening',"UPDATE beauty.work_interval SET start_time='10:00' WHERE master_id=1 AND work_date=beauty.local_now()::date+1 AND start_time='09:00';",'23514'),
 ('future booking protects schedule deletion',"DELETE FROM beauty.work_interval WHERE master_id=1 AND work_date=beauty.local_now()::date+1 AND start_time='09:00';",'23514'),
 ('unoccupied schedule can be changed',"UPDATE beauty.work_interval SET start_time='10:00' WHERE master_id=3 AND work_date=beauty.local_now()::date+1 AND start_time='09:00';",None),
 ('overlapping working intervals rejected',"SELECT beauty.save_work_interval(1001,3,beauty.local_now()::date+1,time '12:00',time '14:00');",'23P01'),
 ('cross-salon master service rejected',"CALL beauty.set_master_service(1001,1,7,true);",'23514'),
 ('owner has at most one salon',"SELECT beauty.create_salon(1001,1,'extra','address',59,30,'phone','hours');",'23505'),
 ('owner role checked by trigger',"INSERT INTO beauty.salon(owner_user_id,district_id,name,address,latitude,longitude,phone,opening_hours) VALUES(10001,1,'bad','a',59,30,'p','h');",'23514'),
 ('user role cannot be changed',"UPDATE beauty.user_account SET role='MASTER' WHERE user_id=10001;",'23514'),
 ('master cannot move to another salon',"UPDATE beauty.master SET salon_id=2 WHERE master_id=1;",'23514'),
 ('wrong client cannot review another visit',"SELECT beauty.add_review(10001,501,'SALON',5::smallint);",'42501'),
 ('rating range checked',"SELECT beauty.add_review(10502,501,'SALON',6::smallint);",'23514'),
 ('one review per target enforced',"SELECT beauty.add_review(10502,501,'SALON',5::smallint);",'23505'),
 ('appointment history cannot be deleted',"DELETE FROM beauty.appointment WHERE appointment_id=50005;",'23514'),
 ('review content cannot be edited',"UPDATE beauty.review SET text='changed' WHERE review_id=2;",'23514'),
 ('only admin may moderate',"SELECT beauty.moderate(1001,'SALON',1,'UNPUBLISH','reason');",'42501'),
 ('moderation XOR violation rolls back target change',"""DO $$ BEGIN
 BEGIN INSERT INTO beauty.moderation_decision(admin_user_id,target_user_id,target_salon_id,action,reason) VALUES(1,10001,1,'BLOCK','bad XOR'); RAISE EXCEPTION 'expected violation';
 EXCEPTION WHEN check_violation THEN NULL; END;
 ASSERT (SELECT account_status='ACTIVE' FROM beauty.user_account WHERE user_id=10001); END $$;""",None),
 ('photo moderation requires existing attribute element',"SELECT beauty.moderate(1,'SALON',1,'HIDE','reason','missing.png');",'23514'),
 ('photo attributes moderated via parent and path',"""SELECT beauty.moderate(1,'SALON',1,'HIDE','reason','salon/1/interior.png');
 DO $$ BEGIN ASSERT (SELECT visibility='HIDDEN' FROM beauty.salon_photo WHERE salon_id=1); END $$;
 SELECT beauty.moderate(1,'SALON',1,'RESTORE','reason','salon/1/interior.png');""",None),
 ('wrong owner cannot upload a work',"CALL beauty.put_photo(1002,'MASTER',1,'x.png','',0,'image/png',100);",'42501'),
 ('file metadata size constrained',"CALL beauty.put_photo(1001,'SALON',1,'x.png','',0,'image/png',5242881);",'23514'),
 ('file metadata MIME constrained',"CALL beauty.put_photo(1001,'SALON',1,'x.svg','',0,'image/svg+xml',100);",'23514'),
 ('photo quota includes hidden elements and releases archived ones',"""DO $$ DECLARE i integer; BEGIN
 FOR i IN 1..19 LOOP CALL beauty.put_photo(1001,'SALON',1,'quota/'||i||'.png','',0,'image/png',100); END LOOP;
 BEGIN CALL beauty.put_photo(1001,'SALON',1,'quota/overflow.png','',0,'image/png',100); RAISE EXCEPTION 'expected quota'; EXCEPTION WHEN check_violation THEN NULL; END;
 CALL beauty.archive_photo(1001,'SALON',1,'salon/1/interior.png'); CALL beauty.put_photo(1001,'SALON',1,'quota/replacement.png','',0,'image/png',100);
 ASSERT (SELECT count(*)=20 FROM beauty.salon_photo WHERE salon_id=1 AND visibility<>'ARCHIVED'); END $$;""",None),
 ('salon and master ratings independent after moderation',"""DO $$ DECLARE r record; sc bigint; mc bigint; BEGIN
 SELECT v.review_id,a.master_id,s.salon_id INTO r FROM beauty.review v JOIN beauty.appointment a USING(appointment_id) JOIN beauty.salon_service s USING(salon_service_id) WHERE v.target_type='SALON' AND v.visibility='PUBLISHED' ORDER BY v.review_id LIMIT 1;
 SELECT review_count INTO sc FROM beauty.salon_rating WHERE salon_id=r.salon_id; SELECT review_count INTO mc FROM beauty.master_rating WHERE master_id=r.master_id;
 PERFORM beauty.moderate(1,'REVIEW',r.review_id,'HIDE','reason'); ASSERT (SELECT review_count=sc-1 FROM beauty.salon_rating WHERE salon_id=r.salon_id); ASSERT (SELECT review_count=mc FROM beauty.master_rating WHERE master_id=r.master_id);
 PERFORM beauty.moderate(1,'REVIEW',r.review_id,'RESTORE','reason'); ASSERT (SELECT review_count=sc FROM beauty.salon_rating WHERE salon_id=r.salon_id); END $$;""",None),
 ('master account block preserves existing bookings',"""SELECT beauty.moderate(1,'MASTER',1,'BLOCK','reason');
 DO $$ BEGIN ASSERT (SELECT status='CONFIRMED' FROM beauty.appointment WHERE appointment_id=50003); ASSERT (SELECT count(*)=0 FROM beauty.available_slots(1,1,beauty.local_now()::date+1)); END $$;
 SELECT beauty.cancel_appointment(1001,50003,'owner resolves'); SELECT beauty.moderate(1,'MASTER',1,'UNBLOCK','reason');""",None),
 ('unpublishing prevents new bookings and preserves old ones',"""SELECT beauty.moderate(1,'SALON',1,'UNPUBLISH','reason');
 DO $$ BEGIN ASSERT (SELECT status='CONFIRMED' FROM beauty.appointment WHERE appointment_id=50003); ASSERT (SELECT count(*)=0 FROM beauty.available_slots(1,1,beauty.local_now()::date+1)); END $$;
 SELECT beauty.moderate(1,'SALON',1,'PUBLISH','reason');""",None),
 ('admin exceptional cancellation requires blocked owner',"SELECT beauty.cancel_appointment(1,50003,'exception');",'42501'),
 ('admin resolves bookings of a blocked owner',"SELECT beauty.moderate(1,'USER',1001,'BLOCK','reason'); SELECT beauty.cancel_appointment(1,50003,'blocked owner');",None),
 ('password required for active client',"INSERT INTO beauty.user_account(email,display_name,role) VALUES('nopassword@example.test','bad','CLIENT');",'23514'),
 ('INVITED status restricted to MASTER role',"INSERT INTO beauty.user_account(email,display_name,password_hash,role,account_status) VALUES('invalid-invited@example.test','bad','non-null','CLIENT','INVITED');",'23514'),
 ('new invitation cannot target an already active master',"INSERT INTO beauty.master_invitation(master_id,created_by_user_id,token_hash,expires_at) VALUES(1,1001,'invalid-active-invitation',beauty.local_now()+interval '2 days');",'23514'),
 ('email normalized and duplicate rejected',"SELECT beauty.register_user('CLIENT1@EXAMPLE.TEST','duplicate','long-demo-password','CLIENT');",'23505'),
 ('registration and password verification through backend API',"""SET LOCAL ROLE beauty_test_backend;
 DO $$ DECLARE id bigint; aid bigint; BEGIN id:=beauty.register_user('new@example.test','New','long-demo-password','CLIENT'); SELECT user_id INTO aid FROM beauty.authenticate('NEW@EXAMPLE.TEST','long-demo-password'); ASSERT id=aid; END $$;""",None),
 ('public cannot register admin',"SELECT beauty.register_user('new@example.test','New','long-demo-password','ADMIN');",'42501'),
 ('invitation never takes over an existing email',"SELECT * FROM beauty.invite_master(1001,1,'client1@example.test','bad');",'23505'),
 ('reissue revokes old token and new token is consumed once',"""DO $$ DECLARE token text; uid bigint; BEGIN
 token:=beauty.reissue_invitation(1001,501);
 BEGIN PERFORM beauty.accept_invitation('demo-invitation-to-reissue','long-demo-password'); RAISE EXCEPTION 'expected revoked token'; EXCEPTION WHEN invalid_parameter_value THEN NULL; END;
 uid:=beauty.accept_invitation(token,'long-demo-password'); ASSERT uid=2501;
 BEGIN PERFORM beauty.accept_invitation(token,'long-demo-password'); RAISE EXCEPTION 'expected used token'; EXCEPTION WHEN invalid_parameter_value THEN NULL; END;
 ASSERT (SELECT account_status='ACTIVE' AND password_hash IS NOT NULL FROM beauty.user_account WHERE user_id=uid); END $$;""",None),
 ('expired invitation rejected',"""UPDATE beauty.master_invitation SET revoked_at=beauty.local_now() WHERE invitation_id=1;
 INSERT INTO beauty.master_invitation(master_id,created_by_user_id,token_hash,created_at,expires_at) VALUES(501,1001,encode(public.digest('expired-token','sha256'),'hex'),beauty.local_now()-interval '3 days',beauty.local_now()-interval '1 day');
 SELECT beauty.accept_invitation('expired-token','long-demo-password');""",'22023'),
 ('backend denied direct table access',"SET LOCAL ROLE beauty_test_backend; SELECT password_hash FROM beauty.user_account;",'42501'),
 ('backend denied private lock helper',"SET LOCAL ROLE beauty_test_backend; SELECT beauty.lock_writes();",'42501'),
 ('untrusted database role denied API access',"SET LOCAL ROLE beauty_test_public; SELECT * FROM beauty.search_salons();",'42501'),
 ('journal limits records by actor',"""DO $$ BEGIN ASSERT NOT EXISTS(SELECT FROM beauty.appointment_journal(1001) WHERE salon_id<>1); ASSERT NOT EXISTS(SELECT FROM beauty.appointment_journal(2001) WHERE master_id<>1); END $$;""",None),
 ('service type and price filter apply to the same service',"DO $$ BEGIN ASSERT (SELECT count(*)=0 FROM beauty.search_salons(p_type=>2,p_max_price=>800)); ASSERT (SELECT count(*)=30 FROM beauty.search_salons(p_type=>1,p_max_price=>750)); END $$;",None),
 ('geographic modes mutually exclusive',"SELECT * FROM beauty.search_salons(p_district=>1,p_lat=>59.9,p_lon=>30.3,p_radius=>3);",'22023'),
 ('map bounds applied',"DO $$ BEGIN ASSERT (SELECT count(*)=1 FROM beauty.search_salons(p_south=>59.905,p_north=>59.907,p_west=>30.249,p_east=>30.251)); END $$;",None),
 ('published salon without services still visible without filters',"""DO $$ DECLARE uid bigint; sid bigint; BEGIN
 uid:=beauty.register_user('empty-owner@example.test','Owner','long-demo-password','OWNER'); sid:=beauty.create_salon(uid,1,'Empty','address',59.9,30.3,'phone','hours'); PERFORM beauty.moderate(1,'SALON',sid,'APPROVE','reason');
 ASSERT EXISTS(SELECT FROM beauty.search_salons() x WHERE x.salon_id=sid AND min_price IS NULL);
 ASSERT NOT EXISTS(SELECT FROM beauty.search_salons(p_type=>1) x WHERE x.salon_id=sid); END $$;""",None),
 ('server replaces supplied snapshots with catalog values',"""INSERT INTO beauty.appointment(client_user_id,master_id,salon_service_id,start_at,service_name_snapshot,price_snapshot,duration_snapshot)
 VALUES(10001,3,3,beauty.local_now()::date+1+time '10:00','fake',1,1);
 DO $$ BEGIN ASSERT EXISTS(SELECT FROM beauty.appointment WHERE master_id=3 AND start_at=beauty.local_now()::date+1+time '10:00' AND price_snapshot=1125 AND duration_snapshot=35); END $$;""",None),
 ('wrong isolation level explicitly rejected',"UPDATE beauty.master SET experience_description='test' WHERE master_id=3;",'25000','REPEATABLE READ'),
]
