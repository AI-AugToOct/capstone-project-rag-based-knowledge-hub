# RAG Knowledge Hub

> A permission-aware knowledge search system: authenticated users ask questions → we retrieve only content they're allowed to see → LLM answers with citations.

[![Built with Next.js](https://img.shields.io/badge/Next.js-14+-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688)](https://fastapi.tiangolo.com/)
[![Postgres](https://img.shields.io/badge/PostgreSQL-15+-336791)](https://www.postgresql.org/)

---

## 📖 Overview

RAG Knowledge Hub is an enterprise knowledge search platform that combines the power of vector search with fine-grained access control. Think of it as "ChatGPT for your company's internal documents" — but with security built-in from day one.

**The Problem:** Teams have knowledge scattered across Notion, Google Drive, Confluence, and internal wikis. Finding information requires knowing where to look and having the right permissions.

**Our Solution:** A unified search interface that:
- Authenticates users via Supabase (JWT-based)
- Searches across all connected data sources (Notion initially, more later)
- Only retrieves documents the user is allowed to see (project-based permissions)
- Uses LLMs (via Groq) to synthesize answers from relevant chunks
- Provides citations with deep links back to source documents

**Who It's For:**
- Engineering teams with internal documentation in Notion
- Organizations that need secure, permission-aware search
- Teams building internal AI tools with compliance requirements

---

## ✨ Features

- 🔐 **Permission-Aware Search** — Users only see documents from their projects + public docs
- 🎯 **Vector Search** — Uses pgvector with HNSW index for fast semantic search
- 🤖 **LLM-Powered Answers** — Groq inference (Llama 3.3, Mixtral, ChatGPT-OSS ) with Cohere embeddings
- 📚 **Source Citations** — Every answer includes links to source documents
- 🔄 **Cohere Reranker** — Improves relevance by reranking vector search results
- 📊 **Audit Logging** — Tracks every query for compliance and debugging
- 🌐 **Notion Integration** — Ingests pages from Notion databases (extensible to PDFs, Drive, etc.)
- 🎨 **Modern UI** — Built with Next.js 14, shadcn/ui, and Tailwind CSS
- 🌙 **Dark Mode** — Built-in theme switching

---

## 🏗️ How It Works

### High-Level Flow

```
User Browser
    ↓ (1) Login via Supabase Auth
    ↓ (2) Ask question in chat interface
    ↓
Next.js Frontend (Port 3000)
    ↓ (3) POST /api/search with JWT
    ↓
FastAPI Backend (Port 8000)
    ↓ (4) Verify JWT → Get user's projects
    ↓ (5) Embed query (Cohere 1024-dim)
    ↓ (6) Search chunks (pgvector + ACL filter)
    ↓ (7) Rerank results (Cohere rerank-v3)
    ↓ (8) Generate answer (Groq LLM)
    ↓ (9) Log to audit_queries
    ↓
    ← (10) Return answer + citations
    ↓
User sees answer with source links

Offline (Cron/Scheduled):
Notion API → Workers → Normalize → Chunk → Embed → Upsert to Postgres
```

### Access Control Logic

**Rule:** User can see document IF:
```
document.visibility = 'Public' 
OR 
document.project_id IN user.projects
```

**Example:**
- **User:** Sarah (`employee_id: 550e8400-...`)
- **Sarah's Projects:** `['Atlas', 'Phoenix']` (from `employee_projects` table)
- **Documents:**
  - **Atlas Deploy Guide** → `visibility=Private, project_id=Atlas` → ✅ Sarah CAN see
  - **Company Handbook** → `visibility=Public` → ✅ Sarah CAN see
  - **Bolt API Docs** → `visibility=Private, project_id=Bolt` → ❌ Sarah CANNOT see

ACL is enforced at the database level via SQL `WHERE` clause, not in application code.

### Database Schema

5 tables power the entire system:

1. **`employees`** — Users (synced with Supabase Auth)
2. **`projects`** — Access boundaries (e.g., 'Atlas', 'Bolt')
3. **`employee_projects`** — Who belongs to which projects
4. **`documents`** — Metadata for each Notion page/file
5. **`chunks`** — Searchable text pieces with 1024-dim embeddings
6. **`audit_queries`** — Query logs for compliance

**For detailed schema with examples and SQL queries, see [`supabase/README.md`](./supabase/README.md).**

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Supabase Account** (free tier works)
- **API Keys:**
  - Cohere API key ([cohere.com](https://cohere.com))
  - Groq API key ([console.groq.com](https://console.groq.com))
  - Notion Integration token ([notion.so/my-integrations](https://www.notion.so/my-integrations))

### Installation (30 minutes)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd rag-knowledge-hub

# 2. Install frontend dependencies
cd apps/web
npm install

# 3. Install backend dependencies
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Install worker dependencies
cd ../../workers
pip install -r requirements.txt

# 5. Set up environment variables
cd ../..
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section)

# 6. Run database migrations
cd supabase
npx supabase link --project-ref <your-supabase-project-ref>
npx supabase db push

# 7. Seed test data
# In Supabase SQL Editor (https://supabase.com/dashboard/project/_/sql):
INSERT INTO employees (employee_id, email, display_name) 
VALUES ('<your-supabase-auth-uid>', 'you@example.com', 'Your Name');

INSERT INTO projects (project_id, name) 
VALUES ('Atlas', 'Atlas Platform');

INSERT INTO employee_projects (employee_id, project_id, role) 
VALUES ('<your-supabase-auth-uid>', 'Atlas', 'owner');

# 8. Ingest Notion pages (run once to seed data)
cd workers
python ingest_notion.py --notion-db-id <your-notion-database-id>
# This will embed 5-10 pages. Takes ~5 minutes depending on content size.
```

### Running Locally

```bash
# Terminal 1 - Frontend
cd apps/web
npm run dev
# → http://localhost:3000

# Terminal 2 - Backend
cd apps/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000
# → API docs: http://localhost:8000/docs

# Terminal 3 - Worker (optional, for re-ingesting)
cd workers
source venv/bin/activate
python ingest_notion.py --notion-db-id <id>
```

### First Test

1. Open http://localhost:3000
2. Sign up / Log in with email + password
3. Navigate to "AI Search" tab
4. Type: **"What is Atlas?"** or **"How do I deploy?"**
5. You should see:
   - An answer generated by the LLM
   - 3-5 source citations with links to Notion pages
   - Clicking a citation opens the Notion page

---

## 🌍 Environment Variables

### Frontend (`apps/web/.env.local`)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL | `https://abcdefgh.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `NEXT_PUBLIC_API_URL` | Backend API endpoint | `http://localhost:8000` (local) or `https://api.yourapp.com` (prod) |

**Get Supabase credentials:** Dashboard → Settings → API

### Backend (`apps/backend/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Postgres connection string with pgvector | `postgresql://user:pass@host:5432/db` |
| `SUPABASE_JWT_SECRET` | For verifying JWT tokens | Get from Supabase Dashboard → Settings → API → JWT Secret |
| `COHERE_API_KEY` | Cohere API key for embeddings + reranking | `xxx-yyy-zzz` |
| `GROQ_API_KEY` | Groq API key for LLM inference | `gsk_xxxxxxxxxxxxx` |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `http://localhost:3000,https://yourapp.com` |

### Workers (`workers/.env`)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Same Postgres connection string | (same as backend) |
| `NOTION_API_KEY` | Notion integration token | `secret_xxxxxxxxxxxxx` |
| `COHERE_API_KEY` | Same Cohere key | (same as backend) |

---

## 📂 Repository Structure

```
rag-knowledge-hub/
├── .env.example                      # Template for environment variables
├── .gitignore                        # Git ignore rules
├── docker-compose.yml                # Local dev: backend + postgres (optional)
├── README.md                         # This file
├── ARCHITECTURE.md                   # Lean architecture (essentials)
├── TESTING_GUIDE.md                  # How to test individual functions
│
├── supabase/                         # Database schema and migrations
│   ├── migrations/
│   │   └── 20251002234351_updated_db.sql # Creates 5 core tables + indexes
│   └── README.md                     # Complete database documentation
│
├── apps/                             # Frontend and backend applications
│   │
│   ├── web/                          # Next.js 14 frontend (TypeScript + React)
│   │   ├── app/
│   │   │   ├── layout.tsx            # Root layout with auth provider
│   │   │   ├── page.tsx              # Main app interface (tabs: Search/Docs/Projects)
│   │   │   ├── globals.css           # Global Tailwind styles
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # Login page with Supabase Auth
│   │   │   └── signup/
│   │   │       └── page.tsx          # Signup page
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui primitives (button, input, card, etc.)
│   │   │   ├── ChatInput.tsx         # Text input + send button for queries
│   │   │   ├── MessageList.tsx       # Display Q&A conversation
│   │   │   ├── SourcesList.tsx       # Show document citations
│   │   │   ├── Navbar.tsx            # Navigation bar
│   │   │   ├── theme-provider.tsx    # Dark mode provider
│   │   │   │
│   │   │   ├── documents-tab.tsx     # [Optional] Browse all searchable documents
│   │   │   └── projects-tab.tsx      # [Optional] View user's project memberships
│   │   │
│   │   ├── lib/
│   │   │   ├── utils.ts              # Utility functions (cn, etc.)
│   │   │   ├── supabase.ts           # Supabase client for auth
│   │   │   └── api.ts                # Backend API calls (searchKnowledge, etc.)
│   │   │
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript types (SearchResponse, Chunk, etc.)
│   │   │
│   │   ├── __tests__/                # Frontend unit tests (see README in this folder)
│   │   │   ├── components/           # Component tests (Jest + React Testing Library)
│   │   │   ├── lib/                  # API/utility tests
│   │   │   └── README.md             # How to run frontend tests
│   │   │
│   │   ├── public/                   # Static assets (logos, placeholders)
│   │   │
│   │   ├── package.json              # Dependencies and scripts
│   │   ├── tsconfig.json             # TypeScript config
│   │   ├── next.config.mjs           # Next.js config
│   │   ├── jest.config.js            # Jest configuration for tests
│   │   ├── jest.setup.js             # Test setup file
│   │   ├── .env.local                # Local environment variables (gitignored)
│   │   ├── postcss.config.mjs        # PostCSS config
│   │   └── components.json           # shadcn/ui config
│   │
│   └── backend/                      # FastAPI backend (Python)
│       ├── app/
│       │   ├── main.py               # FastAPI app entry (CORS, routers, startup)
│       │   │
│       │   ├── api/
│       │   │   └── routes/
│       │   │       ├── search.py     # POST /api/search — Main RAG endpoint
│       │   │       └── docs.py       # GET /api/docs/:doc_id — Document metadata
│       │   │
│       │   ├── services/
│       │   │   ├── auth.py           # JWT verification, get user projects
│       │   │   ├── embeddings.py     # Cohere embed-english-v3 (1024-dim)
│       │   │   ├── retrieval.py      # pgvector search + ACL + Cohere reranking
│       │   │   ├── llm.py            # Groq LLM inference (Llama 3.3, Mixtral, ChatGPT-OSS)
│       │   │   └── audit.py          # Audit logging to database
│       │   │
│       │   ├── db/
│       │   │   └── client.py         # asyncpg connection pool
│       │   │
│       │   └── models/
│       │       └── schemas.py        # Pydantic request/response models
│       │
│       ├── tests/                    # Unit tests for backend services (see TESTING_GUIDE.md)
│       │
│       ├── requirements.txt          # Python dependencies
│       ├── Dockerfile                # Container for deployment
│       └── .dockerignore             # Exclude files from Docker image
│
└── workers/                          # Offline ingestion (not a web server)
    ├── ingest_notion.py              # Main script: syncs Notion → Database
    ├── requirements.txt              # Worker dependencies
    │
    ├── lib/
    │   ├── notion_client.py          # Notion API wrapper
    │   ├── normalizer.py             # Convert Notion blocks → Markdown
    │   ├── chunker.py                # Split text into 300-700 token chunks
    │   ├── embeddings.py             # Embed chunks with Cohere
    │   └── db_operations.py          # Upsert documents and chunks to DB
    │
    └── tests/                        # Unit tests for worker functions (see TESTING_GUIDE.md)
```

---

## 📚 Understanding the Repository Structure

This section explains what each major folder does and why it exists. Read this to understand how the pieces fit together.

### 🗄️ `supabase/` — Database Schema & Migrations

**What it is:** This folder contains all database-related code — table definitions, indexes, and schema changes.

**What it does:**
- Defines the 5 core tables (`employees`, `projects`, `employee_projects`, `documents`, `chunks`, `audit_queries`)
- Creates indexes for fast searches (especially the HNSW index for vector search)
- Manages schema changes over time (migrations)

**Why we need it:**
- Database is the **single source of truth** for all data
- Stores document metadata, user permissions, and vector embeddings
- Migrations ensure everyone's database has the same structure

**Key files:**
- `migrations/20251002234351_updated_db.sql` — Creates all tables and indexes (run this first!)
- `README.md` — Complete guide to the database with examples and troubleshooting

**When you use it:**
- **Setup:** Run migrations once when setting up the project (`npx supabase db push`)
- **Development:** Add new migration files when you need to change the schema
- **Reference:** Check README.md when writing queries or debugging access control

---

### 📦 `apps/` — All Application Code

**What it is:** This folder contains both the **frontend** (user interface) and **backend** (API server).

**Why it's called "apps":**
- Modern projects often have multiple apps (web, mobile, admin panel, etc.)
- Keeps related applications organized in one place
- In our case, we have 2 apps: `web` (frontend) and `backend` (API)

**Think of it like this:**
```
apps/
├── web/       ← What users see and interact with (browser)
└── backend/   ← What powers the search and handles data (server)
```

---

### 🌐 `apps/web/` — Frontend (User Interface)

**What it is:** The website users interact with. Built with **Next.js 14** (a React framework).

**What it does:**
1. **Shows the chat interface** where users type questions
2. **Displays answers** from the AI with source citations
3. **Handles login/signup** via Supabase Auth
4. **Calls the backend API** to search for documents

**How it works:**
```
User types question
  → Frontend sends to backend API
  → Backend returns answer + sources
  → Frontend displays results
```

**Main folders inside `apps/web/`:**

#### `app/` — Page Definitions (Next.js App Router)
- `layout.tsx` — Root layout (wraps entire app with font, theme, auth provider)
- `page.tsx` — Main app interface (chat, search, navigation tabs)
- `login/page.tsx` — Login page
- `signup/page.tsx` — Signup page
- `globals.css` — Global styles (colors, fonts, Tailwind base)

**Think of `app/` as the "pages" of your website.**

#### `components/` — Reusable UI Pieces
- **Core components:**
  - `ChatInput.tsx` — Text box + Send button for asking questions
  - `MessageList.tsx` — Shows conversation history (user questions + AI answers)
  - `SourcesList.tsx` — Displays document citations with links
  - `Navbar.tsx` — Top navigation bar
  - `theme-provider.tsx` — Dark mode / light mode switching

- **UI primitives (`ui/` folder):**
  - Pre-built components from shadcn/ui library
  - Examples: `button.tsx`, `input.tsx`, `card.tsx`, `table.tsx`
  - Used throughout the app for consistent design

**Think of `components/` as Lego blocks you can reuse everywhere.**

#### `lib/` — Helper Functions & API Clients
- `utils.ts` — Utility functions (e.g., `cn()` for combining CSS classes)
- `supabase.ts` — Supabase client (handles login, signup, JWT tokens)
- `api.ts` — Functions to call backend API (`searchKnowledge()`, `getDocMetadata()`)

**Think of `lib/` as your toolbox of helper functions.**

#### `types/` — TypeScript Type Definitions
- `index.ts` — Defines data shapes (e.g., what a `SearchResponse` looks like)

**Example:**
```typescript
type SearchResponse = {
  answer: string
  chunks: Chunk[]
  used_doc_ids: number[]
}
```

**Why we need types:** TypeScript catches errors before code runs (e.g., typos in field names).

#### `public/` — Static Files
- Images, logos, icons that don't change
- Accessed directly via URL (e.g., `/logo.png`)

#### Configuration Files
- `package.json` — Lists all npm packages (React, Next.js, Tailwind, etc.)
- `tsconfig.json` — TypeScript compiler settings
- `next.config.mjs` — Next.js configuration
- `.env.local` — Environment variables (API URLs, Supabase keys) — **NEVER commit this!**

---

### ⚙️ `apps/backend/` — Backend (API Server)

**What it is:** The API server that powers search, authentication, and data retrieval. Built with **FastAPI** (Python framework).

**What it does:**
1. **Verifies user identity** (checks JWT tokens from Supabase)
2. **Enforces access control** (ensures users only see documents they're allowed to)
3. **Searches the database** using vector similarity (pgvector)
4. **Calls AI services** (Cohere for embeddings/reranking, Groq for LLM)
5. **Returns answers with citations** to the frontend
6. **Logs all queries** to `audit_queries` table

**How it works:**
```
Frontend sends: "How do I deploy Atlas?"
  ↓
Backend:
  1. Verify JWT → Get user's projects
  2. Embed query → Search database (with ACL filter)
  3. Rerank results → Call LLM
  4. Return answer + citations
```

**Main folders inside `apps/backend/`:**

#### `app/main.py` — Application Entry Point
- Creates the FastAPI app
- Sets up CORS (allows frontend to call backend)
- Registers API routes (`/api/search`, `/api/docs/:id`)
- Initializes database connection pool on startup

**Think of this as the "main" function that starts the server.**

#### `app/api/routes/` — API Endpoints
- `search.py` — `POST /api/search` (main RAG search endpoint)
- `docs.py` — `GET /api/docs/:doc_id` (get document metadata)

**These are the URLs the frontend calls.**

#### `app/services/` — Business Logic (Core Functions)
This is where the **real work** happens. Each service has a specific job:

- **`auth.py`** — Authentication & Authorization
  - `verify_jwt(token)` → Validates Supabase JWT, returns `user_id`
  - `get_user_projects(user_id)` → Queries database for user's projects

- **`embeddings.py`** — Convert Text to Vectors
  - `embed_query(text)` → Calls Cohere API, returns 1024-dim vector
  - Example: `"How do I deploy?"` → `[0.12, -0.08, 0.34, ...]`

- **`retrieval.py`** — Search & Rerank
  - `run_vector_search(qvec, projects, top_k=200)` → Queries pgvector with ACL filter
  - `rerank(chunks, query)` → Calls Cohere reranker, returns top 12 most relevant

- **`llm.py`** — Generate Answers
  - `call_llm(query, chunks)` → Calls Groq (Llama 3.3 or Mixtral, ChatGPT-OSS), generates answer

- **`audit.py`** — Logging
  - `audit_log(user_id, query, used_doc_ids)` → Inserts row into `audit_queries` table

**Think of services as specialist workers:**
- `auth.py` = Security guard (who's allowed in?)
- `embeddings.py` = Translator (text → numbers)
- `retrieval.py` = Librarian (find relevant documents)
- `llm.py` = Writer (synthesize answer)
- `audit.py` = Recordkeeper (log everything)

#### `app/db/client.py` — Database Connection
- Creates connection pool to Postgres (using asyncpg)
- Provides helper functions: `fetch()`, `execute()`

**Think of this as the phone line to the database.**

#### `app/models/schemas.py` — Request/Response Models
- Pydantic models define API input/output shapes
- Example: `SearchRequest`, `SearchResponse`, `Chunk`, `DocMetadata`

**Why we need this:** FastAPI auto-validates requests and generates API docs.

#### Configuration Files
- `requirements.txt` — Lists all Python packages (FastAPI, asyncpg, cohere, groq, etc.)
- `Dockerfile` — Instructions to build backend as Docker container
- `.env` — Environment variables (database URL, API keys) — **NEVER commit this!**

---

### 🔧 `workers/` — Offline Ingestion Pipeline

**What it is:** Python scripts that run **separately** from the web server to ingest documents.

**What it does:**
1. **Fetches pages from Notion** (via Notion API)
2. **Converts to Markdown** (cleans up formatting, preserves structure)
3. **Chunks text** (splits into 300-700 token pieces)
4. **Generates embeddings** (calls Cohere to convert text → vectors)
5. **Saves to database** (`documents` and `chunks` tables)

**Why workers are separate from backend:**
- **Backend** = Real-time (responds to user queries in <2 seconds)
- **Workers** = Batch processing (takes 5-30 minutes to ingest 100 pages)
- Running ingestion in the backend would block user requests
- Workers run on a schedule (every 6 hours via cron/Lambda/Cloud Scheduler)

**How it works:**
```
Cron triggers: python workers/ingest_notion.py --notion-db-id abc123
  ↓
1. Fetch Notion pages
2. For each page:
   a. Convert blocks → Markdown
   b. Chunk into 300-700 tokens
   c. Embed each chunk (Cohere)
   d. Upsert to database
  ↓
Database now has searchable content
  ↓
Users can search via frontend → backend
```

**Main files inside `workers/`:**

#### `ingest_notion.py` — Main Script
- Entry point: Run this to sync Notion data
- Usage: `python ingest_notion.py --notion-db-id <your-id>`
- Orchestrates the full pipeline

#### `lib/notion_client.py` — Notion API Wrapper
- `list_notion_pages(db_id)` → Fetches all pages from a Notion database
- `fetch_blocks(page_id)` → Gets content blocks (paragraphs, headings, lists, etc.)

#### `lib/normalizer.py` — Convert Notion → Markdown
- `normalize_to_markdown(blocks)` → Converts Notion blocks to clean Markdown
- Preserves headings, tables, code blocks
- Extracts `heading_path` (e.g., `['Runbook', 'Incidents', 'Step 1']`)

**Why Markdown?** Easy to chunk, preserves structure, human-readable.

#### `lib/chunker.py` — Split Text into Chunks
- `chunk_markdown(md)` → Splits long documents into 300-700 token pieces
- Adds 50-token overlap (so context isn't lost between chunks)

**Why chunk?** LLMs have token limits. Sending 50 pages would fail. Chunks = bite-sized pieces.

#### `lib/embeddings.py` — Generate Vectors
- `embed(text)` → Calls Cohere API, returns 1024-dim vector
- Same embedding model as backend (consistency is critical!)

#### `lib/db_operations.py` — Database Writes
- `upsert_document(source_id, title, project_id, ...)` → Insert or update `documents` table
- `insert_chunk(doc_id, text, embedding, ...)` → Insert into `chunks` table

**"Upsert" = Update if exists, Insert if new.** Prevents duplicates when re-running worker.

---

### 🔧 Root Configuration Files

#### `.env.example` — Environment Variable Template
- Shows what variables you need (without actual secrets)
- Copy to `.env` and fill in your API keys
- **NEVER commit `.env` to git!**

#### `.gitignore` — Files Git Should Ignore
- `.env`, `node_modules/`, `__pycache__/`, `.next/`, `venv/`
- Prevents secrets and dependencies from being committed

#### `docker-compose.yml` — Local Development Setup
- Runs backend + Postgres in Docker containers
- Frontend runs outside Docker (better dev experience)
- Optional: Can run everything locally without Docker

---

## 🧩 How Everything Connects (Big Picture)

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                          │
│                                                                 │
│  apps/web/ (Frontend)                                          │
│  - User types question in ChatInput.tsx                        │
│  - lib/api.ts sends POST to backend                            │
│  - MessageList.tsx displays answer                             │
│  - SourcesList.tsx shows citations                             │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP Request (with JWT token)
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                      apps/backend/ (API Server)                 │
│                                                                 │
│  1. main.py receives request                                   │
│  2. api/routes/search.py handles /api/search                   │
│  3. services/auth.py verifies JWT                              │
│  4. services/embeddings.py converts query → vector             │
│  5. services/retrieval.py searches database (with ACL)         │
│  6. services/llm.py generates answer                           │
│  7. services/audit.py logs query                               │
│  8. Returns JSON response                                      │
└────────────────────┬────────────────────────────────────────────┘
                     │ SQL Queries
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                   supabase/ (Database)                          │
│                                                                 │
│  - employees, projects, employee_projects (ACL)                │
│  - documents (metadata)                                         │
│  - chunks (searchable text + embeddings)                       │
│  - audit_queries (logs)                                         │
└─────────────────────────────────────────────────────────────────┘
                     ↑
                     │ Upsert documents & chunks
                     │
┌─────────────────────────────────────────────────────────────────┐
│                  workers/ (Ingestion Pipeline)                  │
│                                                                 │
│  1. ingest_notion.py runs (scheduled via cron)                 │
│  2. lib/notion_client.py fetches pages                         │
│  3. lib/normalizer.py converts to Markdown                     │
│  4. lib/chunker.py splits into pieces                          │
│  5. lib/embeddings.py generates vectors                        │
│  6. lib/db_operations.py saves to database                     │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight:**
- **Frontend** and **Backend** run 24/7 (respond to users in real-time)
- **Workers** run periodically (scheduled jobs to ingest new content)
- **Database** is the shared state (everyone reads/writes here)

---

### Notes on UI Components

**Core Components:**
- `ChatInput.tsx`, `MessageList.tsx`, `SourcesList.tsx` — Core RAG interface
- `login/page.tsx`, `signup/page.tsx` — Authentication
- `Navbar.tsx`, `theme-provider.tsx` — Navigation and theming
- `ui/*` — All shadcn/ui primitives (used throughout)

**Optional Components:**
- `documents-tab.tsx` — Browse all documents (connects to `documents` table)
- `projects-tab.tsx` — View project memberships (connects to `employee_projects` table)

Some components from initial UI prototyping may not be used and can be removed as needed.

---

## 🔗 How Components Connect

### 1. User Login Flow

```
User clicks "Login" 
  → app/login/page.tsx
  → lib/supabase.ts: supabase.auth.signInWithPassword(email, password)
  → Supabase Auth validates credentials
  → Returns JWT token
  → Token stored in browser (Supabase handles this)
  → Redirect to main app (app/page.tsx)
```

### 2. RAG Search Flow (End-to-End)

```
User types "How do I deploy Atlas?" 
  → components/ChatInput.tsx captures input
  → Calls lib/api.ts: searchKnowledge(query, jwt)
  → 
  
Frontend (lib/api.ts):
  fetch('http://localhost:8000/api/search', {
    method: 'POST',
    headers: { Authorization: `Bearer ${jwt}` },
    body: JSON.stringify({ query, top_k: 12 })
  })
  →

Backend (apps/backend/app/api/routes/search.py):
  1. Extract JWT from Authorization header
  2. services/auth.py: verify_jwt(token) → user_id
  3. services/auth.py: get_user_projects(user_id) → ['Atlas', 'Phoenix']
  4. services/embeddings.py: embed_query(query) → 1024-dim vector
  5. services/retrieval.py: run_vector_search(vector, projects, top_k=200)
     → Runs SQL with pgvector:
        WHERE visibility='Public' OR project_id IN ('Atlas','Phoenix')
        ORDER BY embedding <=> query_vector
     → Returns 200 candidate chunks
  6. services/retrieval.py: rerank(chunks, query) via Cohere
     → Returns top 12 most relevant chunks
  7. services/llm.py: call_llm(query, chunks) via Groq
     → Generates answer with citations
  8. services/audit.py: audit_log(user_id, query, doc_ids)
     → Inserts into audit_queries table
  9. Return JSON: { answer, chunks, used_doc_ids }
  →

Frontend (components/MessageList.tsx):
  Receives response
  → Displays answer in chat bubble
  → components/SourcesList.tsx shows citations
  → User clicks citation → opens Notion page
```

### 3. Document Ingestion Flow (Offline)

```
Cron job triggers (or manual run):
  python workers/ingest_notion.py --notion-db-id abc123
  →

workers/ingest_notion.py:
  1. lib/notion_client.py: list_notion_pages(db_id)
     → Fetches pages from Notion API
  2. For each page:
     a. lib/notion_client.py: fetch_blocks(page_id)
        → Gets all blocks (paragraphs, headings, lists, etc.)
     b. lib/normalizer.py: normalize_to_markdown(blocks)
        → Converts to clean Markdown
        → Extracts heading_path (e.g., ['Runbook', 'Incidents'])
     c. lib/chunker.py: chunk_markdown(md)
        → Splits into 300-700 token pieces with 50-token overlap
     d. Compute content_hash (MD5 of markdown)
        → If hash unchanged from previous run → skip re-embedding
     e. lib/db_operations.py: upsert_document(...)
        → INSERT ... ON CONFLICT (source_external_id) DO UPDATE
        → Returns doc_id
     f. For each chunk:
        - lib/embeddings.py: embed(chunk.text) via Cohere
          → Returns 1024-dim vector
        - lib/db_operations.py: insert_chunk(doc_id, chunk, embedding)
          → INSERT into chunks table
  →

Database now has:
  - 1 row in documents table (metadata)
  - N rows in chunks table (searchable text + embeddings)
```

### 4. Permission Check (How ACL Works)

```
User Sarah logs in (employee_id: 550e8400-...)
  → Backend queries:
     SELECT project_id FROM employee_projects 
     WHERE employee_id = '550e8400-...'
  → Result: ['Atlas', 'Phoenix']
  
User asks question:
  → Backend runs vector search with ACL:
     SELECT c.text, d.title, d.uri
     FROM chunks c
     JOIN documents d ON d.doc_id = c.doc_id
     WHERE d.deleted_at IS NULL
       AND (
         d.visibility = 'Public'                    -- Public docs
         OR d.project_id = ANY(ARRAY['Atlas','Phoenix'])  -- Sarah's projects
       )
     ORDER BY c.embedding <=> query_vector
     LIMIT 200
  
  → Only chunks from allowed documents are returned
  → LLM never sees restricted content
```

---

## 🧪 Testing

### What is Unit Testing?

**Unit testing** means testing individual functions in isolation to ensure they work correctly. Instead of running the entire application, you test one function at a time with known inputs and verify the outputs.

**Example:**
```python
# Function to test
def embed_query(text: str) -> list[float]:
    # Calls Cohere API to embed text
    return cohere.embed([text])[0]

# Unit test
def test_embed_query():
    # Test with known input
    result = embed_query("hello world")
    
    # Verify output
    assert len(result) == 1024  # Cohere v3 returns 1024 dimensions
    assert all(isinstance(x, float) for x in result)
    assert result != [0] * 1024  # Not all zeros
```

**Benefits:**
- Catch bugs early (before they reach production)
- Verify each function works correctly in isolation
- Make refactoring safer (tests catch breaking changes)
- Document expected behavior (tests serve as examples)

### Testing Strategy

**Backend (Python):**
```bash
cd apps/backend
pytest tests/ -v

# Test individual services with mocked dependencies:
# - tests/test_auth.py: verify_jwt(), get_user_projects()
# - tests/test_embeddings.py: embed_query() with mocked Cohere
# - tests/test_retrieval.py: run_vector_search() with test database
# - tests/test_llm.py: call_llm() with mocked Groq
```

**Frontend (TypeScript):**
```bash
cd apps/web
npm test

# Test components with React Testing Library:
# - ChatInput.test.tsx: user can type and submit
# - MessageList.test.tsx: messages render correctly
# - SourcesList.test.tsx: citations display with links
```

### Manual Testing Checklist

```bash
# 1. Backend health check
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# 2. Database has data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM chunks;"
# Expected: > 0

# 3. Full flow test
# - Open http://localhost:3000
# - Log in with test account
# - Type: "What is Atlas?"
# - Verify: Answer appears + 3-5 sources shown
# - Click source → Notion page opens in new tab

# 4. Permission test
# - Create user with no projects
# - Log in as that user
# - Search should only return Public documents
```

---

## 🚀 Deployment

### Containerized Deployment

Both frontend and backend are deployed as Docker containers to the same cloud region for low latency.

**Step 1: Build Docker Images**

```bash
# Build frontend
cd apps/web
docker build -t rag-frontend:latest .

# Build backend
cd ../backend
docker build -t rag-backend:latest .
```

**Step 2: Push to Container Registry**

```bash
# Tag for your registry (Docker Hub, ECR, GCR, etc.)
docker tag rag-frontend:latest <your-registry>/rag-frontend:latest
docker tag rag-backend:latest <your-registry>/rag-backend:latest

# Push
docker push <your-registry>/rag-frontend:latest
docker push <your-registry>/rag-backend:latest
```

**Step 3: Deploy to Cloud**

**Option A: AWS (ECS/Fargate)**
```bash
# Deploy using ECS task definitions
# Frontend: Public ALB → Port 3000
# Backend: Internal ALB → Port 8000
# Both in same VPC for fast communication
```

**Option B: Google Cloud (Cloud Run)**
```bash
gcloud run deploy rag-frontend \
  --image <your-registry>/rag-frontend:latest \
  --region us-central1

gcloud run deploy rag-backend \
  --image <your-registry>/rag-backend:latest \
  --region us-central1 \
  --no-allow-unauthenticated  # Internal only
```

**Option C: Azure (Container Apps)**
```bash
az containerapp create \
  --name rag-frontend \
  --image <your-registry>/rag-frontend:latest \
  --resource-group myResourceGroup
```

**Step 4: Configure Environment Variables**

Set environment variables in your cloud provider's dashboard:

**Frontend:**
- `NEXT_PUBLIC_API_URL` (internal backend URL)
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

**Backend:**
- `DATABASE_URL`
- `SUPABASE_JWT_SECRET`
- `COHERE_API_KEY`
- `GROQ_API_KEY`
- `CORS_ORIGINS`

**Step 5: Deploy Workers**

Workers run as scheduled jobs (not web servers):

**AWS Lambda + EventBridge:**
```bash
# Package workers as Lambda function
cd workers
zip -r function.zip .
aws lambda create-function --function-name ingest-notion --runtime python3.11 --handler ingest_notion.handler --zip-file fileb://function.zip

# Schedule with EventBridge (every 6 hours)
aws events put-rule --schedule-expression "rate(6 hours)" --name ingest-schedule
```

**Google Cloud Run Jobs:**
```bash
gcloud run jobs create ingest-notion \
  --image <your-registry>/workers:latest \
  --region us-central1

# Schedule with Cloud Scheduler
gcloud scheduler jobs create http ingest-schedule \
  --schedule="0 */6 * * *" \
  --uri="https://run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT/jobs/ingest-notion:run"
```

### Database

Database is already hosted on Supabase. No additional deployment needed — just ensure your backend and workers have the correct `DATABASE_URL`.

---

## 🐛 Troubleshooting

### "CORS error when calling backend"

**Cause:** Backend's `CORS_ORIGINS` doesn't include frontend URL.

**Fix:**
```bash
# In apps/backend/.env
CORS_ORIGINS=http://localhost:3000,https://yourapp.com
```

### "JWT verification failed"

**Cause:** Wrong `SUPABASE_JWT_SECRET`.

**Fix:**
1. Go to Supabase Dashboard → Settings → API
2. Copy "JWT Secret" (not "anon public" key)
3. Paste into `apps/backend/.env`:
   ```bash
   SUPABASE_JWT_SECRET=your-actual-jwt-secret
   ```

### "No results returned from search"

**Possible causes:**

1. **No chunks in database:**
   ```bash
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM chunks;"
   # If 0: Run worker to ingest data
   ```

2. **User has no project access:**
   ```sql
   -- Check user's projects
   SELECT project_id FROM employee_projects WHERE employee_id = 'user-id';
   
   -- Add user to project
   INSERT INTO employee_projects (employee_id, project_id, role) 
   VALUES ('user-id', 'Atlas', 'viewer');
   ```

3. **All docs are Private and user not in any project:**
   ```sql
   -- Make one doc Public for testing
   UPDATE documents SET visibility = 'Public' WHERE doc_id = 1;
   ```

### "pgvector extension not found"

**Cause:** Postgres doesn't have pgvector installed.

**Fix:**
```sql
-- In Supabase SQL editor
CREATE EXTENSION IF NOT EXISTS vector;
```

### "Cohere API rate limit exceeded"

**Cause:** Free tier limits (100 requests/minute for embeddings).

**Fix:**
1. Upgrade Cohere plan, or
2. Add rate limiting in `workers/lib/embeddings.py`:
   ```python
   import time
   time.sleep(0.1)  # Between embed calls
   ```

### "Worker fails with 'Notion API error'"

**Common issues:**

1. **Wrong Notion API key:**
   - Get integration token from [notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Must grant integration access to your database

2. **Database not shared with integration:**
   - Open Notion database
   - Click "•••" → "Connections" → Add your integration

3. **Rate limits:**
   - Notion API: 3 requests/second
   - Add delays in `workers/lib/notion_client.py`

---

## 📚 Additional Resources

- **Supabase:** [docs.supabase.com](https://docs.supabase.com)
- **FastAPI:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Next.js:** [nextjs.org/docs](https://nextjs.org/docs)
- **pgvector:** [github.com/pgvector/pgvector](https://github.com/pgvector/pgvector)
- **Cohere:** [docs.cohere.com](https://docs.cohere.com)
- **Groq:** [console.groq.com/docs](https://console.groq.com/docs)
- **shadcn/ui:** [ui.shadcn.com](https://ui.shadcn.com)

---

## 📋 API Reference

### POST /api/search

Search for documents and generate an answer.

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
  "answer": "To deploy the Atlas API, follow these steps: 1. Run `make deploy`...",
  "chunks": [
    {
      "doc_id": 123,
      "title": "Atlas Deploy Guide",
      "snippet": "To deploy Atlas API, first ensure all environment variables...",
      "uri": "https://notion.so/abc123",
      "score": 0.87
    }
  ],
  "used_doc_ids": [123, 456, 789]
}
```

### GET /api/docs/:doc_id

Get metadata for a specific document (with ACL check).

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "doc_id": 123,
  "title": "Atlas Deploy Guide",
  "project_id": "Atlas",
  "visibility": "Private",
  "uri": "https://notion.so/abc123",
  "updated_at": "2025-01-15T10:30:00Z",
  "language": "en"
}
```

**Error:** 403 if user doesn't have access to this document.

---

## 🔮 Future Enhancements

Potential features for future versions:

- **Additional Data Sources:** Google Drive, Confluence, Slack, GitHub
- **Hybrid Search:** Combine vector search with BM25 keyword search for better accuracy
- **Multi-turn Conversations:** Chat history and follow-up questions with context
- **Fine-grained Permissions:** User-level and group-level document access controls
- **Analytics Dashboard:** Query trends, popular documents, user activity metrics
- **Feedback Loop:** Thumbs up/down on answers to improve retrieval quality
- **Document Upload:** Manual file uploads (PDFs, DOCX, TXT) without external integrations
- **Smart Summaries:** Auto-generate summaries for long documents
- **Team Collaboration:** Share searches, annotate results, collaborative notes
- **Advanced Filters:** Filter by date range, document type, project, author
- **Mobile App:** iOS/Android native apps for on-the-go access
- **Voice Search:** Ask questions via voice input
- **Export Results:** Export search results and answers to PDF/Markdown

---

