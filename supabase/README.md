# Database Schema Guide

## 📊 Visual Schema Diagram

**[View Full ER Diagram (schema.svg)](./schema.svg)**

The diagram shows all 7 tables, their relationships, primary/foreign keys, and data types.

---

## Overview

Our knowledge hub uses **7 tables** to manage permissions, documents, handovers, and search:

```
employees ──┐
            ├──→ employee_projects ──→ projects
            │                             ↓
            ├──→ audit_queries         documents ──→┐
            │                                       ├──→ chunks
            └──→ handovers ──────────────────────────┘
```

**Core idea:**
- Users belong to projects → Documents belong to projects → Only retrieve document chunks user can access
- Users send/receive handovers → Handovers are private → Only retrieve handover chunks user is involved in

**Search combines BOTH sources:**
```sql
SELECT ... FROM chunks
WHERE (doc_id IS NOT NULL AND user can access document)
   OR (handover_id IS NOT NULL AND user is involved in handover)
```

---

## Table 1: `employees`

**Purpose:** Central user registry, synced with Supabase Auth.

| Column | Type | Description |
|--------|------|-------------|
| `employee_id` | UUID | Primary key, matches Supabase `auth.uid()` |
| `email` | TEXT | User's email (unique) |
| `display_name` | TEXT | Optional friendly name |

### Example Data
```sql
employee_id                           | email                    | display_name
--------------------------------------|--------------------------|-------------
550e8400-e29b-41d4-a716-446655440000 | sarah@company.com        | Sarah Chen
6ba7b810-9dad-11d1-80b4-00c04fd430c8 | john@company.com         | John Doe
```

### When It's Used
- When user logs in → Supabase Auth gives JWT → we extract `employee_id`
- To look up which projects user belongs to
- To check handover access (sender, recipient, CC)
- To log searches in `audit_queries`

---

## Table 2: `projects`

**Purpose:** Define access boundaries for private documents and handovers.

| Column | Type | Description |
|--------|------|-------------|
| `project_id` | TEXT | Human-readable ID (e.g., 'atlas-api') |
| `name` | TEXT | Display name |

### Example Data
```sql
project_id    | name
--------------|------------------
atlas-api     | Atlas API
demo-project  | Demo Project
phoenix-ui    | Phoenix UI
```

### When It's Used
- Documents are assigned to projects via `documents.project_id`
- Handovers can reference projects via `handovers.project_id` (optional)
- Users are granted access via `employee_projects`
- Retrieval filters by user's projects

---

## Table 3: `employee_projects`

**Purpose:** Many-to-many junction table. Controls who sees private documents.

| Column | Type | Description |
|--------|------|-------------|
| `employee_id` | UUID | Foreign key → `employees` |
| `project_id` | TEXT | Foreign key → `projects` |
| `role` | TEXT | 'member' or 'manager' |

### Example Data
```sql
employee_id                           | project_id    | role
--------------------------------------|---------------|--------
550e8400-e29b-41d4-a716-446655440000 | atlas-api     | member
550e8400-e29b-41d4-a716-446655440000 | demo-project  | member
6ba7b810-9dad-11d1-80b4-00c04fd430c8 | atlas-api     | manager
```

**Role meanings:**
- **member**: Can view documents, receive handovers
- **manager**: Can upload documents, create handovers

**Translation:**
- Sarah (employee) can see atlas-api and demo-project private docs
- John (manager) can see atlas-api docs AND upload new docs

### When It's Used
```python
# In /api/search, we load user's projects:
projects = db.execute("""
    SELECT project_id
    FROM employee_projects
    WHERE employee_id = %s
""", (user_id,))
# Result: ['atlas-api', 'demo-project']
```

---

## Table 4: `documents`

**Purpose:** One row per Notion page or uploaded file. Metadata only, no content.

