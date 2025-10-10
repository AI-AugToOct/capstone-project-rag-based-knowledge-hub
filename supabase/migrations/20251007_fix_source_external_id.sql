-- Add unique constraint on source_external_id
-- This replaces the partial index with a full constraint

BEGIN;

-- Drop the partial index
DROP INDEX IF EXISTS documents_source_unique;

-- Add unique constraint (allows multiple NULLs, but unique non-NULL values)
-- Note: In PostgreSQL, NULL values are considered distinct, so multiple NULL values are allowed
ALTER TABLE documents 
  ADD CONSTRAINT documents_source_external_id_unique 
  UNIQUE (source_external_id);

COMMIT;
