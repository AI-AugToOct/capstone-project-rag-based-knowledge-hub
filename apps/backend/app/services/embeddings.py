"""
Embeddings Service

This module handles converting text into vector embeddings using Cohere.
Embeddings are numerical representations of text that capture semantic meaning.
"""

from typing import List
import os


def embed_query(text: str) -> List[float]:
    """
    Converts a user's search query into a 1024-dimensional vector embedding.

    Args:
        text (str): The user's search query
            Example: "How do I deploy the Atlas API?"
            Example: "What are the steps for onboarding new employees?"

    Returns:
        List[float]: A 1024-dimensional vector (list of 1024 floating point numbers)
            Example: [0.023, -0.15, 0.091, ..., 0.18, -0.22]
            Length: Always exactly 1024 elements

    Raises:
        ValueError: If text is empty or None
        Exception: If Cohere API call fails (network error, invalid API key, rate limit)

    What This Does:
        1. Validates the input text is not empty
        2. Gets the Cohere API key from environment variables
        3. Calls Cohere's embed API with:
           - model: "embed-english-v3.0" (1024 dimensions)
           - input_type: "search_query" (optimized for queries, not documents)
           - texts: [text] (API accepts a list, we send one item)
        4. Extracts the embedding vector from the response
        5. Returns it as a list of floats

    Example Usage:
        >>> query = "How do I deploy the Atlas API?"
        >>> vector = embed_query(query)
        >>> print(len(vector))
        1024
        >>> print(vector[:3])
        [0.023, -0.15, 0.091]
        >>> # This vector will be compared to document chunk vectors

    Why We Need This:
        - Vector search works by comparing the similarity between vectors
        - The user's query must be in the same "embedding space" as document chunks
        - Same model (Cohere v3) is used for both queries and documents
        - input_type="search_query" tells Cohere to optimize for search (not classification)

    How Vector Search Works:
        1. User asks: "How do I deploy?"
        2. embed_query() → [0.1, 0.2, 0.3, ...]
        3. Database has chunks with vectors:
           - Chunk A: [0.11, 0.19, 0.32, ...] (very similar!)
           - Chunk B: [0.9, -0.5, 0.1, ...] (not similar)
        4. Database returns Chunk A because vectors are close

    API Parameters Explained:
        - model: "embed-english-v3.0"
          → Latest Cohere embedding model (1024 dims, better than v2)

        - input_type: "search_query"
          → Tells Cohere this is a user question, not a document
          → Cohere optimizes the embedding for retrieval
          → IMPORTANT: Workers use "search_document" for chunks!

        - texts: [text]
          → API accepts multiple texts, we only send one

    Dependencies:
        - cohere Python library: pip install cohere
        - Environment variable: COHERE_API_KEY

    API Documentation:
        https://docs.cohere.com/docs/embeddings
        https://docs.cohere.com/reference/embed

    Example API Response:
        {
          "embeddings": [
            [0.023, -0.15, 0.091, ..., 0.18]
          ],
          "meta": {...}
        }

    Common Pitfalls:
        - Using "embed-english-v2.0" instead of "v3.0" (wrong dimensions!)
        - Using input_type="search_document" instead of "search_query"
        - Forgetting to extract embeddings[0] from response
        - Not handling API rate limits (100 requests/min on free tier)

    Implementation Hints:
        - import cohere
        - client = cohere.Client(os.getenv("COHERE_API_KEY"))
        - response = client.embed(
              texts=[text],
              model="embed-english-v3.0",
              input_type="search_query"
          )
        - return response.embeddings[0]

    Testing:
        - Mock the Cohere API to avoid using credits during tests
        - Verify returned list has exactly 1024 elements
        - Verify all elements are floats
        - Verify vector is not all zeros
    """
    raise NotImplementedError("TODO: Implement Cohere query embedding")