# Database Schema Guide

## Overview

Our knowledge hub uses **5 tables** to manage permissions, documents, and search:

```
employees ──┐
            ├──→ employee_projects ──→ projects
            │                             ↓
            └──→ audit_queries      documents ──→ chunks
```

**Core idea:** Users belong to projects → Documents belong to projects → We only retrieve chunks from documents the user can access.

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
- To log searches in `audit_queries`

---

## Table 2: `projects`

**Purpose:** Define access boundaries for private documents.

| Column | Type | Description |
|--------|------|-------------|
| `project_id` | TEXT | Human-readable ID (e.g., 'Atlas') |
| `name` | TEXT | Display name |

### Example Data
```sql
project_id | name
-----------|------------------
Atlas      | Atlas Platform
Bolt       | Bolt Mobile App
Phoenix    | Phoenix Redesign
```

### When It's Used
- Documents are assigned to projects via `documents.project_id`
- Users are granted access via `employee_projects`
- Retrieval filters by user's projects

---

## Table 3: `employee_projects`

**Purpose:** Many-to-many junction table. Controls who sees private docs.

| Column | Type | Description |
|--------|------|-------------|
| `employee_id` | UUID | Foreign key → `employees` |
| `project_id` | TEXT | Foreign key → `projects` |
| `role` | TEXT | Optional: 'viewer', 'editor', 'owner' |

### Example Data
```sql
employee_id                           | project_id | role
--------------------------------------|------------|--------
550e8400-e29b-41d4-a716-446655440000 | Atlas      | editor
550e8400-e29b-41d4-a716-446655440000 | Phoenix    | viewer
6ba7b810-9dad-11d1-80b4-00c04fd430c8 | Atlas      | owner
```

**Translation:**
- Sarah can see Atlas (editor) and Phoenix (viewer) private docs
- John can see Atlas (owner) private docs

### When It's Used
```python
# In /api/search, we load user's projects:
projects = db.execute("""
    SELECT project_id 
    FROM employee_projects 
    WHERE employee_id = %s
""", (user_id,))
# Result: ['Atlas', 'Phoenix']
```

---

## Table 4: `documents`

**Purpose:** One row per Notion page (or future file). Metadata only, no content.

| Column | Type | Description |
|--------|------|-------------|
| `doc_id` | BIGSERIAL | Primary key |
| `title` | TEXT | "Atlas Deploy Guide" |
| `project_id` | TEXT | Which project owns this (nullable for Public) |
| `visibility` | TEXT | 'Public' or 'Private' |
| `uri` | TEXT | Deep link back to Notion page |
| `language` | TEXT | Optional: 'en', 'ar' |
| `updated_at` | TIMESTAMPTZ | When content last changed |
| `deleted_at` | TIMESTAMPTZ | Soft delete (null = active) |
| `source_external_id` | TEXT | Notion page ID (for upserts) |
| `content_hash` | TEXT | MD5 of markdown (skip re-embed if unchanged) |

### Example Data
```sql
doc_id | title                  | project_id | visibility | uri                          | deleted_at | source_external_id     | content_hash
-------|------------------------|------------|------------|------------------------------|------------|------------------------|-------------
1      | Atlas Deploy Guide     | Atlas      | Private    | https://notion.so/abc123     | NULL       | notion_abc123          | d8e8fca2dc...
2      | Company Handbook       | NULL       | Public     | https://notion.so/def456     | NULL       | notion_def456          | 9b74c9897b...
3      | Bolt API Docs          | Bolt       | Private    | https://notion.so/ghi789     | NULL       | notion_ghi789          | 7f3d4e5a1c...
4      | Old Runbook (deleted)  | Atlas      | Private    | https://notion.so/jkl012     | 2025-09-15 | notion_jkl012          | a1b2c3d4e5...
```

**Access rules:**
- Doc 1 (Atlas Deploy Guide): Only users in Atlas project can see it
- Doc 2 (Company Handbook): Everyone can see it (Public)
- Doc 3 (Bolt API Docs): Only users in Bolt project can see it
- Doc 4: Ignored (deleted_at is not null)

### When It's Used
```sql
-- Retrieval query checks access:
WHERE d.deleted_at IS NULL
  AND (
    d.visibility = 'Public'
    OR d.project_id = ANY(string_to_array('Atlas,Phoenix', ','))
  )
```

### Indexes Explained
- `documents_project_idx`: Fast filtering by project
- `documents_active_idx`: Fast filtering of non-deleted docs
- `documents_source_unique`: Prevents duplicate Notion pages

