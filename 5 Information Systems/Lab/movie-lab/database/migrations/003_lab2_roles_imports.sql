-- Idempotent upgrade: preserves accounts, credentials and all Lab 1 domain data.
ALTER TABLE app_user ADD COLUMN IF NOT EXISTS role varchar(10) NOT NULL DEFAULT 'USER'
    CHECK (role IN ('USER','ADMIN'));
CREATE TABLE IF NOT EXISTS import_operation (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY CHECK(id>0),
    user_id bigint NOT NULL REFERENCES app_user(id),
    status varchar(20) NOT NULL CHECK(status IN ('RUNNING','SUCCESS','FAILED')),
    added_count integer,
    started_at timestamp with time zone NOT NULL,
    finished_at timestamp with time zone,
    filename varchar(255) NOT NULL,
    error_code varchar(64),
    error_message varchar(1000),
    CHECK ((status='SUCCESS' AND added_count>0 AND finished_at IS NOT NULL) OR
           (status='RUNNING' AND added_count IS NULL AND finished_at IS NULL) OR
           (status='FAILED' AND added_count IS NULL AND finished_at IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS import_operation_user_idx ON import_operation(user_id,started_at DESC,id DESC);
