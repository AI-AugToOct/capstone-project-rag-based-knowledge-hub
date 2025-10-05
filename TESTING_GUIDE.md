# Testing Guide

## Overview

This guide shows **how to test each implementation** as you build the system. Each function has specific test criteria based on its expected behavior.

## Testing Philosophy

- ✅ **Use real APIs** when possible (embeddings, LLM, reranking) - you have API keys anyway
- ✅ **Use test database** for database functions - create test data once
- ✅ **Test one function at a time** - no dependencies on other unfinished modules
- ✅ **Clear pass/fail criteria** - from the table below

---

## Function Testing Reference.. we will add more later.

| Function              | Test With              | Verify                                    | Test File                  |
|-----------------------|------------------------|-------------------------------------------|----------------------------|
| `embed_query()`       | Real Cohere API        | 1024 dims, all floats, not all zeros      | `test_embeddings.py`       |
| `verify_jwt()`        | Test JWT token         | Returns user_id string                    | `test_auth.py`             |
| `get_user_projects()` | Test DB                | Returns list of strings                   | `test_auth.py`             |
| `run_vector_search()` | Test DB                | Returns list of dicts with correct keys   | `test_retrieval.py`        |
| `rerank()`            | Real Cohere API        | Returns top_k items with rerank_score     | `test_retrieval.py`        |
| `call_llm()`          | Real Groq API          | Returns non-empty string                  | `test_llm.py`              |
| `audit_log()`         | Test DB                | No errors, row inserted                   | `test_audit.py`            |
| `chunk_markdown()`    | Pure logic (no API)    | Returns chunks with text, order, tokens   | `test_chunker.py`          |
| `normalize_to_markdown()` | Pure logic         | Returns markdown + sections               | `test_normalizer.py`       |

---

## Quick Start

### 1. Install Test Dependencies

```bash
cd apps/backend
pip install pytest pytest-asyncio

cd ../../workers
pip install pytest
```

### 2. Set Environment Variables

Create `.env` file with your API keys:

```bash
# Required for tests
COHERE_API_KEY=your-cohere-key
GROQ_API_KEY=your-groq-key
DATABASE_URL=your-database-url
SUPABASE_JWT_SECRET=your-jwt-secret

# Optional test helpers
TEST_USER_ID=550e8400-e29b-41d4-a716-446655440000
TEST_JWT_TOKEN=your-test-jwt
```

### 3. Prepare Test Database (One-Time Setup)

```sql
-- Run this in Supabase SQL Editor

-- Create a test user
INSERT INTO employees (employee_id, email, display_name)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'test@example.com', 'Test User');

-- Create test projects
INSERT INTO projects (project_id, name)
VALUES ('Atlas', 'Atlas Project'), ('Phoenix', 'Phoenix Project');

-- Assign test user to projects
INSERT INTO employee_projects (employee_id, project_id, role)
VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'Atlas', 'viewer'),
  ('550e8400-e29b-41d4-a716-446655440000', 'Phoenix', 'viewer');

-- Create a test document
INSERT INTO documents (source_external_id, title, project_id, visibility, uri, content_hash, language)
VALUES ('test-doc-1', 'Test Document', 'Atlas', 'Private', 'https://notion.so/test', 'abc123', 'en');

-- Create test chunks (adjust doc_id based on your database)
INSERT INTO chunks (doc_id, text, embedding, heading_path, order_in_doc)
SELECT
  doc_id,
  'Test chunk 1',
  ARRAY[0.1]::vector(1024),
  ARRAY['Test'],
  0
FROM documents WHERE source_external_id = 'test-doc-1';
```

---

## Running Tests

### Backend Tests

```bash
cd apps/backend

# Test individual modules
pytest tests/test_embeddings.py -v
pytest tests/test_auth.py -v
pytest tests/test_retrieval.py -v
pytest tests/test_llm.py -v
pytest tests/test_audit.py -v

# Run all tests
pytest tests/ -v

# Run without capturing output (see print statements)
pytest tests/test_embeddings.py -v -s
```

### Worker Tests

```bash
cd workers

# Test individual modules
pytest tests/test_chunker.py -v
pytest tests/test_normalizer.py -v

# Run all tests
pytest tests/ -v
```

### Run Single Test

```bash
# Run one specific test function
pytest tests/test_embeddings.py::test_embed_query_basic -v
```

---

## Testing Workflow Example

### When implementing `embeddings.py`

