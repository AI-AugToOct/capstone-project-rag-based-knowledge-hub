# Archive

This folder contains **early exploratory work** that is not part of the V1 production system. These files are preserved for reference and potential future use.

## Contents

### `backend/` (Archived)
**Early RAG prototype** using FAISS for local vector storage.

**Why archived:**
- Uses FAISS (local file-based) instead of pgvector (Supabase)
- No authentication or access control
- No integration with Supabase Auth
- Different architecture than V1 spec

**What it has:**
- `rag_workflow.py` — Basic RAG flow (load docs → embed → search → LLM)
- `embedding_generator.py` — Sentence Transformers embeddings + FAISS index
- `document_loader.py` — Load PDFs, DOCX, TXT from local folder
- `notion_api.py` — Fetch Notion tasks (metadata only, not full pages)
- `main.py` — FastAPI endpoints (`/query`, `/upload`, `/notion-tasks`)

**Useful for:**
- Understanding early design decisions
- Reference implementation of basic RAG concepts
- Local testing without Supabase dependency

---

### `Code_asana.ipynb` (Archived)
**Asana integration exploration** — Fetches tasks from Asana API and converts them to LangChain documents.

**Why archived:**
- V1 focuses on **Notion only**
- Asana integration is planned for V2+

**What it does:**
```python
# Fetches tasks from Asana project
tasks = fetch_asana_tasks()  # gid, name, assignee, status, notes, due_on

# Converts to LangChain documents
documents = [Document(page_content=task['name'] + task['notes'], metadata=task) for task in tasks]

# Chunks with RecursiveCharacterTextSplitter (512 tokens, 50 overlap)
chunked_docs = splitter.split_documents(documents)
```

**Reuse for V2:**
- Pattern for multi-source ingestion
- Worker code to fetch Asana data
- Mapping Asana fields to our schema

---

### `jira.ipynb` (Archived)
**Jira integration exploration** — Fetches issues from Jira Cloud API with descriptions.

**Why archived:**
- V1 focuses on **Notion only**
- Jira integration is planned for V2+

**What it does:**
```python
# Fetches issues from Jira project (via JQL)
response = requests.get(f"https://{domain}.atlassian.net/rest/api/3/search/jql",
                        params={'jql': f'project = {project_key}'})

# Extracts: summary, status, priority, description, duedate, fixVersions
# Displays in tabulated format
```

**Reuse for V2:**
- Pattern for multi-source ingestion
- Worker code to fetch Jira data
- Mapping Jira fields to our schema

---

## When to Use Archive Files

**Use these files if:**
- You want to understand early design decisions
- You're implementing Asana/Jira connectors for V2+
- You need a simple local RAG demo without cloud dependencies
- You're researching alternative architectures

**Do NOT use these files for:**
- V1 production system (completely different architecture)
- Reference implementation of auth/ACL (not present in archived code)
- Embedding strategy (V1 uses Cohere, archived code uses sentence-transformers)

---

## Migration Notes

If you want to bring back Asana/Jira integrations in V2, follow this pattern:

### 1. Create Source Connector (`workers/lib/asana_client.py`)
```python
def list_asana_tasks(project_gid: str) -> list[dict]:
    # Fetch tasks from Asana API (similar to Code_asana.ipynb)
    # Return normalized task data
```

### 2. Map to Schema (`workers/ingest_asana.py`)
```python
# For each Asana task:
doc_id = upsert_document(
    source_external_id=f"asana_{task['gid']}",
    title=task['name'],
    project_id=detect_project_from_asana(task),  # Map Asana project → our project
    visibility='Private',  # Or 'Public' based on Asana workspace
    uri=f"https://app.asana.com/0/{project_gid}/{task['gid']}",
    content_hash=hash_content(task['notes'])
)

# Chunk and embed task description + notes
chunks = chunk_markdown(task['notes'])
for chunk in chunks:
    embed = embed_text(chunk.text)
    insert_chunk(doc_id, chunk.text, embed)
```

### 3. Add to Ingestion Pipeline
```bash
# Run alongside Notion ingestion
python workers/ingest_asana.py --project-gid 1211535446206848
```

---

## Questions?

- **V1 architecture:** See main [`README.md`](../README.md) and [`ARCHITECTURE.md`](../ARCHITECTURE.md)
- **Database schema:** See [`supabase/README.md`](../supabase/README.md)
- **Why archive these?** V1 spec requires different tech stack (Supabase pgvector + Cohere + Groq). Archived code uses FAISS + sentence-transformers + local files.
