"""
Embeddings Service for Workers

Converts document chunks to vector embeddings using Cohere.
Same as backend embeddings, but with input_type="search_document" instead of "search_query".
"""

from typing import List
import os


def embed_text(text: str) -> List[float]:
    """
    Converts a document chunk into a 1024-dimensional vector embedding.

    Args:
        text (str): The document chunk text to embed
            Example: "To deploy Atlas API, follow these steps: 1. Configure..."

    Returns:
        List[float]: A 1024-dimensional vector (list of 1024 floats)
            Example: [0.12, -0.08, 0.34, ..., -0.15, 0.22]

    Raises:
        ValueError: If text is empty or None
        Exception: If Cohere API call fails

    What This Does:
        1. Validates input text
        2. Gets Cohere API key from environment
        3. Calls Cohere embed API with:
           - model: "embed-english-v3.0" (1024 dimensions)
           - input_type: "search_document" (optimized for documents, NOT queries)
           - texts: [text]
        4. Extracts embedding from response
        5. Returns as list of floats

    Example Usage:
        >>> chunk = "To deploy Atlas API: 1. Configure environment..."
        >>> vector = embed_text(chunk)
        >>> print(len(vector))
        1024
        >>> print(vector[:3])
        [0.12, -0.08, 0.34]

    Difference from Backend's embed_query():
        - Backend uses input_type="search_query" (for user questions)
        - Workers use input_type="search_document" (for document chunks)
        - Cohere optimizes embeddings differently based on input_type
        - CRITICAL: Must use correct input_type for good search results!

    Why input_type Matters:
        - search_query: "How do I deploy Atlas?"
          → Optimized to match against documents

        - search_document: "To deploy Atlas API: 1. Configure..."
          → Optimized to be matched by queries

        - Using wrong type reduces search quality!

    Same Embedding Model:
        - Workers and backend MUST use same model (embed-english-v3.0)
        - Must have same dimensions (1024)
        - Otherwise vectors aren't comparable!

    API Parameters:
        - model: "embed-english-v3.0"
        - input_type: "search_document" (NOT "search_query"!)
        - texts: [text] (API accepts list, we send one)

    Example API Response:
        {
          "embeddings": [
            [0.12, -0.08, 0.34, ..., -0.15]
          ]
        }

    Rate Limiting:
        - Cohere free tier: 100 requests/minute
        - For large ingestion jobs, add delays
        - Or upgrade to paid plan

    Dependencies:
        - cohere Python library: pip install cohere
        - Environment variable: COHERE_API_KEY

    API Documentation:
        https://docs.cohere.com/docs/embeddings
        https://docs.cohere.com/reference/embed

    Implementation Hints:
        - import cohere
        - client = cohere.Client(os.getenv("COHERE_API_KEY"))
        - response = client.embed(
              texts=[text],
              model="embed-english-v3.0",
              input_type="search_document"  # Different from backend!
          )
        - return response.embeddings[0]

    Batch Embedding (optional optimization):
        - Cohere API can embed multiple texts at once
        - If embedding 100 chunks, send in batches of 96
        - Faster than 100 individual API calls

        def embed_batch(texts: List[str]) -> List[List[float]]:
            response = client.embed(
                texts=texts,  # Up to 96 texts
                model="embed-english-v3.0",
                input_type="search_document"
            )
            return response.embeddings

    Testing:
        - Mock Cohere API in tests
        - Verify returned vector has 1024 dimensions
        - Verify all elements are floats
        - Verify different texts → different embeddings
    """
    raise NotImplementedError("TODO: Implement Cohere document embedding")