---

## Table 5: `chunks`

**Purpose:** The actual searchable content. Documents are split into chunks, each with an embedding.

| Column | Type | Description |
|--------|------|-------------|
| `chunk_id` | BIGSERIAL | Primary key |
| `doc_id` | BIGINT | Foreign key → `documents` |
| `heading_path` | TEXT[] | Breadcrumb trail: `['Handover', 'Runbook', 'Incidents']` |
| `order_in_doc` | INT | Position in doc (1, 2, 3...) for stitching |
| `page` | INT | For PDFs; null for Notion |
| `text` | TEXT | Actual chunk content (300-700 tokens) |
| `embedding` | VECTOR(1536) | 1536-dim vector from OpenAI/Cohere |
| `updated_at` | TIMESTAMPTZ | When embedded |

### Example Data
```sql
chunk_id | doc_id | heading_path              | order_in_doc | text                                    | embedding
---------|--------|---------------------------|--------------|------------------------------------------|----------
1        | 1      | ['Deployment', 'Steps']   | 1            | "To deploy Atlas API: 1. Run make..." | [0.023, -0.15, ...]
2        | 1      | ['Deployment', 'Steps']   | 2            | "After deployment, verify health..."  | [0.091, 0.34, ...]
3        | 2      | ['Benefits', 'Health']    | 1            | "Full-time employees get dental..."   | [-0.12, 0.07, ...]
4        | 3      | ['Authentication']        | 1            | "Bolt API uses JWT tokens. To..."     | [0.18, -0.22, ...]
```

**Why chunks exist:**
- LLMs have token limits → can't send entire 50-page doc
- Chunking = sending only relevant paragraphs
- Each chunk gets embedded once (offline), then searched at query time

### When It's Used
```python
# User asks: "How do I deploy Atlas?"
# 1. Embed the query
qvec = embed_query("How do I deploy Atlas?")  # Returns [0.12, -0.08, ...]

# 2. Find similar chunks (only from docs user can access)
chunks = db.execute("""
    SELECT c.text, d.title, d.uri,
           1 - (c.embedding <=> %s::vector) AS score
    FROM chunks c
    JOIN documents d ON d.doc_id = c.doc_id
    WHERE d.deleted_at IS NULL
      AND (d.visibility = 'Public' OR d.project_id = ANY(%s))
    ORDER BY c.embedding <=> %s::vector
    LIMIT 12
""", (qvec, ['Atlas', 'Phoenix'], qvec))

# 3. Send top chunks to LLM
answer = call_llm("How do I deploy Atlas?", [chunk['text'] for chunk in chunks])
```

### Indexes Explained
- `chunks_embedding_hnsw`: Fast approximate nearest neighbor search using HNSW algorithm
- `chunks_doc_order_unique`: Prevents duplicate chunks, enables upserts

---

## Table 6: `audit_queries`

**Purpose:** Log every search for debugging, compliance, and analytics.

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Primary key |
| `user_id` | UUID | Who asked |
| `query` | TEXT | What they asked |
| `used_doc_ids` | BIGINT[] | Which docs contributed to answer |
| `created_at` | TIMESTAMPTZ | When |

### Example Data
```sql
id | user_id                              | query                          | used_doc_ids | created_at
---|--------------------------------------|--------------------------------|--------------|------------------
1  | 550e8400-e29b-41d4-a716-446655440000| How do I deploy Atlas API?     | {1, 5}       | 2025-10-03 14:32
2  | 6ba7b810-9dad-11d1-80b4-00c04fd430c8| What are our dental benefits?  | {2}          | 2025-10-03 15:18
3  | 550e8400-e29b-41d4-a716-446655440000| Who is on-call this week?      | {8, 12}      | 2025-10-03 16:45
```

