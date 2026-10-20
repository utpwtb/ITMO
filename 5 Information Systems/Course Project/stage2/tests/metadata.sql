SELECT jsonb_build_object(
 'server_version',current_setting('server_version'),
 'tables',(SELECT jsonb_agg(jsonb_build_object('name',t.table_name,'columns',
  (SELECT jsonb_agg(jsonb_build_object('name',c.column_name,'type',c.data_type,'udt',c.udt_name,'nullable',c.is_nullable='YES',
    'generated',c.is_generated,'expression',c.generation_expression,'default',c.column_default,'precision',c.numeric_precision,'scale',c.numeric_scale) ORDER BY c.ordinal_position)
   FROM information_schema.columns c WHERE c.table_schema='beauty' AND c.table_name=t.table_name)) ORDER BY t.table_name)
  FROM information_schema.tables t WHERE t.table_schema='beauty' AND t.table_type='BASE TABLE'),
 'constraints',(SELECT jsonb_agg(jsonb_build_object('table',r.relname,'name',c.conname,'kind',c.contype,'definition',pg_get_constraintdef(c.oid))) FROM pg_constraint c JOIN pg_class r ON r.oid=c.conrelid JOIN pg_namespace n ON n.oid=r.relnamespace WHERE n.nspname='beauty'),
 'indexes',(SELECT jsonb_agg(jsonb_build_object('table',tablename,'name',indexname,'definition',indexdef)) FROM pg_indexes WHERE schemaname='beauty'),
 'routines',(SELECT jsonb_agg(jsonb_build_object('name',p.proname,'kind',p.prokind,'signature',p.oid::regprocedure::text,'result',pg_get_function_result(p.oid),'security_definer',p.prosecdef)) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='beauty'),
 'triggers',(SELECT jsonb_agg(jsonb_build_object('table',r.relname,'name',t.tgname,'definition',pg_get_triggerdef(t.oid))) FROM pg_trigger t JOIN pg_class r ON r.oid=t.tgrelid JOIN pg_namespace n ON n.oid=r.relnamespace WHERE n.nspname='beauty' AND NOT t.tgisinternal)
);