| Column | Type | Description |
|--------|------|-------------|
| `doc_id` | BIGSERIAL | Primary key |
| `title` | TEXT | "Atlas Deploy Guide" |
| `project_id` | TEXT | Which project owns this (nullable for Public) |
| `visibility` | TEXT | 'Public' or 'Private' |
| `uri` | TEXT | Deep link back to Notion page or file URL |
| `language` | TEXT | Optional: 'en', 'ar' |
| `updated_at` | TIMESTAMPTZ | When content last changed |
| `deleted_at` | TIMESTAMPTZ | Soft delete (null = active) |
| `source_external_id` | TEXT | Notion page ID or upload UUID (for upserts) |
| `content_hash` | TEXT | MD5 of markdown (skip re-embed if unchanged) |

### Example Data
```sql
doc_id | title                  | project_id    | visibility | uri                          | deleted_at | source_external_id     | content_hash
-------|------------------------|---------------|------------|------------------------------|------------|------------------------|-------------
1      | Atlas Deploy Guide     | atlas-api     | Private    | https://notion.so/abc123     | NULL       | notion_abc123          | d8e8fca2dc...
2      | Company Handbook       | NULL          | Public     | https://notion.so/def456     | NULL       | notion_def456          | 9b74c9897b...
3      | Phoenix Design Guide   | phoenix-ui    | Private    | upload://uuid123/design.pdf  | NULL       | upload_uuid123         | 7f3d4e5a1c...
```

**Access rules:**
- Doc 1 (Atlas Deploy Guide): Only users in atlas-api project can see it
- Doc 2 (Company Handbook): Everyone can see it (Public)
- Doc 3 (Phoenix Design Guide): Only users in phoenix-ui project can see it

### When It's Used
```sql
-- Retrieval query checks access:
WHERE d.deleted_at IS NULL
  AND (
    d.visibility = 'Public'
    OR d.project_id = ANY(ARRAY['atlas-api','demo-project'])
  )
```

### Indexes
- `documents_project_idx`: Fast filtering by project
- `documents_active_idx`: Fast filtering of non-deleted docs
- `documents_source_unique`: Prevents duplicate Notion pages/uploads

---

## Table 5: `chunks`

**Purpose:** The actual searchable content. Documents AND handovers are split into chunks, each with an embedding.

| Column | Type | Description |
|--------|------|-------------|
| `chunk_id` | BIGSERIAL | Primary key |
| `doc_id` | BIGINT | Foreign key → `documents` (nullable) |
| `handover_id` | BIGINT | Foreign key → `handovers` (nullable) |
| `heading_path` | TEXT[] | Breadcrumb trail: `['Handover', 'Runbook', 'Incidents']` |
| `order_in_doc` | INT | Position in doc/handover (1, 2, 3...) |
| `page` | INT | For PDFs; null for Notion/handovers |
| `text` | TEXT | Actual chunk content (300-700 tokens) |
| `embedding` | VECTOR(1024) | 1024-dim vector from Cohere |
| `updated_at` | TIMESTAMPTZ | When embedded |

**IMPORTANT:** Each chunk belongs to EITHER a document OR a handover:
- `(doc_id IS NOT NULL AND handover_id IS NULL)` → Document chunk
- `(doc_id IS NULL AND handover_id IS NOT NULL)` → Handover chunk
- Enforced by constraint: `chunks_source_check`

### Example Data
```sql
chunk_id | doc_id | handover_id | heading_path              | text                                    | embedding
---------|--------|-------------|---------------------------|------------------------------------------|----------
1        | 1      | NULL        | ['Deployment', 'Steps']   | "To deploy Atlas API: 1. Run make..." | [0.023, -0.15, ...]
2        | 1      | NULL        | ['Deployment', 'Steps']   | "After deployment, verify health..."  | [0.091, 0.34, ...]
3        | 2      | NULL        | ['Benefits', 'Health']    | "Full-time employees get dental..."   | [-0.12, 0.07, ...]
4        | NULL   | 5           | ['Handover', 'Atlas API'] | "Atlas Handover: Current status..."   | [0.18, -0.22, ...]
```

**Why chunks exist:**
- LLMs have token limits → can't send entire 50-page doc
- Chunking = sending only relevant paragraphs
- Each chunk gets embedded once (offline), then searched at query time