**Step 1: Implement the function**
```python
# In apps/backend/app/services/embeddings.py
def embed_query(text: str) -> List[float]:
    # ... implementation
    return embedding
```

**Step 2: Run the test**
```bash
cd apps/backend
pytest tests/test_embeddings.py -v
```

**Step 3: Check results**
```
test_embed_query_basic PASSED ✅
test_embed_query_empty_string PASSED ✅
test_embed_query_none PASSED ✅

✅ embed_query() works! First 5 values: [0.123, -0.456, 0.789, ...]

==================== 3 passed in 2.1s ====================
```

**Step 4: If tests fail, debug**
```bash
# See detailed output
pytest tests/test_embeddings.py -v -s

# Check error messages
# Fix implementation
# Run tests again
```

---

## Common Test Scenarios

### Test with Mock Data (No DB/API Needed)

```python
# Example: Test chunker (pure logic)
def test_chunker():
    markdown = "# Test\n\nThis is a test."
    chunks = chunk_markdown(markdown)
    assert len(chunks) > 0  # ✅ Pass
```

### Test with Real API

```python
# Example: Test embeddings
def test_embeddings():
    vector = embed_query("test query")
    assert len(vector) == 1024  # ✅ Pass
```

### Test with Test Database

```python
# Example: Test vector search
def test_vector_search():
    test_vector = [0.1] * 1024
    results = run_vector_search(test_vector, ["Atlas"], top_k=10)
    assert isinstance(results, list)  # ✅ Pass
```

---

## Troubleshooting

### "No module named 'app'"

```bash
# Run from backend directory
cd apps/backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/test_embeddings.py -v
```

### "Database connection failed"

```bash
# Check DATABASE_URL is set
echo $DATABASE_URL

# Test connection manually
psql $DATABASE_URL -c "SELECT 1;"
```

### "Cohere API error"

```bash
# Check API key
echo $COHERE_API_KEY

# Test API manually
python -c "import cohere; print(cohere.Client('your-key').embed(texts=['test']))"
```

### "JWT verification failed"

You need a valid JWT token. Get one from Supabase:

```javascript
// In Supabase console or your frontend
const { data } = await supabase.auth.getSession()
console.log(data.session.access_token)  // Copy this
```

Then set in `.env`:
```
TEST_JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Module Testing Checklist

**Backend Services:**
- [ ] `embeddings.py` - embed_query() returns 1024-dim vector
- [ ] `auth.py` - verify_jwt() and get_user_projects() work
- [ ] `retrieval.py` - run_vector_search() and rerank() return correct format
- [ ] `llm.py` - call_llm() generates non-empty answer
- [ ] `audit.py` - audit_log() inserts to database without errors

**Workers:**
- [ ] `chunker.py` - chunk_markdown() splits text correctly
- [ ] `normalizer.py` - normalize_to_markdown() converts Notion blocks
- [ ] `embeddings.py` - embed_text() returns 1024-dim vector
- [ ] `db_operations.py` - upsert_document() and insert_chunk() work
- [ ] `notion_client.py` - list_notion_pages() and fetch_blocks() work

**Integration:**
- [ ] Full search endpoint works end-to-end
- [ ] Full ingestion pipeline works end-to-end

---

## Complete Test Session Example

```bash
# 1. Implement your function
# 2. Run the corresponding test
cd apps/backend
pytest tests/test_embeddings.py -v

# Output:
# test_embed_query_basic PASSED ✅
# test_embed_query_empty_string PASSED ✅
# test_embed_query_none PASSED ✅
#
# ✅ embed_query() works! First 5 values: [0.123, -0.456, ...]
#
# ==================== 3 passed in 2.1s ====================

# 3. Commit your working code
git add .
git commit -m "✅ Implement embed_query() - all tests passing"
git push
```

---

## Best Practices

1. **Test early, test often** - Don't wait until everything is done
2. **One function at a time** - Focus on making one test pass
3. **Use real APIs** - Catch integration issues early
4. **Read test failures carefully** - They tell you exactly what's wrong
5. **Keep test database clean** - Use consistent test data

---

## Next Steps

Once individual functions pass: (IF time permits, otherwise skip :) ) 

1. **Integration testing** - Test full search endpoint
2. **Pipeline testing** - Test complete Notion ingestion
3. **Edge case testing** - Empty queries, missing data, etc.
4. **Performance testing** - Measure response times
5. **End-to-end testing** - Test via frontend

