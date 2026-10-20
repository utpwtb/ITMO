-- Deterministic synthetic history, relative to installation date. No real personal data.
-- Run only after 01_tables.sql and before triggers, in the same installation transaction.
INSERT INTO beauty.district(district_id,name) SELECT i,'Район '||i FROM generate_series(1,10) i;
INSERT INTO beauty.service_type(service_type_id,name) VALUES
 (1,'Маникюр'),(2,'Педикюр'),(3,'Стрижка'),(4,'Укладка'),(5,'Окрашивание'),(6,'Уход');
CREATE TEMP TABLE seed_password ON COMMIT DROP AS SELECT public.crypt('demo-password-2026',public.gen_salt('bf',8)) AS hash;
INSERT INTO beauty.user_account(user_id,email,display_name,password_hash,role)
 SELECT 1,'admin@example.test','Администратор',hash,'ADMIN' FROM seed_password;
INSERT INTO beauty.user_account(user_id,email,display_name,password_hash,role)
 SELECT 1000+i,'owner'||i||'@example.test','Владелец '||i,hash,'OWNER' FROM generate_series(1,100) i CROSS JOIN seed_password;
INSERT INTO beauty.user_account(user_id,email,display_name,password_hash,role)
 SELECT 2000+i,'master'||i||'@example.test','Мастер '||i,hash,'MASTER' FROM generate_series(1,500) i CROSS JOIN seed_password;
INSERT INTO beauty.user_account(user_id,email,display_name,password_hash,role)
 SELECT 10000+i,'client'||i||'@example.test','Клиент '||i,hash,'CLIENT' FROM generate_series(1,5000) i CROSS JOIN seed_password;
INSERT INTO beauty.salon(salon_id,owner_user_id,district_id,name,address,latitude,longitude,phone,opening_hours,publication_status)
 SELECT i,1000+i,(i-1)%10+1,'Салон '||i,'Учебная улица, '||i,59.90+(i%10)*.006,30.25+(i/10)*.008,'+70000000000','09:00-18:00','PUBLISHED' FROM generate_series(1,100) i;
INSERT INTO beauty.master(master_id,user_id,salon_id,specialization,experience_description)
 SELECT i,2000+i,(i-1)/5+1,'Услуги красоты','Учебный профиль' FROM generate_series(1,500) i;
INSERT INTO beauty.salon_service(salon_service_id,salon_id,service_type_id,name,price,duration_minutes)
 SELECT (s.salon_id-1)*6+t.service_type_id,s.salon_id,t.service_type_id,t.name||' базовый',
  500+t.service_type_id*200+(s.salon_id%10)*25,
  CASE t.service_type_id WHEN 1 THEN 45 WHEN 2 THEN 60 WHEN 3 THEN 35 WHEN 4 THEN 30 WHEN 5 THEN 90 ELSE 120 END
 FROM beauty.salon s CROSS JOIN beauty.service_type t;
INSERT INTO beauty.master_service(master_id,salon_service_id)
 SELECT m.master_id,s.salon_service_id FROM beauty.master m JOIN beauty.salon_service s USING(salon_id) WHERE s.service_type_id<=3;
INSERT INTO beauty.work_interval(master_id,work_date,start_time,end_time)
 SELECT m.master_id,current_date-d,'09:00','18:00' FROM beauty.master m CROSS JOIN generate_series(1,100) d;
INSERT INTO beauty.work_interval(master_id,work_date,start_time,end_time)
 SELECT m.master_id,current_date+d,v.a::time,v.b::time FROM beauty.master m CROSS JOIN generate_series(0,29) d
 CROSS JOIN (VALUES('09:00','13:00'),('14:00','18:00')) v(a,b);
INSERT INTO beauty.appointment(appointment_id,client_user_id,master_id,salon_service_id,start_at,service_name_snapshot,price_snapshot,duration_snapshot,status,created_at,
 cancelled_at,cancelled_by_user_id,result_marked_at,result_marked_by_user_id)
 SELECT (d-1)*500+m.master_id,10001+(((d-1)*500+m.master_id)%5000),m.master_id,ss.salon_service_id,
  (current_date-d)+time '09:00',ss.name,ss.price,ss.duration_minutes,
  CASE d%6 WHEN 0 THEN 'CANCELLED' WHEN 1 THEN 'NO_SHOW' ELSE 'COMPLETED' END,(current_date-d-1)+time '09:00',
  CASE WHEN d%6=0 THEN (current_date-d)+time '08:30' END,
  CASE WHEN d%6=0 THEN 10001+(((d-1)*500+m.master_id)%5000) END,
  CASE WHEN d%6<>0 THEN (current_date-d)+time '09:00'+make_interval(mins=>ss.duration_minutes+5) END,
  CASE WHEN d%6<>0 THEN m.user_id END
 FROM beauty.master m CROSS JOIN generate_series(1,100) d
 JOIN beauty.salon_service ss ON ss.salon_id=m.salon_id AND ss.service_type_id=(m.master_id-1)%3+1;