### When It's Used (UNION pattern)
```python
# User asks: "How do I deploy Atlas?"
# 1. Embed the query
qvec = embed_query("How do I deploy Atlas?")  # Returns [0.12, -0.08, ...]

# 2. Find similar chunks from BOTH documents AND handovers
chunks = db.execute("""
    (
        -- Documents user can access
        SELECT c.text, d.title, d.uri, 'document' as source_type
        FROM chunks c
        JOIN documents d ON d.doc_id = c.doc_id
        WHERE c.doc_id IS NOT NULL
          AND d.deleted_at IS NULL
          AND (d.visibility = 'Public' OR d.project_id = ANY($2))
    )
    UNION ALL
    (
        -- Handovers user is involved in
        SELECT c.text, h.title, 'handover://' || h.handover_id as uri, 'handover' as source_type
        FROM chunks c
        JOIN handovers h ON h.handover_id = c.handover_id
        WHERE c.handover_id IS NOT NULL
          AND (h.from_employee_id = $3
               OR h.to_employee_id = $3
               OR $3 = ANY(h.cc_employee_ids))
    )
    ORDER BY embedding <=> $1::vector
    LIMIT 200
""", (qvec, ['atlas-api', 'demo-project'], user_id))

# 3. Rerank and send top chunks to LLM
answer = call_llm("How do I deploy Atlas?", top_12_chunks)
```

### Indexes
- `chunks_embedding_hnsw`: Fast approximate nearest neighbor search using HNSW algorithm
- `chunks_doc_idx`: Fast filtering by document
- `chunks_handover_idx`: Fast filtering by handover

---

## Table 6: `handovers`

**Purpose:** Employee knowledge transfer records. Searchable and private.

| Column | Type | Description |
|--------|------|-------------|
| `handover_id` | BIGSERIAL | Primary key |
| `from_employee_id` | UUID | Sender (FK → employees) |
| `to_employee_id` | UUID | Recipient (FK → employees) |
| `cc_employee_ids` | UUID[] | Optional CC list (managers, stakeholders) |
| `project_id` | TEXT | Optional project reference |
| `title` | TEXT | "Atlas API Handover" |
| `context` | TEXT | Why this handover exists |
| `current_status` | TEXT | What's been done |
| `next_steps` | JSONB | Array of tasks: `[{"task": "...", "done": false}]` |
| `resources` | JSONB | Links: `[{"type": "doc", "doc_id": 123, "title": "..."}]` |
| `contacts` | JSONB | `[{"name": "John", "email": "...", "role": "..."}]` |
| `additional_notes` | TEXT | Free-form notes |
| `status` | TEXT | 'pending', 'acknowledged', or 'completed' |
| `created_at` | TIMESTAMPTZ | When created |
| `acknowledged_at` | TIMESTAMPTZ | When recipient acknowledged |
| `completed_at` | TIMESTAMPTZ | When work completed |

### Example Data
```sql
handover_id | from_employee_id                      | to_employee_id                        | title                | status        | created_at
------------|---------------------------------------|---------------------------------------|----------------------|---------------|------------------
5           | 550e8400-e29b-41d4-a716-446655440000 | 6ba7b810-9dad-11d1-80b4-00c04fd430c8 | Atlas API Handover   | acknowledged  | 2025-10-05 10:00
6           | 6ba7b810-9dad-11d1-80b4-00c04fd430c8 | 770e8400-e29b-41d4-a716-446655440002 | Phoenix Setup        | pending       | 2025-10-06 14:30
```

### Access Control (PRIVATE)

**Rule:** User can see handover IF:
- User is sender (`from_employee_id`), OR
- User is recipient (`to_employee_id`), OR
- User is CC'd (`user IN cc_employee_ids`)

**Unlike documents (project-based), handovers are person-to-person.**

### When It's Used

**Creation (automatic embedding):**
```python
# User creates handover via POST /api/handovers
# Backend:
1. Inserts handover record into database
2. Constructs searchable text:
   text = f"""
   Title: {title}
   Context: {context}
   Current Status: {current_status}
   Next Steps: {', '.join(step['task'] for step in next_steps)}
   Additional Notes: {additional_notes}
   """
3. Chunks text (300-700 tokens)
4. Embeds each chunk with Cohere
5. Inserts chunks with handover_id (doc_id=NULL)
```

