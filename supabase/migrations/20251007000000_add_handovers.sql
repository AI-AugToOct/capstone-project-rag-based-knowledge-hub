-- ============================================================================
-- Migration: Add Handovers Feature
-- ============================================================================
-- This adds handover functionality for employee knowledge transfer
-- Handovers are searchable and have strict ACL (only sender + recipient)
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Create Handovers Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS handovers (
  handover_id BIGSERIAL PRIMARY KEY,

  -- People
  from_employee_id UUID NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,
  to_employee_id UUID NOT NULL REFERENCES employees(employee_id) ON DELETE CASCADE,

  -- Optional CC (for managers or stakeholders)
  cc_employee_ids UUID[],

  -- Context
  project_id TEXT REFERENCES projects(project_id) ON DELETE SET NULL,
  title TEXT NOT NULL,

  -- Structured content (all optional except title)
  context TEXT,              -- Why this handover
  current_status TEXT,       -- What's been done
  next_steps JSONB,          -- Array of tasks: [{"task": "...", "done": false}]
  resources JSONB,           -- Array of links: [{"type": "doc", "doc_id": 123, "title": "..."}]
  contacts JSONB,            -- Array: [{"name": "John", "email": "...", "role": "..."}]
  additional_notes TEXT,     -- Free-form notes

  -- Lifecycle
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'completed')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  acknowledged_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,

  -- Constraints
  CHECK (from_employee_id != to_employee_id),  -- Can't hand over to yourself
  CHECK (acknowledged_at IS NULL OR acknowledged_at >= created_at),
  CHECK (completed_at IS NULL OR completed_at >= created_at)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS handovers_from_idx ON handovers(from_employee_id);
CREATE INDEX IF NOT EXISTS handovers_to_idx ON handovers(to_employee_id);
CREATE INDEX IF NOT EXISTS handovers_status_idx ON handovers(status);
CREATE INDEX IF NOT EXISTS handovers_project_idx ON handovers(project_id);
CREATE INDEX IF NOT EXISTS handovers_created_idx ON handovers(created_at DESC);

-- ============================================================================
-- 2. Update Chunks Table to Support Handovers
-- ============================================================================

-- Make doc_id nullable (chunks can be from handovers instead of documents)
ALTER TABLE chunks ALTER COLUMN doc_id DROP NOT NULL;

-- Add handover_id column
ALTER TABLE chunks ADD COLUMN IF NOT EXISTS handover_id BIGINT REFERENCES handovers(handover_id) ON DELETE CASCADE;

-- Add constraint: chunks must belong to EITHER a document OR a handover
ALTER TABLE chunks ADD CONSTRAINT chunks_source_check
  CHECK (
    (doc_id IS NOT NULL AND handover_id IS NULL) OR
    (doc_id IS NULL AND handover_id IS NOT NULL)
  );

-- Add index for handover chunks
CREATE INDEX IF NOT EXISTS chunks_handover_idx ON chunks(handover_id);

COMMIT;

-- ============================================================================
-- Verification
-- ============================================================================

-- Check table exists
SELECT 'Handovers table created' as status
WHERE EXISTS (
  SELECT FROM information_schema.tables
  WHERE table_name = 'handovers'
);

-- Check chunks column added
SELECT 'Chunks.handover_id column added' as status
WHERE EXISTS (
  SELECT FROM information_schema.columns
  WHERE table_name = 'chunks' AND column_name = 'handover_id'
);

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- Handover ACL (Access Control):
--   User can see handover IF:
--     - user = from_employee_id (they sent it)
--     - user = to_employee_id (they received it)
--     - user IN cc_employee_ids (they were CC'd)
--
-- Handover Lifecycle:
--   1. Created → status = 'pending'
--   2. Recipient acknowledges → status = 'acknowledged', acknowledged_at set
--   3. Work completed → status = 'completed', completed_at set
--
-- Searchability:
--   - Handovers are chunked and embedded when created
--   - Chunks are inserted with handover_id (not doc_id)
--   - Search query includes handover ACL check
--   - Only sender + recipient + CC can find handover in search
--
-- ============================================================================