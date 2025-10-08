# RAG Knowledge Hub with Employee Handovers

> **Enterprise RAG system with permission-aware search, document management, and knowledge handover capabilities.**

[![Next.js](https://img.shields.io/badge/Next.js-15.2-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Platform-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.5+-blue)](https://github.com/pgvector/pgvector)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com/)
[![AWS](https://img.shields.io/badge/AWS-Deployed-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/)

---

## 📖 Overview

**RAG Knowledge Hub** is an intelligent enterprise search platform that combines:
- **Permission-aware vector search** with pgvector and HNSW indexing
- **LLM-powered answers** with citations using Groq (Llama 3.3, Mixtral, ChatGPT-OSS)
- **Employee knowledge handovers** for seamless onboarding and transitions
- **Notion integration** for automated document ingestion
- **Strict access control** based on project memberships and roles

**Think of it as:** "ChatGPT for your company's internal documents" + "Knowledge handover system for employee transitions" — with security and compliance built-in.

### The Problem

- Teams have knowledge scattered across Notion, wikis, and individuals' heads
- When employees leave or transition projects, critical knowledge is lost
- Existing search tools don't understand context or enforce permissions
- Onboarding new team members takes weeks of manual knowledge transfer

### Our Solution

A unified platform that:
1. **Ingests documents** from Notion (PDF/DOCX via upload)
2. **Embeds content** using Cohere (1024-dim vectors)
3. **Searches semantically** with pgvector + Cohere reranking
4. **Generates answers** with LLMs and source citations
5. **Enforces access control** (project-based + handover-based)
6. **Manages handovers** for structured knowledge transfer between employees

---

## ✨ Features

### 🔍 Core RAG Features
- **🔐 Permission-Aware Search** — Users only see documents from their projects + handovers they're involved in
- **🎯 Vector Search** — pgvector with HNSW index (<2s query time on 100K chunks)
- **🤖 LLM-Powered Answers** — Groq inference with Cohere embeddings & reranking
- **📚 Source Citations** — Every answer includes links to source documents
- **📊 Audit Logging** — Track every query for compliance

### 🤝 Employee Handover System
- **📝 Structured Handovers** — Context, current status, next steps, resources, contacts
- **🔒 Private ACL** — Only sender, recipient, and CC'd users can access
- **🔍 Searchable** — Handovers appear in RAG search (embedded automatically)
- **📈 Lifecycle Tracking** — pending → acknowledged → completed
- **📎 Resource Links** — Attach documents and external resources

### 🌐 Document Management
- **Notion Integration** — Auto-ingest Notion databases (scheduled workers)
- **File Upload** — Managers can upload PDFs/DOCX (chunked + embedded)
- **Version Tracking** — Content hash prevents duplicate embeddings
- **Project Assignment** — Documents belong to projects with visibility controls

### 🎨 Modern Frontend
- **Next.js 15** with App Router & React 19
- **TypeScript 5** for type safety
- **Tailwind CSS 4** with shadcn/ui components
- **Radix UI** primitives for accessibility
- **Dark mode** built-in with next-themes
- **Responsive design** for desktop and mobile
- **Separate interfaces** for employees and managers

---

## 🏗️ Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                         │
├─────────────────────────────────────────────────────────────────┤
│  1. User logs in (dev: mock auth | prod: Supabase Auth)        │
│  2. User asks question: "How do I deploy Atlas?"                │
│  3. User views received handovers from departing employees      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                          │
├─────────────────────────────────────────────────────────────────┤
│  • apps/web/app/chatbot/         - RAG search interface        │
│  • apps/web/app/handovers/       - Handover management         │
│  • apps/web/app/documents/       - Document browser            │
│  • apps/web/app/manager/         - Manager upload interface    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP (JWT auth)
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  POST /api/search                                               │
│    1. Verify JWT → Get user_id                                 │
│    2. Load user's projects                                      │
│    3. Embed query (Cohere)                                      │
│    4. Vector search (pgvector + ACL)                            │
│       → UNION(documents user can access, handovers user is in)  │
│    5. Rerank results (Cohere)                                   │
│    6. Generate answer (Groq LLM)                                │
│    7. Audit log query                                           │
│                                                                 │
│  POST /api/handovers                                            │
│    1. Create handover record                                    │
│    2. Chunk handover content                                    │
│    3. Embed chunks (Cohere)                                     │
│    4. Insert chunks with handover_id                            │
│                                                                 │
│  GET /api/handovers                                             │
│    → Returns handovers user sent/received                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓ SQL queries
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE (Postgres + pgvector)                     │
├─────────────────────────────────────────────────────────────────┤
│  • employees              - Users (synced with Supabase Auth)   │
│  • projects               - Access boundaries                   │
│  • employee_projects      - Who belongs to which projects       │
│  • documents              - Document metadata                   │
│  • handovers              - Knowledge handover records          │
│  • chunks                 - Searchable text + 1024-dim vectors  │
│    ├─ doc_id (nullable)   - Chunks from documents              │
│    └─ handover_id (null)  - Chunks from handovers              │
│  • audit_queries          - Query logs for compliance           │
└─────────────────────────────────────────────────────────────────┘
                              ↑
                              │ (scheduled ingestion)
┌─────────────────────────────────────────────────────────────────┐
│                   WORKERS (Notion Ingestion)                    │
├─────────────────────────────────────────────────────────────────┤
│  python workers/ingest_notion.py --notion-db-id <id>            │
│    1. Fetch pages from Notion API                               │
│    2. Convert blocks → Markdown                                 │
│    3. Chunk text (300-700 tokens, 50-token overlap)             │
│    4. Embed chunks (Cohere)                                     │
│    5. Upsert documents + chunks to database                     │
│    (Runs every 6 hours via cron/Lambda/Cloud Scheduler)         │
└─────────────────────────────────────────────────────────────────┘
```

### Access Control Logic

**Documents:**
```
User can see document IF:
  • document.visibility = 'Public', OR
  • document.project_id IN user.projects
```

**Handovers:**
```
User can see handover IF:
  • user = handover.from_employee_id (sender), OR
  • user = handover.to_employee_id (recipient), OR
  • user IN handover.cc_employee_ids (CC'd)
```

**Search Results:**
- UNION of documents + handovers user has access to
- Ordered by vector similarity score
- Reranked by Cohere for relevance

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **Supabase Account** (free tier works)
- **API Keys:**
  - Cohere API key ([cohere.com](https://cohere.com))
  - Groq API key ([console.groq.com](https://console.groq.com))
  - Notion API key ([notion.so/my-integrations](https://www.notion.so/my-integrations)) — optional

### Installation (30 minutes)

#### 1. Clone Repository

```bash
git clone <your-repo-url>
cd capstone-project-rag-based-knowledge-hub
```

#### 2. Database Setup (Supabase)

**a. Create Supabase Project**
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Wait for initialization (~2 minutes)

**b. Run Migrations**

Go to **Supabase Dashboard** → **SQL Editor** and run these in order:

```sql
-- Migration 1: Base schema (employees, projects, documents, chunks)
-- Copy entire content from: supabase/migrations/20251002234351_updated_db.sql
```

```sql
-- Migration 2: Handovers feature
-- Copy entire content from: supabase/migrations/20251007000000_add_handovers.sql
```

```sql
-- Migration 3: Fix source_external_id
-- Copy entire content from: supabase/migrations/20251007_fix_source_external_id.sql
```

**c. Seed Test Data**

```sql
-- Copy entire content from: supabase/seed.sql
-- This creates test employees, projects, and assignments
```

#### 3. Environment Variables

Create `.env` in project root:

```env
# ============================================================================
# Database (from Supabase Dashboard → Settings → Database → Connection String)
# ============================================================================
DATABASE_URL=postgresql://postgres.[PROJECT]:PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres

# ============================================================================
# Backend (apps/backend/.env)
# ============================================================================
SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
COHERE_API_KEY=your-cohere-api-key
GROQ_API_KEY=gsk_your-groq-key
CORS_ORIGINS=http://localhost:3000

# Testing (dev only)
TEST_USER_ID=550e8400-e29b-41d4-a716-446655440000
TEST_JWT_TOKEN=<generate using apps/backend/generate_test_jwt.py>

# ============================================================================
# Frontend (apps/web/.env.local)
# ============================================================================
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# ============================================================================
# Workers (optional, for Notion ingestion)
# ============================================================================
NOTION_API_KEY=secret_your-notion-integration-token
```

**How to get these values:**
- `SUPABASE_URL` + `SUPABASE_ANON_KEY`: Dashboard → Settings → API
- `SUPABASE_JWT_SECRET`: Dashboard → Settings → API → JWT Secret
- `DATABASE_URL`: Dashboard → Settings → Database → Connection String (use "Connection pooling")
- `COHERE_API_KEY`: Sign up at [cohere.com](https://cohere.com) → Dashboard → API Keys
- `GROQ_API_KEY`: Sign up at [console.groq.com](https://console.groq.com) → API Keys
- `NOTION_API_KEY`: [notion.so/my-integrations](https://www.notion.so/my-integrations) → Create integration

#### 4. Install Dependencies

```bash
# Frontend
cd apps/web
npm install

# Backend
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Workers (optional, for Notion ingestion)
cd ../../workers
pip install -r requirements.txt
```

#### 5. Generate Test JWT Tokens

```bash
cd apps/backend
python generate_test_jwt.py employee  # Regular employee token
python generate_test_jwt.py manager   # Manager token

# Add these to apps/backend/.env:
# TEST_JWT_TOKEN=<token-from-above>
```

#### 6. Run Services Locally

**Terminal 1 - Backend:**
```bash
cd apps/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000
# → API docs: http://localhost:8000/docs
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm run dev
# → http://localhost:3000
```

**Terminal 3 - Worker (optional, for Notion ingestion):**
```bash
cd workers
source venv/bin/activate
python ingest_notion.py --notion-db-id <your-notion-database-id>
```

#### 7. Test the Application

1. **Open** http://localhost:3000
2. **Login** with test credentials:
   - Employee: `employee@company.com` / `dev`
   - Manager: `manager@company.com` / `dev`
3. **Navigate** to Chatbot section
4. **Ask a question**: "What is Atlas?" or "How do I deploy?"
5. **See results** with AI-generated answer + source citations

---

## 📂 Repository Structure

```
capstone-project-rag-based-knowledge-hub/
├── README.md                         ← You are here
├── .env.example                      ← Environment variable template
├── docker-compose.yml                ← Docker deployment (backend + frontend)
├── AWS_AMPLIFY_APPRUNNER_GUIDE.md    ← Full AWS deployment guide
├── DEMO_DEPLOYMENT.md                ← Quick demo deployment guide
├── HANDOVERS_TESTING_GUIDE.md        ← How to test handovers feature
│
├── supabase/                         ← Database schema and migrations
│   ├── migrations/
│   │   ├── 20251002234351_updated_db.sql          ← Base schema
│   │   ├── 20251007000000_add_handovers.sql       ← Handovers feature
│   │   └── 20251007_fix_source_external_id.sql    ← Notion ID fix
│   └── seed.sql                      ← Test data (employees, projects)
│
├── apps/
│   ├── web/                          ← Next.js 14 Frontend
│   │   ├── app/
│   │   │   ├── page.tsx              ← Landing page
│   │   │   ├── login/page.tsx        ← Login page (dev: mock auth)
│   │   │   ├── home/                 ← Employee dashboard
│   │   │   ├── chatbot/              ← RAG search interface
│   │   │   ├── handovers/            ← Handover management
│   │   │   ├── documents/            ← Document browser
│   │   │   └── manager/              ← Manager interface (upload docs)
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                   ← shadcn/ui primitives
│   │   │   ├── login-form.tsx        ← Mock login (dev only)
│   │   │   ├── manager-dashboard.tsx ← Manager dashboard
│   │   │   └── [other components]    ← Feature-specific components
│   │   │
│   │   ├── hooks/                    ← Custom React hooks
│   │   ├── types/                    ← TypeScript type definitions
│   │   ├── Dockerfile                ← Frontend Docker image
│   │   └── next.config.mjs           ← Next.js config (standalone mode)
│   │
│   └── backend/                      ← FastAPI Backend
│       ├── app/
│       │   ├── main.py               ← FastAPI app entry point
│       │   │
│       │   ├── api/routes/
│       │   │   ├── search.py         ← POST /api/search (RAG endpoint)
│       │   │   ├── docs.py           ← GET /api/docs/:id (document metadata)
│       │   │   ├── upload.py         ← POST /api/upload (file upload)
│       │   │   ├── handovers.py      ← Handover CRUD endpoints
│       │   │   ├── employees.py      ← Employee endpoints
│       │   │   └── notion.py         ← Notion webhook endpoint
│       │   │
│       │   ├── services/
│       │   │   ├── auth.py           ← JWT verification, get user projects
│       │   │   ├── embeddings.py     ← Cohere embeddings (1024-dim)
│       │   │   ├── retrieval.py      ← Vector search + Cohere reranking
│       │   │   ├── llm.py            ← Groq LLM inference
│       │   │   ├── audit.py          ← Audit logging
│       │   │   ├── db.py             ← Database helper functions
│       │   │   └── storage.py        ← File storage (uploads)
│       │   │
│       │   ├── db/
│       │   │   └── client.py         ← asyncpg connection pool
│       │   │
│       │   └── models/
│       │       └── schemas.py        ← Pydantic request/response models
│       │
│       ├── tests/
│       │   ├── test_handovers_api.py ← Handover API tests (13 tests)
│       │   ├── test_handovers_db.py  ← Handover DB tests (12 tests)
│       │   └── seed_test_data.sql    ← Test fixtures
│       │
│       ├── generate_test_jwt.py      ← Generate JWT tokens for testing
│       ├── Dockerfile                ← Backend Docker image
│       └── requirements.txt          ← Python dependencies
│
└── workers/                          ← Notion Ingestion Pipeline
    ├── ingest_notion.py              ← Main ingestion script
    ├── debug_notion.py               ← Debugging tool
    │
    ├── lib/
    │   ├── notion_client.py          ← Notion API wrapper
    │   ├── normalizer.py             ← Convert Notion blocks → Markdown
    │   ├── chunker.py                ← Split text into chunks
    │   ├── embeddings.py             ← Embed chunks with Cohere
    │   └── db_operations.py          ← Upsert to database
    │
    └── requirements.txt              ← Worker dependencies
```

---

## 🧩 Feature Deep Dives

### 1. Employee Handovers

**What is a Handover?**

A structured knowledge transfer from one employee to another, typically during:
- Onboarding new team members
- Project transitions
- Employee offboarding
- Temporary coverage (vacation, leave)

**Handover Structure:**

```typescript
{
  title: "Atlas API Handover",
  from_employee_id: "uuid-of-sender",
  to_employee_id: "uuid-of-recipient",
  cc_employee_ids: ["uuid-of-manager"],  // Optional CC
  project_id: "atlas-api",                // Optional project link

  // Content sections (all optional)
  context: "Why this handover exists...",
  current_status: "What's been done so far...",
  next_steps: [
    { task: "Review deployment checklist", done: false },
    { task: "Set up local dev environment", done: true }
  ],
  resources: [
    { type: "doc", doc_id: 123, title: "Atlas Deploy Guide" },
    { type: "link", url: "https://github.com/atlas", title: "Atlas Repo" }
  ],
  contacts: [
    { name: "John Doe", email: "john@company.com", role: "Tech Lead" }
  ],
  additional_notes: "Free-form notes...",

  // Lifecycle
  status: "pending" | "acknowledged" | "completed",
  created_at: "2025-01-15T10:00:00Z",
  acknowledged_at: null,  // Set when recipient acknowledges
  completed_at: null       // Set when work is done
}
```

**How Handovers are Embedded and Searched:**

1. **Creation:**
   ```
   User creates handover via POST /api/handovers
     ↓
   Backend:
     1. Inserts handover record into database
     2. Constructs searchable text from all fields:
        "Title: Atlas API Handover
         Context: Project transition...
         Current Status: API deployed...
         Next Steps: Review deployment checklist..."
     3. Chunks the text (300-700 tokens)
     4. Embeds each chunk with Cohere
     5. Inserts chunks with handover_id (doc_id=NULL)
   ```

2. **Searching:**
   ```
   User searches "How do I deploy Atlas?"
     ↓
   Backend:
     1. Embeds query with Cohere
     2. Runs vector search:
        SELECT ... FROM chunks
        UNION (
          -- Documents user can access
          WHERE doc_id IS NOT NULL AND (public OR in user's projects)
        )
        UNION (
          -- Handovers user is involved in
          WHERE handover_id IS NOT NULL
            AND (user=sender OR user=recipient OR user IN cc_list)
        )
     3. Reranks results with Cohere
     4. Generates answer with Groq LLM
     5. Returns answer + citations (includes handover links)
   ```

3. **Access Control:**
   - Handovers are **PRIVATE** by default
   - Only sender, recipient, and CC'd users can:
     - View the handover details
     - See handover chunks in search results
   - Prevents unauthorized access to sensitive knowledge

**API Endpoints:**

- `POST /api/handovers` — Create handover
- `GET /api/handovers` — List user's handovers (sent + received)
- `GET /api/handovers/:id` — Get specific handover
- `PATCH /api/handovers/:id` — Update status (acknowledge/complete)
- `DELETE /api/handovers/:id` — Delete handover (sender only)

**Lifecycle:**

```
Created (status=pending)
  ↓
Recipient acknowledges (status=acknowledged, acknowledged_at set)
  ↓
Work completed (status=completed, completed_at set)
```

---

### 2. Notion Ingestion

**What It Does:**

Automatically syncs Notion pages into your RAG system, making them searchable via vector embeddings.

**How It Works:**

```
1. Fetch Pages from Notion Database
   ↓
   notion_client.list_notion_pages(database_id)
   → Returns list of pages with metadata

2. For Each Page:
   a. Fetch Blocks (content)
      notion_client.fetch_blocks(page_id)
      → Returns paragraphs, headings, lists, code blocks, etc.

   b. Convert to Markdown
      normalizer.normalize_to_markdown(blocks)
      → Preserves structure: headings, lists, tables
      → Extracts heading_path: ["Runbook", "Incidents", "Step 1"]

   c. Compute Content Hash
      hashlib.md5(markdown)
      → If hash unchanged from last run → skip re-embedding

   d. Detect Metadata
      - Project: page.properties["Project"]["select"]["name"] → "Atlas"
      - Visibility: page.properties["Visibility"]["status"]["name"] → "Public"/"Private"

   e. Upsert Document
      db_operations.upsert_document(...)
      → INSERT ... ON CONFLICT (source_external_id) DO UPDATE
      → Returns doc_id

   f. Chunk the Markdown
      chunker.chunk_markdown(markdown)
      → Splits into 300-700 token pieces with 50-token overlap
      → Preserves context between chunks

   g. Embed Each Chunk
      embeddings.embed_text(chunk.text)
      → Calls Cohere API
      → Returns 1024-dimensional vector

   h. Insert Chunks
      db_operations.insert_chunk(doc_id, chunk, embedding)
      → Inserts into chunks table with doc_id

3. Database Now Contains:
   - 1 row in documents (title, project, visibility, URI, hash)
   - N rows in chunks (text, embedding, heading_path, doc_id)
```

**Why Chunking?**

- LLMs have token limits (8K-32K tokens)
- Long documents (50+ pages) exceed these limits
- Chunks = bite-sized pieces (300-700 tokens each)
- Overlap ensures context isn't lost between chunks

**Why Content Hash?**

- Avoid re-embedding unchanged content (saves API costs)
- Worker checks hash before embedding
- Only re-embeds if content changed

**Scheduling:**

Run ingestion periodically to sync new/updated Notion pages:

```bash
# Manual run
python workers/ingest_notion.py --notion-db-id <id>

# Cron (every 6 hours)
0 */6 * * * cd /path/to/workers && python ingest_notion.py --notion-db-id <id>

# AWS Lambda (scheduled with EventBridge)
# Google Cloud Run Job (scheduled with Cloud Scheduler)
```

**Notion Setup:**

1. Create Notion integration: [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Get integration token (starts with `secret_`)
3. Share your Notion database with the integration:
   - Open database → Click `•••` → "Connections" → Add your integration
4. Get database ID from URL:
   - URL: `https://notion.so/workspace/<DATABASE_ID>?v=...`
5. Add to `.env`:
   ```
   NOTION_API_KEY=secret_your-token
   ```

---

### 3. RAG Search Flow (End-to-End)

```
[1] User asks: "How do I deploy Atlas?"
      ↓
[2] Frontend: POST /api/search
      Headers: Authorization: Bearer <JWT>
      Body: { query: "How do I deploy Atlas?", top_k: 12 }
      ↓
[3] Backend (apps/backend/app/api/routes/search.py):
      ↓
    [3a] Verify JWT → Extract user_id
         auth.verify_jwt(token) → "550e8400-e29b-41d4-a716-446655440000"
      ↓
    [3b] Load user's projects
         auth.get_user_projects(user_id) → ["atlas-api", "demo-project"]
      ↓
    [3c] Embed query
         embeddings.embed_query("How do I deploy Atlas?")
         → Returns 1024-dim vector: [0.023, -0.15, 0.091, ...]
      ↓
    [3d] Vector search (retrieval.run_vector_search)
         SQL:
         SELECT ... FROM chunks
         UNION (
           -- Documents
           WHERE doc_id IS NOT NULL
             AND (visibility='Public' OR project_id IN ('atlas-api','demo-project'))
         )
         UNION (
           -- Handovers
           WHERE handover_id IS NOT NULL
             AND (from_employee_id='<user>' OR to_employee_id='<user>' OR user IN cc_list)
         )
         ORDER BY embedding <=> query_vector  -- pgvector cosine similarity
         LIMIT 200

         → Returns 200 candidate chunks
      ↓
    [3e] Rerank (retrieval.rerank)
         Cohere rerank-v3 reranks 200 → top 12 most relevant
         → Returns 12 best chunks
      ↓
    [3f] Generate answer (llm.call_llm)
         Prompt to Groq (Llama 3.3 or Mixtral):
         """
         Based on these documents, answer: How do I deploy Atlas?

         [Chunk 1: Atlas Deploy Guide - "To deploy Atlas API, first..."]
         [Chunk 2: Atlas Runbook - "Deployment checklist: 1. Check env vars..."]
         [Chunk 3: Atlas Handover - "Deployment steps: make deploy, verify health..."]
         """

         → LLM generates: "To deploy Atlas API, follow these steps: ..."
      ↓
    [3g] Audit log (audit.audit_log)
         Inserts into audit_queries table:
         (user_id, query, used_doc_ids, used_handover_ids, timestamp)
      ↓
    [3h] Return response
         {
           "answer": "To deploy Atlas API, follow these steps: ...",
           "chunks": [
             { "doc_id": 123, "title": "Atlas Deploy Guide", "text": "...", "score": 0.87 },
             { "handover_id": 5, "title": "Atlas Handover", "text": "...", "score": 0.82 }
           ],
           "used_doc_ids": [123, 124],
           "used_handover_ids": [5]
         }
      ↓
[4] Frontend displays:
    - AI-generated answer in chat bubble
    - Source citations with links:
      → "Atlas Deploy Guide" (links to Notion)
      → "Atlas Handover" (links to /handovers/5)
    - User clicks citation → Opens source
```

**Key Points:**
- **ACL enforced at SQL level** (not in application code)
- **UNION** combines document chunks + handover chunks
- **Reranking** improves relevance (Cohere is good at this)
- **Audit logs** track all queries for compliance

---

## 🌍 Environment Variables

### Frontend (`apps/web/.env.local`)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API endpoint | `http://localhost:8000` (dev)<br>`https://your-api.awsapprunner.com` (prod) |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | `https://abcdefgh.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |

### Backend (`apps/backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (from Supabase) | `postgresql://postgres.abc:pass@aws-0-us-east-1.pooler.supabase.com:5432/postgres` |
| `SUPABASE_JWT_SECRET` | For verifying JWT tokens | Get from Supabase Dashboard → Settings → API → JWT Secret |
| `SUPABASE_URL` | Supabase project URL | `https://abcdefgh.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (for admin operations) | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `COHERE_API_KEY` | Cohere API key for embeddings + reranking | `xxx-yyy-zzz` |
| `GROQ_API_KEY` | Groq API key for LLM inference | `gsk_xxxxxxxxxxxxx` |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `http://localhost:3000,https://yourapp.com` |
| `TEST_USER_ID` | Test user UUID (dev only) | `550e8400-e29b-41d4-a716-446655440000` |
| `TEST_JWT_TOKEN` | Test JWT token (dev only) | Generate with `generate_test_jwt.py` |

### Workers (`workers/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Same PostgreSQL connection string | (same as backend) |
| `NOTION_API_KEY` | Notion integration token | `secret_xxxxxxxxxxxxx` |
| `COHERE_API_KEY` | Same Cohere key | (same as backend) |

---

## 🧪 Testing

### Backend Tests

```bash
cd apps/backend

# Run all tests
pytest tests/ -v

# Test handovers feature
pytest tests/test_handovers_db.py -v      # Database layer (12 tests)
pytest tests/test_handovers_api.py -v     # API endpoints (13 tests)

# Test specific function
pytest tests/test_handovers_db.py::test_create_handover -v
```

### Manual Testing

```bash
# 1. Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 2. Test search (with JWT)
curl -X POST http://localhost:8000/api/search \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I deploy Atlas?", "top_k": 12}'

# 3. Test handovers
curl -X GET http://localhost:8000/api/handovers \
  -H "Authorization: Bearer <your-jwt-token>"

# 4. Check database has data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM chunks;"
# Expected: > 0
```

### Frontend Testing

1. Open http://localhost:3000
2. Login with test credentials:
   - Employee: `employee@company.com` / `dev`
   - Manager: `manager@company.com` / `dev`
3. Test search in Chatbot section
4. Test handovers:
   - Create handover as manager
   - View received handovers as employee
   - Acknowledge and complete handovers

---

## 🚀 Deployment

### Development (Docker Compose)

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production (AWS - Recommended)

**Full guide:** [`AWS_AMPLIFY_APPRUNNER_GUIDE.md`](./AWS_AMPLIFY_APPRUNNER_GUIDE.md)

**Summary:**
1. **Backend → AWS App Runner** (from ECR Docker image)
2. **Frontend → AWS Amplify** (from GitHub repo)
3. **Database → Supabase** (already hosted)
4. **Workers → AWS Lambda** (scheduled with EventBridge)

**Quick steps:**

```bash
# 1. Push code to GitHub
git push origin main

# 2. Build and push backend to ECR
cd apps/backend
aws ecr create-repository --repository-name rag-backend --region us-east-1
docker build -t rag-backend:latest .
docker tag rag-backend:latest <ECR_URI>:latest
docker push <ECR_URI>:latest

# 3. Create App Runner service (via AWS Console)
# - Container registry: ECR
# - Image URI: <ECR_URI>:latest
# - Port: 8000
# - Environment variables: DATABASE_URL, SUPABASE_JWT_SECRET, COHERE_API_KEY, GROQ_API_KEY, CORS_ORIGINS

# 4. Deploy frontend to Amplify (via AWS Console)
# - Connect GitHub repo
# - Branch: main
# - Build settings: Auto-detected (Next.js)
# - Root directory: apps/web
# - Environment variables: NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

# 5. Update CORS
# Update backend CORS_ORIGINS to include Amplify URL
```

**Cost:** ~$10-15/month with AWS free tier

### Alternative Deployments

**Vercel + Render:**
- Frontend → Vercel (free)
- Backend → Render (free tier available)

**Google Cloud:**
- Frontend → Cloud Run
- Backend → Cloud Run
- Workers → Cloud Run Jobs (scheduled)

**Azure:**
- Frontend → Azure Static Web Apps
- Backend → Azure Container Apps

---

## ⚠️ Authentication Status

### Current Setup (Development)

**Mock Authentication:**
- Frontend uses hardcoded credentials (see `apps/web/components/login-form.tsx`)
- Passwords are just "dev"
- Pre-generated JWT tokens stored in localStorage
- Works for demos and local testing only

**Test Users:**
- **Employee:** `employee@company.com` / `dev`
  - Projects: demo-project, atlas-api
  - Role: member (read-only)
- **Manager:** `manager@company.com` / `dev`
  - Projects: all projects
  - Role: manager (can upload, create handovers)

### Production Requirements

**For real deployment, you MUST:**

1. **Create real Supabase Auth users:**
   - Supabase Dashboard → Authentication → Users → Add user
   - Use real email addresses
   - Users sign up via frontend

2. **Replace mock login with Supabase Auth:**
   ```typescript
   // apps/web/components/login-form.tsx
   import { createClient } from '@supabase/supabase-js'

   const supabase = createClient(
     process.env.NEXT_PUBLIC_SUPABASE_URL,
     process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
   )

   // In handleSubmit:
   const { data, error } = await supabase.auth.signInWithPassword({
     email,
     password
   })

   if (error) {
     setError(error.message)
     return
   }

   // Supabase auto-stores JWT in cookies
   router.push('/home')
   ```

3. **Sync employees table with Supabase Auth:**
   ```sql
   -- After user signs up, insert into employees table
   INSERT INTO employees (employee_id, email, display_name)
   VALUES (auth.uid(), auth.email(), 'User Name')
   ON CONFLICT (employee_id) DO NOTHING;
   ```

4. **Token Expiry:**
   - Current test tokens expire in ~1 year
   - Production tokens should expire in 1-24 hours
   - Supabase handles token refresh automatically

---

## 🐛 Troubleshooting

### "CORS error when calling backend"

**Cause:** Backend's `CORS_ORIGINS` doesn't include frontend URL.

**Fix:**
```bash
# In apps/backend/.env
CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.com

# Restart backend
```

### "JWT verification failed"

**Cause:** Wrong `SUPABASE_JWT_SECRET`.

**Fix:**
1. Go to Supabase Dashboard → Settings → API
2. Copy "JWT Secret" (NOT "anon public" key)
3. Update `apps/backend/.env`:
   ```
   SUPABASE_JWT_SECRET=your-actual-jwt-secret
   ```
4. Restart backend

### "No search results returned"

**Possible causes:**

1. **No chunks in database:**
   ```bash
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM chunks;"
   # If 0: Run Notion ingestion worker
   ```

2. **User has no project access:**
   ```sql
   -- Check user's projects
   SELECT project_id FROM employee_projects
   WHERE employee_id = '<user-id>';

   -- Add user to project
   INSERT INTO employee_projects (employee_id, project_id, role)
   VALUES ('<user-id>', 'demo-project', 'member');
   ```

3. **All docs are Private:**
   ```sql
   -- Make one doc Public for testing
   UPDATE documents SET visibility = 'Public' WHERE doc_id = 1;
   ```

### "Notion API error"

**Common issues:**

1. **Wrong API key:**
   - Get integration token from [notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Must start with `secret_`

2. **Database not shared with integration:**
   - Open Notion database
   - Click `•••` → "Connections" → Add your integration

3. **Rate limits:**
   - Notion API: 3 requests/second
   - Add delays in `workers/lib/notion_client.py`

### "Cohere API rate limit exceeded"

**Cause:** Free tier limits (100 requests/minute).

**Fix:**
1. Upgrade Cohere plan, OR
2. Add rate limiting in `workers/lib/embeddings.py`:
   ```python
   import time
   time.sleep(0.1)  # Between API calls
   ```

### "pgvector extension not found"

**Cause:** PostgreSQL doesn't have pgvector installed.

**Fix:**
```sql
-- In Supabase SQL editor
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 📚 Additional Resources

- **Supabase:** [docs.supabase.com](https://docs.supabase.com)
- **FastAPI:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Next.js:** [nextjs.org/docs](https://nextjs.org/docs)
- **pgvector:** [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
- **Cohere:** [docs.cohere.com](https://docs.cohere.com)
- **Groq:** [console.groq.com/docs](https://console.groq.com/docs)
- **shadcn/ui:** [ui.shadcn.com](https://ui.shadcn.com)
- **Notion API:** [developers.notion.com](https://developers.notion.com)

---

## 📋 API Reference

### Core Endpoints

#### POST /api/search

Search documents and handovers, generate AI answer.

**Request:**
```json
{
  "query": "How do I deploy the Atlas API?",
  "top_k": 12
}
```

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "answer": "To deploy the Atlas API, follow these steps: ...",
  "chunks": [
    {
      "doc_id": 123,
      "handover_id": null,
      "title": "Atlas Deploy Guide",
      "text": "To deploy Atlas API, first ensure...",
      "uri": "https://notion.so/abc123",
      "source_type": "document",
      "score": 0.87
    },
    {
      "doc_id": null,
      "handover_id": 5,
      "title": "Atlas Handover",
      "text": "Deployment steps: make deploy...",
      "uri": "handover://5",
      "source_type": "handover",
      "score": 0.82
    }
  ],
  "used_doc_ids": [123, 456],
  "used_handover_ids": [5]
}
```

#### POST /api/handovers

Create a new handover.

**Request:**
```json
{
  "to_employee_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Atlas Project Handover",
  "project_id": "atlas-api",
  "context": "Transitioning Atlas project to new team member",
  "current_status": "API deployed, documentation updated",
  "next_steps": [
    { "task": "Review deployment checklist", "done": false },
    { "task": "Set up local dev environment", "done": false }
  ],
  "resources": [
    { "type": "doc", "doc_id": 123, "title": "Atlas Deploy Guide" },
    { "type": "link", "url": "https://github.com/atlas", "title": "Atlas Repo" }
  ],
  "contacts": [
    { "name": "John Doe", "email": "john@company.com", "role": "Tech Lead" }
  ],
  "additional_notes": "Feel free to reach out with questions",
  "cc_employee_ids": ["770e8400-e29b-41d4-a716-446655440002"]
}
```

**Response:** (201 Created)
```json
{
  "handover_id": 10,
  "from_employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "to_employee_id": "660e8400-e29b-41d4-a716-446655440001",
  "from_name": "John Employee",
  "from_email": "employee@company.com",
  "title": "Atlas Project Handover",
  "status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  ...
}
```

#### GET /api/handovers

List all handovers for authenticated user.

**Response:**
```json
{
  "received": [
    { "handover_id": 10, "title": "Atlas Handover", "status": "pending", ... }
  ],
  "sent": [
    { "handover_id": 11, "title": "Phoenix Handover", "status": "acknowledged", ... }
  ]
}
```

#### PATCH /api/handovers/:id

Update handover status (recipient only).

**Request:**
```json
{
  "status": "acknowledged"  // or "completed"
}
```

---

## 🔮 Future Enhancements

- **Additional Data Sources:** Google Drive, Confluence, Slack, GitHub
- **Hybrid Search:** Combine vector + BM25 keyword search
- **Multi-turn Conversations:** Chat history and follow-up questions
- **Fine-grained Permissions:** User-level and group-level access
- **Analytics Dashboard:** Query trends, popular documents, user activity
- **Feedback Loop:** Thumbs up/down to improve retrieval
- **Document Upload Improvements:** OCR for scanned PDFs
- **Smart Summaries:** Auto-generate document summaries
- **Mobile App:** iOS/Android native apps
- **Voice Search:** Ask questions via voice input
- **Export Results:** Export to PDF/Markdown
- **Handover Templates:** Pre-defined templates for common transitions
- **Handover Reminders:** Automatic notifications for pending handovers

---

## 👥 Contributors

Built by the RAG Knowledge Hub team at PNU Computer Science Department.

---

## 📄 License

MIT License - see LICENSE file for details.

---

**🚀 Ready to deploy? Check out [`AWS_AMPLIFY_APPRUNNER_GUIDE.md`](./AWS_AMPLIFY_APPRUNNER_GUIDE.md) for step-by-step AWS deployment!**