**Retrieval (included in search):**
```sql
-- Search includes handover chunks if user is involved
WHERE c.handover_id IS NOT NULL
  AND (h.from_employee_id = $user_id
       OR h.to_employee_id = $user_id
       OR $user_id = ANY(h.cc_employee_ids))
```

### Lifecycle
```
Created (status='pending')
  ↓
Recipient acknowledges (status='acknowledged', acknowledged_at set)
  ↓
Work completed (status='completed', completed_at set)
```

### Indexes
- `handovers_from_idx`: Fast filtering by sender
- `handovers_to_idx`: Fast filtering by recipient
- `handovers_status_idx`: Fast filtering by status
- `handovers_project_idx`: Fast filtering by project
- `handovers_created_idx`: Sort by creation date

---

## Table 7: `audit_queries`

**Purpose:** Log every search for debugging, compliance, and analytics.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `user_id` | UUID | Who asked |
| `query` | TEXT | What they asked |
| `used_doc_ids` | BIGINT[] | Which docs contributed to answer |
| `used_handover_ids` | BIGINT[] | Which handovers contributed to answer |
| `created_at` | TIMESTAMPTZ | When |

### Example Data
```sql
id | user_id                              | query                          | used_doc_ids | used_handover_ids | created_at
---|--------------------------------------|--------------------------------|--------------|-------------------|------------------
1  | 550e8400-e29b-41d4-a716-446655440000| How do I deploy Atlas API?     | {1, 5}       | {10}              | 2025-10-03 14:32
2  | 6ba7b810-9dad-11d1-80b4-00c04fd430c8| What are our dental benefits?  | {2}          | NULL              | 2025-10-03 15:18
3  | 550e8400-e29b-41d4-a716-446655440000| Phoenix setup steps?           | {8, 12}      | {6}               | 2025-10-03 16:45
```

### When It's Used
```python
# After answering user's question:
audit_log(
    user_id=user_id,
    query=query,
    used_doc_ids=[1, 5],
    used_handover_ids=[10]
)

# Later for analytics:
# - Which docs/handovers are most useful?
SELECT doc_id, COUNT(*) as usage_count
FROM audit_queries, unnest(used_doc_ids) AS doc_id
GROUP BY doc_id ORDER BY usage_count DESC;

# - What is Sarah searching for?
SELECT query, created_at
FROM audit_queries
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY created_at DESC LIMIT 10;
```

---

## Complete Access Control Flow

### Scenario: Sarah asks "How do I deploy Atlas?"