### When It's Used
```python
# After answering user's question:
audit_log(user_id, query, used_doc_ids=[1, 5])

# Later for analytics:
# - Which docs are most useful?
SELECT doc_id, COUNT(*) 
FROM audit_queries, unnest(used_doc_ids) AS doc_id
GROUP BY doc_id ORDER BY COUNT(*) DESC;

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
   → Result: ['Atlas', 'Phoenix']

5. Backend embeds query:
   qvec = embed_query("How do I deploy Atlas?")

6. Backend runs vector search with ACL:
   SELECT c.text, d.title, d.uri
   FROM chunks c
   JOIN documents d ON d.doc_id = c.doc_id
   WHERE d.deleted_at IS NULL
     AND (
       d.visibility = 'Public'                    -- Allow public docs
       OR d.project_id = ANY(['Atlas','Phoenix']) -- Allow Sarah's projects
     )
   ORDER BY c.embedding <=> qvec
   LIMIT 12
   
   → Returns chunks from:
     - Doc 1 (Atlas Deploy Guide) ✓ Sarah is in Atlas
     - Doc 2 (Company Handbook) ✓ Public
     - NOT Doc 3 (Bolt API Docs) ✗ Sarah not in Bolt

7. Backend sends filtered chunks to LLM:
   answer = call_llm(query, filtered_chunks)

8. Backend logs to audit:
   INSERT INTO audit_queries (user_id, query, used_doc_ids)
   VALUES ('550e8400-...', 'How do I deploy Atlas?', [1, 2])

9. Backend returns to frontend:
   {
     "answer": "To deploy Atlas API: 1. Run make deploy...",
     "chunks": [
       { "doc_id": 1, "title": "Atlas Deploy Guide", "snippet": "...", "uri": "..." },
       { "doc_id": 2, "title": "Company Handbook", "snippet": "...", "uri": "..." }
     ]
   }
```

---

## Common Queries for Your Team

### Check user's access
```sql
-- What projects can Sarah see?
SELECT p.name 
FROM employee_projects ep
JOIN projects p ON p.project_id = ep.project_id
WHERE ep.employee_id = '550e8400-e29b-41d4-a716-446655440000';
```

### Find all docs in a project
```sql
-- All Atlas documents
SELECT title, visibility, uri 
FROM documents 
WHERE project_id = 'Atlas' 
  AND deleted_at IS NULL;
```

### See what got embedded today
```sql
-- Recently ingested chunks
SELECT d.title, COUNT(c.chunk_id) as num_chunks
FROM chunks c
JOIN documents d ON d.doc_id = c.doc_id
WHERE c.updated_at > current_date
GROUP BY d.title;
```

### Debug a bad answer
```sql
-- User complained about answer, find what we used
SELECT aq.query, d.title, d.uri
FROM audit_queries aq
CROSS JOIN unnest(aq.used_doc_ids) AS doc_id
JOIN documents d ON d.doc_id = doc_id
WHERE aq.id = 42;  -- The audit log ID
```

---

## Migration Strategy

### Initial Setup
```bash
# 1. Apply schema
npx supabase db push

# 2. Seed test data
INSERT INTO projects VALUES ('Atlas', 'Atlas Platform');
INSERT INTO employees VALUES ('your-supabase-uid', 'you@company.com', 'Your Name');
INSERT INTO employee_projects VALUES ('your-supabase-uid', 'Atlas', 'owner');
```

### After Ingesting Your First Notion Page
```sql
-- Verify it worked
SELECT d.title, COUNT(c.chunk_id) as chunks
FROM documents d
LEFT JOIN chunks c ON c.doc_id = d.doc_id
GROUP BY d.doc_id, d.title;

-- Expected output:
-- title                | chunks
-- ---------------------|-------
-- Atlas Deploy Guide   | 8
```

---

## Troubleshooting

### "User can't see documents they should have access to"
```sql
-- 1. Check if user exists
SELECT * FROM employees WHERE email = 'user@company.com';

-- 2. Check their projects
SELECT project_id FROM employee_projects WHERE employee_id = 'their-uuid';

-- 3. Check document visibility
SELECT doc_id, title, project_id, visibility 
FROM documents 
WHERE deleted_at IS NULL;

-- 4. Verify access logic
-- Public docs: everyone sees
-- Private docs: user must be in that project
```

### "Chunks not returning in search"
```sql
-- 1. Check chunks exist
SELECT COUNT(*) FROM chunks WHERE doc_id = 123;

-- 2. Check embedding dimension matches
SELECT pg_typeof(embedding), vector_dims(embedding) 
FROM chunks LIMIT 1;
-- Should be: vector, 1536 (or your model's dim)

-- 3. Test vector search manually
SELECT chunk_id, text, 
       1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS score
FROM chunks 
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector 
LIMIT 5;
```

### "Ingestion fails with duplicate key error"
```sql
-- If you get unique constraint violation on chunks:
-- Your chunker is producing non-stable order_in_doc values
-- Fix: Make chunker deterministic, then clean duplicates:

DELETE FROM chunks a USING chunks b
WHERE a.chunk_id > b.chunk_id 
  AND a.doc_id = b.doc_id 
  AND a.order_in_doc = b.order_in_doc;
```