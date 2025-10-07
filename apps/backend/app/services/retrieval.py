#DANIYAH

"""
Retrieval Service

This module handles:
- Vector similarity search using pgvector
- Access control filtering (ACL)
- Reranking results using Cohere
"""

from typing import List, Dict, Any
import os
import cohere
from app.db.client import fetch_all

#from dotenv import load_dotenv #for load env. variables
#load_dotenv()


async def run_vector_search(
    query_vector: List[float],
    user_projects: List[str],
    user_id: str,
    top_k: int = 200
) -> List[Dict[str, Any]]:

    """
    Searches the database for similar chunks using vector similarity + ACL filtering.
    Includes both documents AND handovers that the user has access to.
    Uses the connection pool for efficient database access.
    """

    # 1. Validate vector dimensions
    if len(query_vector) != 1024:
        raise ValueError(f"Query vector must have 1024 dimensions, got {len(query_vector)}")

    # 2. Run pgvector similarity search with ACL filter
    # UNION results from both documents and handovers
    try:
        sql = """
        (
            -- Search chunks from documents
            SELECT
                c.chunk_id,
                c.doc_id,
                NULL::bigint as handover_id,
                d.title,
                c.text,
                d.uri,
                c.heading_path,
                'document' as source_type,
                1 - (c.embedding <=> $1::vector) AS score
            FROM chunks c
            JOIN documents d ON d.doc_id = c.doc_id
            WHERE d.deleted_at IS NULL
              AND c.doc_id IS NOT NULL
              AND (
                d.visibility = 'Public'
                OR d.project_id = ANY($2)
              )
        )
        UNION ALL
        (
            -- Search chunks from handovers (user must be sender, recipient, or CC'd)
            SELECT
                c.chunk_id,
                NULL::bigint as doc_id,
                c.handover_id,
                h.title,
                c.text,
                'handover://' || h.handover_id as uri,
                c.heading_path,
                'handover' as source_type,
                1 - (c.embedding <=> $1::vector) AS score
            FROM chunks c
            JOIN handovers h ON h.handover_id = c.handover_id
            WHERE c.handover_id IS NOT NULL
              AND (
                h.from_employee_id = $4
                OR h.to_employee_id = $4
                OR $4 = ANY(h.cc_employee_ids)
              )
        )
        ORDER BY score DESC
        LIMIT $3
        """

        # Convert Python list to PostgreSQL array format
        # [0.1, 0.2, ...] → '[0.1,0.2,...]'
        vector_str = '[' + ','.join(map(str, query_vector)) + ']'

        rows = await fetch_all(sql, vector_str, user_projects, top_k, user_id)

        # 3. Format results
        results = []
        for row in rows:
            results.append({
                "chunk_id": row["chunk_id"],
                "doc_id": row["doc_id"],
                "handover_id": row["handover_id"],
                "title": row["title"],
                "text": row["text"],
                "uri": row["uri"],
                "heading_path": row["heading_path"],
                "source_type": row["source_type"],
                "score": float(row["score"]),
            })

        return results

    except Exception as e:
        raise Exception(f"Database query failed: {e}")


#ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
#ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
    """
    Searches the database for similar chunks using vector similarity + ACL filtering.

    Args:
        query_vector (List[float]): The embedded query (1024-dimensional vector)
            Example: [0.023, -0.15, 0.091, ..., 0.18]

        user_projects (List[str]): List of project IDs the user has access to
            Example: ["Atlas", "Phoenix"]
            Example (no projects): []

        top_k (int): Maximum number of results to return (default: 200)
            We oversample (200) because we'll rerank later to get top 12
            Example: 200

    Returns:
        List[Dict[str, Any]]: List of matching chunks with metadata
            Example:
            [
                {
                    "chunk_id": 1,
                    "doc_id": 42,
                    "title": "Atlas Deploy Guide",
                    "text": "To deploy Atlas API, first ensure...",
                    "uri": "https://notion.so/abc123",
                    "score": 0.87,
                    "heading_path": ["Deployment", "Steps"]
                },
                {
                    "chunk_id": 5,
                    "doc_id": 43,
                    "title": "Company Handbook",
                    "text": "All deployments must follow...",
                    "uri": "https://notion.so/def456",
                    "score": 0.72,
                    "heading_path": ["DevOps", "Deployment"]
                }
            ]

    Raises:
        Exception: If database query fails

    What This Does:
        1. Connects to the database
        2. Runs a pgvector similarity search with ACL filter
        3. Finds chunks with vectors close to query_vector
        4. ONLY returns chunks from documents the user can access
        5. Orders by similarity score (cosine distance)
        6. Returns top_k results

    SQL Query Template:
        SELECT
            c.chunk_id,
            c.doc_id,
            d.title,
            c.text,
            d.uri,
            c.heading_path,
            1 - (c.embedding <=> %s::vector) AS score
        FROM chunks c
        JOIN documents d ON d.doc_id = c.doc_id
        WHERE d.deleted_at IS NULL
          AND (
            d.visibility = 'Public'
            OR d.project_id = ANY(%s)
          )
        ORDER BY c.embedding <=> %s::vector
        LIMIT %s

    Query Parameters:
        %s (1st): query_vector (the user's embedded question)
        %s (2nd): user_projects (array of project IDs)
        %s (3rd): query_vector (same as first, for ORDER BY)
        %s (4th): top_k (limit number of results)

    Why We Need This:
        - This is the CORE of the RAG system
        - Finds relevant content from the knowledge base
        - Enforces access control at the database level
        - Uses pgvector's HNSW index for fast approximate nearest neighbor search

    Access Control Logic:
        User can see chunk IF:
            - Document is Public (visibility = 'Public')
            OR
            - Document belongs to a project the user is in (project_id IN user_projects)

    Example Scenario:
        - User Sarah belongs to ["Atlas", "Phoenix"]
        - Query: "How do I deploy?"
        - Database has:
          • Chunk 1 → Doc 1 (Atlas Deploy, Private, project=Atlas) → ✅ Returned
          • Chunk 2 → Doc 2 (Handbook, Public) → ✅ Returned
          • Chunk 3 → Doc 3 (Bolt API, Private, project=Bolt) → ❌ Filtered out
        - Result: [Chunk 1, Chunk 2]

    pgvector Operators:
        - <=> : Cosine distance (smaller = more similar)
        - 1 - (x <=> y) : Convert distance to similarity score (higher = better)
        - ORDER BY x <=> y : Sort by similarity (closest first)

    Why top_k = 200?
        - Initial search is fast but not perfect (approximate nearest neighbor)
        - We oversample to 200 candidates
        - Then use Cohere reranker to pick the best 12
        - Reranker is more accurate but slower (can't run on all chunks)

    Vector Dimensions:
        - Must match embedding model: Cohere v3 = 1024 dimensions
        - Database schema uses VECTOR(1024)
        - If dimensions don't match, query will fail

    Performance Notes:
        - HNSW index makes this fast (~10-50ms for millions of chunks)
        - Without index, would be O(n) scan (very slow!)
        - ACL filter is applied BEFORE vector search (efficient)

    Dependencies:
        - Database connection (from app.db.client)
        - pgvector extension enabled in Postgres
        - HNSW index on chunks.embedding column

    Implementation Hints:
        - Use parameterized queries (prevent SQL injection)
        - Convert query_vector to proper format for pgvector
        - Convert user_projects list to PostgreSQL array format
        - Handle empty user_projects (user with no projects)

    Edge Cases:
        - User has no projects → only see Public docs
        - No results found → return empty list
        - Query vector wrong size → database will error
    """
    #raise NotImplementedError("TODO: Implement pgvector search with ACL")

#ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
#ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ

async def rerank(chunks: List[Dict[str, Any]], query: str, top_k: int = 12) -> List[Dict[str, Any]]:
    """
    Reranks chunks using Cohere's reranker model for better relevance.
    """
    if not chunks:
        return []

    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        raise ValueError("Cohere API key not found in environment variables.")

    client = cohere.AsyncClient(api_key)

    try:
        # 1. Takes the 200 candidates from vector search
        documents = [c["text"] for c in chunks]

        # 2. Calls Cohere's rerank
        response = await client.rerank(
            query=query,
            documents=documents,
            model="rerank-english-v3.0",
            top_n=top_k
        )

        # point 3 and 4 
        reranked = []
        for r in response.results:
            idx = r.index
            chunk = chunks[idx].copy()
            chunk["rerank_score"] = r.relevance_score
            reranked.append(chunk)

        return reranked

    except Exception as e:
        raise Exception(f"Failed to rerank with Cohere API: {e}")
    

#ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ
#ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ


    """
    Reranks chunks using Cohere's reranker model for better relevance.

    Args:
        chunks (List[Dict[str, Any]]): Candidate chunks from vector search
            Example: [
                {"text": "To deploy Atlas...", "score": 0.87, ...},
                {"text": "Deployment process...", "score": 0.72, ...},
                ...
            ]
            Length: Usually 200 chunks from run_vector_search()

        query (str): The original user query
            Example: "How do I deploy the Atlas API?"

        top_k (int): Number of top results to return (default: 12)
            Example: 12

    Returns:
        List[Dict[str, Any]]: Reranked chunks (best matches first)
            Example: [
                {"text": "To deploy Atlas API...", "rerank_score": 0.95, ...},
                {"text": "Atlas deployment steps...", "rerank_score": 0.89, ...},
                ...
            ]
            Length: top_k items (12 by default)

    Raises:
        Exception: If Cohere API call fails

    What This Does:
        1. Takes the 200 candidates from vector search
        2. Calls Cohere's rerank API with:
           - query: user's question
           - documents: list of chunk texts
           - model: "rerank-english-v3.0"
           - top_n: 12 (how many to return)
        3. Cohere analyzes each chunk against the query
        4. Returns the 12 most relevant chunks
        5. Adds rerank_score to each chunk

    Example Usage:
        >>> chunks = run_vector_search(qvec, ["Atlas"], 200)  # 200 candidates
        >>> print(len(chunks))
        200
        >>> best_chunks = rerank(chunks, "How do I deploy?", 12)
        >>> print(len(best_chunks))
        12
        >>> print(best_chunks[0]["rerank_score"])
        0.95

    Why We Need This:
        - Vector search is fast but not perfect
        - It finds chunks with similar words, but might miss semantic matches
        - Reranker uses a more sophisticated model (cross-encoder)
        - Much better at understanding "does this chunk answer this question?"

    How It Improves Results:
        Example query: "How do I deploy?"

        Vector search might rank:
        1. "Deploy the frontend..." (score: 0.85) ← Generic
        2. "To deploy Atlas API..." (score: 0.83) ← Actually what user wants!

        Reranker fixes this:
        1. "To deploy Atlas API..." (score: 0.95) ← Moved to top!
        2. "Deploy the frontend..." (score: 0.71) ← Ranked lower

    Vector Search vs Reranking:
        - Vector search: Fast, approximate, embeddings compared by cosine similarity
        - Reranking: Slower, precise, deep model analyzes query + document together

    API Parameters:
        - query: The user's question
        - documents: List of texts to rank
        - model: "rerank-english-v3.0" (latest Cohere reranker)
        - top_n: How many results to return (12)

    API Response Format:
        {
          "results": [
            {
              "index": 5,           # Index in original documents list
              "relevance_score": 0.95
            },
            {
              "index": 12,
              "relevance_score": 0.89
            },
            ...
          ]
        }

    Why top_k = 12?
        - LLMs have token limits
        - 12 chunks ≈ 6,000-8,000 tokens (with context)
        - Leaves room for system prompt + user query + answer
        - More chunks = better context, but risk hitting token limit

    Dependencies:
        - cohere Python library
        - Environment variable: COHERE_API_KEY

    API Documentation:
        https://docs.cohere.com/docs/rerank-guide
        https://docs.cohere.com/reference/rerank

    Implementation Hints:
        - Extract just the text from chunks: [c["text"] for c in chunks]
        - Call Cohere rerank API
        - Map results back to original chunks using index
        - Preserve all original chunk metadata (doc_id, title, uri, etc.)
        - Add rerank_score field to each chunk

    Performance:
        - Reranking 200 chunks takes ~100-300ms
        - Much slower than vector search (~10ms)
        - But much more accurate!

    Testing:
        - Mock Cohere API in tests
        - Verify top_k chunks are returned
        - Verify chunks are reordered (not same order as input)
        - Verify rerank_score is added
    """
    #raise NotImplementedError("TODO: Implement Cohere reranking")