```
1. Sarah logs in
   → Supabase Auth returns JWT with uid = 550e8400-...

2. Frontend calls: POST /api/search
   Headers: { Authorization: "Bearer <JWT>" }
   Body: { query: "How do I deploy Atlas?", top_k: 12 }

3. Backend verifies JWT
   → Extracts employee_id = 550e8400-...

4. Backend loads Sarah's projects:
   SELECT project_id FROM employee_projects
   WHERE employee_id = '550e8400-...'
   → Result: ['atlas-api', 'demo-project']

5. Backend embeds query:
   qvec = embed_query("How do I deploy Atlas?")
   → Returns [0.12, -0.08, 0.34, ...] (1024-dim)

6. Backend runs vector search with DUAL ACL:
   (
     -- Document chunks (project-based access)
     SELECT c.text, d.title, d.uri, 'document' as source_type
     FROM chunks c
     JOIN documents d ON d.doc_id = c.doc_id
     WHERE c.doc_id IS NOT NULL
       AND d.deleted_at IS NULL
       AND (
         d.visibility = 'Public'                          -- Public docs
         OR d.project_id = ANY(['atlas-api','demo-project']) -- Sarah's projects
       )
   )
   UNION ALL
   (
     -- Handover chunks (person-based access)
     SELECT c.text, h.title, 'handover://' || h.handover_id as uri, 'handover' as source_type
     FROM chunks c
     JOIN handovers h ON h.handover_id = c.handover_id
     WHERE c.handover_id IS NOT NULL
       AND (
         h.from_employee_id = '550e8400-...'       -- Sarah sent it
         OR h.to_employee_id = '550e8400-...'      -- Sarah received it
         OR '550e8400-...' = ANY(h.cc_employee_ids) -- Sarah was CC'd
       )
   )
   ORDER BY embedding <=> qvec
   LIMIT 200

   → Returns chunks from:
     ✓ Doc 1 (Atlas Deploy Guide) - Sarah is in atlas-api project
     ✓ Doc 2 (Company Handbook) - Public
     ✓ Handover 10 (Atlas Handover) - Sarah is recipient
     ✗ Doc 3 (Phoenix Design Guide) - Sarah not in phoenix-ui
     ✗ Handover 15 (Bolt Handover) - Sarah not involved

7. Backend reranks with Cohere:
   top_12 = cohere.rerank(query, candidate_chunks[:200])

8. Backend sends filtered chunks to LLM:
   answer = groq.call_llm(query, top_12)

9. Backend logs to audit:
   INSERT INTO audit_queries (user_id, query, used_doc_ids, used_handover_ids)
   VALUES ('550e8400-...', 'How do I deploy Atlas?', [1, 2], [10])

10. Backend returns to frontend:
   {
     "answer": "To deploy Atlas API: 1. Run make deploy...",
     "chunks": [
       { "doc_id": 1, "handover_id": null, "title": "Atlas Deploy Guide", "source_type": "document", ... },
       { "doc_id": null, "handover_id": 10, "title": "Atlas Handover", "source_type": "handover", ... }
     ],
     "used_doc_ids": [1, 2],
     "used_handover_ids": [10]
   }
```

**Key takeaway:** Search seamlessly combines documents (project-based ACL) + handovers (person-based ACL).

---

## Common Queries

### Check user's access

```sql
-- What projects can Sarah see?
SELECT p.name
FROM employee_projects ep
JOIN projects p ON p.project_id = ep.project_id
WHERE ep.employee_id = '550e8400-e29b-41d4-a716-446655440000';

-- What handovers can Sarah see?
SELECT h.handover_id, h.title, h.status,
       from_emp.display_name as sender,
       to_emp.display_name as recipient
FROM handovers h
LEFT JOIN employees from_emp ON h.from_employee_id = from_emp.employee_id
LEFT JOIN employees to_emp ON h.to_employee_id = to_emp.employee_id
WHERE h.from_employee_id = '550e8400-...'
   OR h.to_employee_id = '550e8400-...'
   OR '550e8400-...' = ANY(h.cc_employee_ids)
ORDER BY h.created_at DESC;
```

### Find all content in a project

```sql
-- All atlas-api documents
SELECT title, visibility, uri
FROM documents
WHERE project_id = 'atlas-api'
  AND deleted_at IS NULL;

-- All handovers for atlas-api project
SELECT h.handover_id, h.title, h.status,
       from_emp.display_name as sender,
       to_emp.display_name as recipient
FROM handovers h
LEFT JOIN employees from_emp ON h.from_employee_id = from_emp.employee_id
LEFT JOIN employees to_emp ON h.to_employee_id = to_emp.employee_id
WHERE h.project_id = 'atlas-api'
ORDER BY h.created_at DESC;
```

### See what got embedded today

```sql
-- Recently ingested chunks (documents + handovers)
SELECT
  COALESCE(d.title, h.title) as title,
  CASE
    WHEN c.doc_id IS NOT NULL THEN 'document'
    ELSE 'handover'
  END as source_type,
  COUNT(c.chunk_id) as num_chunks
FROM chunks c
LEFT JOIN documents d ON d.doc_id = c.doc_id
LEFT JOIN handovers h ON h.handover_id = c.handover_id
WHERE c.updated_at > current_date
GROUP BY COALESCE(d.title, h.title), source_type;
```

### Debug a bad answer