INSERT INTO beauty.appointment(appointment_id,client_user_id,master_id,salon_service_id,start_at,service_name_snapshot,price_snapshot,duration_snapshot,status,created_at)
 SELECT v.id,10001,v.mid,v.sid,(current_date+v.delta)+v.tm,ss.name,ss.price,ss.duration_minutes,'CONFIRMED',beauty.local_now()-interval '1 day'
 FROM (VALUES(50001,1,1,-1,time '10:00'),(50002,2,2,-1,time '11:00'),(50003,1,1,1,time '09:00'),(50004,2,2,1,time '14:00')) v(id,mid,sid,delta,tm)
 JOIN beauty.salon_service ss ON ss.salon_service_id=v.sid;
INSERT INTO beauty.appointment(appointment_id,client_user_id,master_id,salon_service_id,start_at,service_name_snapshot,price_snapshot,duration_snapshot,status,created_at,cancelled_at,cancelled_by_user_id)
 SELECT 50005,10001,3,3,current_date+1+time '09:00',name,price,duration_minutes,'CANCELLED',beauty.local_now()-interval '1 hour',beauty.local_now(),10001 FROM beauty.salon_service WHERE salon_service_id=3;
INSERT INTO beauty.review(appointment_id,target_type,rating,text)
 SELECT a.appointment_id,t.kind,(a.appointment_id%5+1)::smallint,'Учебный отзыв'
 FROM (SELECT appointment_id FROM beauty.appointment WHERE status='COMPLETED' ORDER BY appointment_id LIMIT 6000) a CROSS JOIN (VALUES('SALON'),('MASTER')) t(kind);
UPDATE beauty.review SET visibility='HIDDEN' WHERE review_id=1;
INSERT INTO beauty.salon_photo(salon_id,file_path,caption,mime_type,byte_size)
 SELECT salon_id,'salon/'||salon_id||'/interior.png','Интерьер (пример метаданных)','image/png',1024 FROM beauty.salon;
INSERT INTO beauty.master_photo(master_id,file_path,caption,mime_type,byte_size)
 SELECT master_id,'master/'||master_id||'/work.png','Работа (пример метаданных)','image/png',2048 FROM beauty.master;
INSERT INTO beauty.moderation_decision(decision_id,admin_user_id,target_salon_id,action,reason) VALUES(1,1,100,'APPROVE','Демонстрация одобрения');
INSERT INTO beauty.moderation_decision(decision_id,admin_user_id,target_review_id,action,reason) VALUES(2,1,1,'HIDE','Демонстрация скрытого отзыва');
UPDATE beauty.user_account SET account_status='BLOCKED' WHERE user_id=2500;
INSERT INTO beauty.moderation_decision(decision_id,admin_user_id,target_master_id,action,reason) VALUES(3,1,500,'BLOCK','Демонстрация блокировки мастера');
INSERT INTO beauty.user_account(user_id,email,display_name,role,account_status) VALUES(2501,'invited@example.test','Приглашённый мастер','MASTER','INVITED');
INSERT INTO beauty.master(master_id,user_id,salon_id,is_active) VALUES(501,2501,1,false);
INSERT INTO beauty.master_invitation(invitation_id,master_id,created_by_user_id,token_hash,expires_at)
 VALUES(1,501,1001,encode(public.digest('demo-invitation-to-reissue','sha256'),'hex'),beauty.local_now()+interval '2 days');
DO $$ DECLARE c record; seq text; BEGIN
 FOR c IN SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='beauty' AND is_identity='YES' LOOP
  seq:=pg_get_serial_sequence('beauty.'||c.table_name,c.column_name);
  EXECUTE format('SELECT setval(%L,coalesce(max(%I),1),true) FROM beauty.%I',seq,c.column_name,c.table_name);
 END LOOP;
END $$;
-- Validate cross-row conditions in the imported history, in addition to active DDL constraints.
DO $$ BEGIN
 IF EXISTS(SELECT FROM beauty.master_service ms JOIN beauty.master m USING(master_id) JOIN beauty.salon_service s USING(salon_service_id) WHERE m.salon_id<>s.salon_id)
  OR EXISTS(SELECT FROM beauty.review r JOIN beauty.appointment a USING(appointment_id) WHERE a.status<>'COMPLETED')
  OR EXISTS(SELECT FROM beauty.appointment a WHERE NOT EXISTS(SELECT FROM beauty.work_interval w WHERE w.master_id=a.master_id AND w.slot @> a.slot)) THEN
  RAISE EXCEPTION 'Invalid seed history'; END IF;
END $$;
