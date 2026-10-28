-- Preserve existing records. Adding the constraint fails if old data violates it;
-- review those records instead of silently changing either box-office value.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'movie'::regclass AND conname = 'movie_box_office_consistency'
    ) THEN
        ALTER TABLE movie ADD CONSTRAINT movie_box_office_consistency
            CHECK (totalboxoffice IS NULL OR usaboxoffice <= totalboxoffice);
    END IF;
END;
$$;
