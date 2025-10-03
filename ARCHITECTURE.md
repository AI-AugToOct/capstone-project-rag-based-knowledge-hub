# RAG Knowledge Hub – Architecture

Version: 0.3
Last Updated: 2025-10-03

> Internal architecture reference for core retrieval and ingestion flows. Concise and implementation-focused.

---
## 1. High-Level Concept
A permission‑aware Retrieval Augmented Generation (RAG) platform for internal knowledge.

Core Idea:
1. Ingest internal sources (initially Notion) into a unified store
2. Normalize → chunk → embed → store vectors in Postgres (pgvector)
3. At query time: authenticate → enforce project-based ACL → semantic retrieve (ANN) → rerank → LLM answer with citations → audit
4. Guarantee: Users only see Public documents OR documents tied to projects they belong to.

Why RAG (vs pure LLM):
- Grounded answers with explicit source snippets
- Citations build trust + allow verification
- Access control enforced at retrieval layer (no leak via prompt context)

Security Invariant:
"No content leaves the database layer unless ACL condition passes: visibility = 'Public' OR project_id IN user_projects."

---
## 2. Core Components (Detailed)
| Component | Responsibility | Key Interactions |
|-----------|----------------|------------------|
| Frontend (Next.js) | Chat/search UI, auth session management, render answers + citations | Calls `/api/search` with JWT; displays sources; handles login/signup via Supabase SDK |
| Backend API (FastAPI) | Orchestrates per-query RAG pipeline | Verifies JWT → DB (projects) → Cohere (embed + rerank) → Postgres (vector search) → Groq (LLM) → DB (audit) |
| Ingestion Workers | Periodic content sync from Notion | Notion API → normalize → chunk → embed → upsert tables |
| Postgres + pgvector | Source of truth for metadata, ACL, chunks, embeddings, audit trail | Queried by retrieval + updated by workers |
| Auth (Supabase) | Issues JWT with user UUID (employee_id) | Frontend obtains JWT; backend verifies signature/claims |
| Embedding Service (Cohere) | Converts text to dense vectors (query + document spaces) | Query: input_type=search_query; Document: input_type=search_document |
| Reranker (Cohere rerank-v3) | Relevance refinement on candidate chunks | Takes top N raw ANN results → returns top K ranked |
| LLM (Groq) | Synthesizes final answer from retrieved context | Structured prompt with numbered chunks |
| Audit Logging | Records which docs were used per query | Insert into audit_queries |

Responsibilities Clarified:
- Backend derives user projects from DB (never trusts client claims).
- Workers are idempotent (content hash gate).
- Embedding model + dimension must match between ingestion and query.

---
## 4. End-to-End Query Flow
```
Browser → POST /api/search (Authorization: Bearer <jwt>, body: {query, top_k?})
 1. Verify JWT → employee_id
 2. Load user project_ids (employee_projects)
 3. Embed query (Cohere embed-english-v3.0, search_query)
 4. Vector search (pgvector ANN) with ACL filter:
      visibility='Public' OR project_id IN user_projects
 5. Rerank candidates (Cohere rerank-v3) → top K (e.g. 12)
 6. LLM generation (Groq) with structured context
 7. Post-process citations (ensure only valid chunk indices)
 8. Async audit log (user_id, query, used_doc_ids[])
 9. Return JSON { answer, chunks, used_doc_ids }
```
Failure Handling (minimal):
- Rerank failure → use ANN order
- LLM failure → return chunks with answer=null + error flag
- Audit failure → log warning only

---
## 5. Ingestion Pipeline (Notion Source)
```
List pages → fetch blocks → normalize (Markdown)
  → hash compare → skip unchanged
  → chunk (300–700 tokens, slight overlap)
  → embed (Cohere search_document)
  → upsert documents
  → upsert chunks (with vectors)
  → soft-delete missing (set deleted_at)
```
Idempotency:
- `source_external_id` + `content_hash`

Chunking Notes:
- Maintain heading_path for hierarchy
- Slight overlap helps context continuity
- order_in_doc preserves sequence

Failure / Mitigation:
| Issue | Mitigation |
|-------|-----------|
| Notion rate limit | Backoff + small sleep |
| Invalid API key | Fail fast, clear error log |
| Embedding error | Limited retries then skip doc |
| Partial run | Safe due to per-doc upserts |

---
## 6. Logical Architecture Diagram
```
                   +-------------------+
                   |   User Browser    |
                   |  (Next.js UI)     |
                   +---------+---------+
                             | HTTPS (JWT)
                             v
+-------------------+   +----+--------------------+      +-------------------+
| Supabase Auth     |   | FastAPI Backend         |      |  External Services|
| (Identity / JWT)  |   |  /api/search            |      |  - Cohere Embed   |
+---------+---------+   |  /api/docs/:id          |      |  - Cohere Rerank  |
          |             |  /health                |      |  - Groq LLM       |
          |             +----+----------+---------+      |  - Notion API     |
          |                  |          |                +-------------------+
          |        DB Pool   |          | Outbound calls
          |                  |          v
          |                  |   +-------------+
          |                  |   | Retrieval & |
          |                  |   |  Orchestration
          |                  |   +------+------+ 
          |                  |          |
          |                  v          v
          |        +-----------------------------+
          |        | Postgres + pgvector         |
          |        | employees/projects ACL      |
          |        | documents / chunks / audit  |
          |        +--------------+--------------+
          |                       ^
          |                       |
          |             +---------+---------+
          |             | Ingestion Workers |
          |             |  Notion → Chunks  |
          |             |  → Embeddings     |
          |             +-------------------+
```
Legend:
- ACL enforced in the retrieval SQL
- Workers write; backend reads (except audit inserts)

---
## 8. Sequence Diagrams (Text Form)
### 8.1 Search
```
Frontend -> Backend: POST /api/search {query}
Backend -> Auth: verify JWT
Backend -> DB: fetch user projects
Backend -> Cohere: embed(query)
Backend -> DB: ANN vector search (ACL filtered)
Backend -> Cohere: rerank(candidates)
Backend -> Groq: generate(answer)
Backend -> DB: insert audit (async)
Backend -> Frontend: 200 {answer, chunks, used_doc_ids}
```

### 8.2 Ingestion (Notion)
```
Cron -> Worker: ingest run
Worker -> Notion: list pages
Worker -> Notion: fetch blocks
Worker -> Normalizer: blocks -> markdown
Worker -> Hash compare: skip if same
Worker -> Chunker: markdown -> chunks
Worker -> Cohere: embed(batch)
Worker -> DB: upsert document + chunks
Worker -> DB: soft-delete stale (optional)
```

### 8.3 Rerank Down
```
Rerank error → warn → fallback ANN order → continue
```

### 8.4 LLM Down
```
LLM timeout/error → return {answer:null, chunks, error:"GENERATION_FAILED"}
```

---
(End of architecture reference.)