```sql
-- User complained about answer, find what we used
SELECT
  aq.query,
  COALESCE(d.title, h.title) as source_title,
  CASE WHEN d.doc_id IS NOT NULL THEN 'document' ELSE 'handover' END as source_type,
  COALESCE(d.uri, 'handover://' || h.handover_id) as uri
FROM audit_queries aq
LEFT JOIN unnest(aq.used_doc_ids) AS doc_id ON true
LEFT JOIN unnest(aq.used_handover_ids) AS handover_id ON true
LEFT JOIN documents d ON d.doc_id = doc_id
LEFT JOIN handovers h ON h.handover_id = handover_id
WHERE aq.id = 42;  -- The audit log ID
```

### Check handover lifecycle

```sql
-- Pending handovers (need acknowledgement)
SELECT h.handover_id, h.title,
       from_emp.display_name as sender,
       to_emp.display_name as recipient,
       h.created_at
FROM handovers h
LEFT JOIN employees from_emp ON h.from_employee_id = from_emp.employee_id
LEFT JOIN employees to_emp ON h.to_employee_id = to_emp.employee_id
WHERE h.status = 'pending'
ORDER BY h.created_at DESC;

-- Average time to acknowledge
SELECT AVG(acknowledged_at - created_at) as avg_ack_time
FROM handovers
WHERE acknowledged_at IS NOT NULL;

-- Average time to complete
SELECT AVG(completed_at - created_at) as avg_completion_time
FROM handovers
WHERE completed_at IS NOT NULL;
```

---

## Migration Strategy

### Initial Setup

**Step 1: Run Base Migration**
```sql
-- In Supabase Dashboard → SQL Editor
-- Run entire file: supabase/migrations/20251002234351_updated_db.sql
-- Creates: employees, projects, employee_projects, documents, chunks, audit_queries
```

**Step 2: Run Handovers Migration**
```sql
-- Run entire file: supabase/migrations/20251007000000_add_handovers.sql
-- Creates: handovers table
-- Updates: chunks table (adds handover_id, makes doc_id nullable)
```

**Step 3: Fix Source External ID**
```sql
-- Run entire file: supabase/migrations/20251007_fix_source_external_id.sql
-- Fixes: source_external_id uniqueness for Notion pages
```

**Step 4: Seed Test Data**
```sql
-- Run entire file: supabase/seed.sql
-- Creates test employees, projects, and assignments
```

### Verification

```sql
-- Check all tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Expected output:
-- audit_queries
-- chunks
-- documents
-- employee_projects
-- employees
-- handovers
-- projects

-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check indexes exist
SELECT indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY indexname;
```

---

## Troubleshooting

### "User can't see documents they should have access to"

```sql
-- 1. Check if user exists
SELECT * FROM employees WHERE email = 'user@company.com';

-- 2. Check their projects
SELECT project_id, role FROM employee_projects WHERE employee_id = 'their-uuid';

-- 3. Check document visibility
SELECT doc_id, title, project_id, visibility
FROM documents
WHERE deleted_at IS NULL;

-- 4. Test access query manually
SELECT d.title
FROM documents d
WHERE d.deleted_at IS NULL
  AND (d.visibility = 'Public' OR d.project_id = ANY(ARRAY['atlas-api','demo-project']))
```

### "User can't see handovers"

```sql
-- 1. Check if handover exists
SELECT * FROM handovers WHERE handover_id = 123;

-- 2. Check user involvement
SELECT h.handover_id, h.title,
       h.from_employee_id = 'user-uuid' as is_sender,
       h.to_employee_id = 'user-uuid' as is_recipient,
       'user-uuid' = ANY(h.cc_employee_ids) as is_cced
FROM handovers h
WHERE h.handover_id = 123;

-- 3. Test handover access query manually
SELECT h.title
FROM handovers h
WHERE h.from_employee_id = 'user-uuid'
   OR h.to_employee_id = 'user-uuid'
   OR 'user-uuid' = ANY(h.cc_employee_ids);
```

### "Chunks not returning in search"

