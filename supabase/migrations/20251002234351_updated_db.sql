-- ============================================================================
-- Extensions
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- 1) People
-- ============================================================================
CREATE TABLE IF NOT EXISTS employees (
  employee_id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  display_name TEXT
);

-- ============================================================================
-- 2) Projects
-- ============================================================================
CREATE TABLE IF NOT EXISTS projects (
  project_id TEXT PRIMARY KEY,
  name TEXT
);

-- ============================================================================
-- 3) Memberships
-- ============================================================================
CREATE TABLE IF NOT EXISTS employee_projects (
  employee_id UUID REFERENCES employees(employee_id) ON DELETE CASCADE,
  project_id  TEXT REFERENCES projects(project_id)  ON DELETE CASCADE,
  role TEXT,
  PRIMARY KEY (employee_id, project_id)
);

-- ============================================================================
-- 4) Documents
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
  doc_id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  project_id TEXT REFERENCES projects(project_id),
  visibility TEXT NOT NULL CHECK (visibility IN ('Public','Private')) DEFAULT 'Private',
  uri TEXT,
  language TEXT,
  updated_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ,
  source_external_id TEXT,
  content_hash TEXT
);

CREATE INDEX IF NOT EXISTS documents_project_idx ON documents(project_id);
CREATE INDEX IF NOT EXISTS documents_active_idx ON documents(deleted_at) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS documents_source_unique ON documents(source_external_id) WHERE source_external_id IS NOT NULL;

-- ============================================================================
-- 5) Chunks
-- ============================================================================
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id BIGSERIAL PRIMARY KEY,
  doc_id BIGINT REFERENCES documents(doc_id) ON DELETE CASCADE,
  heading_path TEXT[],
  order_in_doc INT NOT NULL,
  page INT,
  text TEXT NOT NULL,
  embedding VECTOR(1024) NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE UNIQUE INDEX IF NOT EXISTS chunks_doc_order_unique ON chunks(doc_id, order_in_doc);

-- ============================================================================
-- 6) Audit
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_queries (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES employees(employee_id),
  query TEXT,
  used_doc_ids BIGINT[],
  created_at TIMESTAMPTZ DEFAULT now()
);