```sql
-- 1. Check chunks exist
SELECT COUNT(*) as total_chunks,
       SUM(CASE WHEN doc_id IS NOT NULL THEN 1 ELSE 0 END) as doc_chunks,
       SUM(CASE WHEN handover_id IS NOT NULL THEN 1 ELSE 0 END) as handover_chunks
FROM chunks;

-- 2. Check embedding dimension matches
SELECT pg_typeof(embedding), vector_dims(embedding)
FROM chunks LIMIT 1;
-- Should be: vector, 1024 (Cohere v3)

-- 3. Test vector search manually (requires actual embedding vector)
SELECT
  COALESCE(d.title, h.title) as title,
  c.text,
  1 - (c.embedding <=> '[0.1, 0.2, ...]'::vector) AS score
FROM chunks c
LEFT JOIN documents d ON d.doc_id = c.doc_id
LEFT JOIN handovers h ON h.handover_id = c.handover_id
ORDER BY c.embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

### "Handover chunks not being created"

```sql
-- 1. Check if handover was created
SELECT * FROM handovers WHERE handover_id = 123;

-- 2. Check if chunks were generated
SELECT COUNT(*) FROM chunks WHERE handover_id = 123;

-- 3. If no chunks exist, check backend logs
-- Backend should log when creating handover chunks
-- Look for: "Embedding handover chunks..." in logs
```

### "Constraint violation on chunks"

```sql
-- Error: "duplicate key value violates unique constraint"
-- Reason: chunks_source_check constraint ensures:
-- - Either doc_id OR handover_id is set (not both, not neither)

-- Check constraint:
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'chunks'::regclass
  AND conname = 'chunks_source_check';

-- Valid chunk examples:
INSERT INTO chunks (doc_id, handover_id, ...) VALUES (123, NULL, ...);    -- ✓ Document chunk
INSERT INTO chunks (doc_id, handover_id, ...) VALUES (NULL, 456, ...);    -- ✓ Handover chunk
INSERT INTO chunks (doc_id, handover_id, ...) VALUES (123, 456, ...);     -- ✗ Both set (invalid)
INSERT INTO chunks (doc_id, handover_id, ...) VALUES (NULL, NULL, ...);   -- ✗ Neither set (invalid)
```

### "Ingestion fails with duplicate source_external_id"

```sql
-- Check for duplicate sources
SELECT source_external_id, COUNT(*)
FROM documents
GROUP BY source_external_id
HAVING COUNT(*) > 1;

-- Fix duplicates (keep most recent)
DELETE FROM documents a USING documents b
WHERE a.doc_id > b.doc_id
  AND a.source_external_id = b.source_external_id;
```

---

## Performance Optimization

### Index Usage

```sql
-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Unused indexes (consider dropping)
SELECT schemaname, tablename, indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public';
```

### Query Performance

```sql
-- Analyze a slow query
EXPLAIN ANALYZE
SELECT c.text, d.title
FROM chunks c
JOIN documents d ON d.doc_id = c.doc_id
WHERE d.visibility = 'Public'
ORDER BY c.embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 12;

-- Check HNSW index is being used
-- Look for: "Index Scan using chunks_embedding_hnsw_idx"
```

### Table Sizes

```sql
-- Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Security Best Practices

1. **Never expose `chunks` table directly** — Always join with `documents` or `handovers` to enforce ACL
2. **Use parameterized queries** — Prevent SQL injection (`$1`, `$2`, not string concatenation)
3. **Soft delete only** — Never hard delete documents/handovers (use `deleted_at`)
4. **Audit everything** — Every search should write to `audit_queries`
5. **Validate JWT on every request** — Never trust client-provided user IDs

---

## Summary

**Document Flow:**
```
Notion Page → Worker → chunks(doc_id=X, handover_id=NULL)
User searches → UNION query → chunks filtered by project access
```

**Handover Flow:**
```
User creates handover → Backend → chunks(doc_id=NULL, handover_id=Y)
User searches → UNION query → chunks filtered by sender/recipient/CC
```

**Search combines both:**
- Documents: project-based ACL (`project_id IN user.projects`)
- Handovers: person-based ACL (`user IN [sender, recipient, CC]`)
- Result: Unified RAG answer with citations from both sources

---

**Ready to start? Run the migrations in order, seed test data, and start ingesting!**
