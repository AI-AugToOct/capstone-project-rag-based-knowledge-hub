"""
Text Chunker

Splits long documents into smaller chunks for embedding and retrieval.
"""
#Raghad

from typing import List, Dict, Any
import tiktoken  # For token counting


def chunk_markdown(
    markdown: str,
    sections: List[Dict[str, Any]] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    
    # Load tiktoken encoding
    encoding = tiktoken.get_encoding("cl100k_base")
    
    # Encode the full markdown text
    tokens = encoding.encode(markdown)
    total_tokens = len(tokens)
    
    # If the document is shorter than chunk_size, return a single chunk
    if total_tokens <= chunk_size:
        return [{
            "text": markdown,
            "heading_path": sections[0]["heading_path"] if sections and len(sections) > 0 else [],
            "token_count": total_tokens,
            "order": 0
        }]
    
    # Split into chunks with overlap
    chunks = []
    order = 0
    position = 0

    while position < total_tokens:
        # Determine the end position for this chunk
        end_position = min(position + chunk_size, total_tokens)

        # Extract chunk tokens and decode to text
        chunk_tokens = tokens[position:end_position]
        chunk_text = encoding.decode(chunk_tokens)

        # Improvement: Try to find a natural sentence or paragraph boundary near the end
        SOFT_SEPS = ["\n\n", "\n", ". ", "! ", "? "]
        extra_tokens = 80  # Small lookahead window after the current chunk
        window_end = min(end_position + extra_tokens, total_tokens)
        window_text = encoding.decode(tokens[position:window_end])

        # Search for a natural separator close to the end of the window
        look_back_from = max(0, len(window_text) - 150)
        split_idx = None
        for sep in SOFT_SEPS:
            i = window_text.rfind(sep, look_back_from)
            if i != -1:
                split_idx = i + (0 if sep.startswith("\n") else len(sep))
                break

        if split_idx is not None:
            chunk_text = window_text[:split_idx]

        # Determine heading_path for this chunk
        heading_path = []
        if sections:
            chunk_start_text = chunk_text[:100].strip().lower()
            for section in sections:
                section_text_snippet = section["text"][:100].strip().lower()
                if section_text_snippet in chunk_text.lower() or chunk_start_text in section["text"].lower():
                    heading_path = section["heading_path"]
                    break

        # Calculate the accurate token count for this chunk
        token_count = len(encoding.encode(chunk_text))

        # Create chunk metadata (only if it has content)
        if chunk_text.strip():
            chunks.append({
                "text": chunk_text,
                "heading_path": heading_path,
                "token_count": token_count,
                "order": order
            })

        # Move position forward (with overlap)
        position += max(1, token_count - chunk_overlap)
        order += 1

    return chunks


    """
    Splits Markdown text into overlapping chunks of approximately chunk_size tokens.

    Args:
        markdown (str): The Markdown text to chunk
            Example: "# Deployment\n\nTo deploy Atlas...\n\n## Prerequisites\n\nYou need..."

        sections (List[Dict], optional): Structured sections from normalizer (with heading_paths)
            Example: [{"heading_path": ["Deployment"], "text": "To deploy..."}]
            If provided, chunks will preserve heading_path metadata

        chunk_size (int): Target chunk size in tokens (default: 500)
            Range: 300-700 tokens is typical
            Why: Balance between context and specificity

        chunk_overlap (int): Number of overlapping tokens between chunks (default: 50)
            Why: Prevents losing context at chunk boundaries

    Returns:
        List[Dict[str, Any]]: List of chunks with metadata
            Example: [
                {
                    "text": "# Deployment\n\nTo deploy Atlas API, follow these steps...",
                    "heading_path": ["Deployment"],
                    "token_count": 487,
                    "order": 0
                },
                {
                    "text": "...follow these steps:\n\n1. Configure environment...",
                    "heading_path": ["Deployment", "Prerequisites"],
                    "token_count": 512,
                    "order": 1
                }
            ]

    What This Does:
        1. Counts tokens in the full document
        2. Splits into chunks of ~chunk_size tokens
        3. Adds overlap between chunks
        4. Preserves heading_path metadata
        5. Assigns order (for reconstruction)

    Example Usage:
        >>> markdown = "# Deploy\n\nTo deploy: 1. Config 2. Run..."
        >>> chunks = chunk_markdown(markdown, chunk_size=100, chunk_overlap=20)
        >>> print(len(chunks))
        3
        >>> print(chunks[0]["token_count"])
        95

    Why We Need Chunking:
        - LLMs have token limits (can't process 50-page documents)
        - Vector search works better with focused chunks
        - Smaller chunks = more precise retrieval
        - BUT chunks must have enough context to be useful

    Why Overlap:
        - Without overlap, important information might be split
        - Example without overlap:
          • Chunk 1: "To deploy Atlas API, you need to configure"
          • Chunk 2: "environment variables and run make deploy"
          ← Sentence is split! Missing context.

        - Example WITH 50-token overlap:
          • Chunk 1: "...you need to configure environment variables..."
          • Chunk 2: "...configure environment variables and run make deploy..."
          ← Overlap preserves full sentence in both chunks!

    Token Counting:
        - Use tiktoken library (OpenAI's tokenizer)
        - Model: cl100k_base (compatible with most models)
        - Example: "Hello world" = 2 tokens

    Optimal Chunk Sizes:
        - 300-500 tokens: Good for FAQs, definitions
        - 500-700 tokens: Good for documentation, guides
        - 700-1000 tokens: Good for detailed technical docs
        - Our default: 500 tokens (balanced)

    Chunking Strategy:

        1. Respect Section Boundaries:
           - Prefer to split at heading boundaries
           - Don't split mid-paragraph if possible

        2. Add Overlap:
           - Take last N tokens from previous chunk
           - Prepend to next chunk
           - Ensures smooth transitions

        3. Preserve Metadata:
           - Each chunk inherits heading_path from its section
           - Helps with context ("this is from Deployment > Steps")

    Example Document:
        Input (1500 tokens total):
            "# Deployment (200 tokens)
             Text A (300 tokens)
             ## Prerequisites (400 tokens)
             Text B (300 tokens)
             ## Steps (300 tokens)"

        Output (chunk_size=500, overlap=50):
            Chunk 0: "# Deployment\nText A" (500 tokens)
                heading_path: ["Deployment"]

            Chunk 1: "...end of Text A (50 overlap)\n## Prerequisites\nText B" (500 tokens)
                heading_path: ["Deployment", "Prerequisites"]

            Chunk 2: "...end of Text B (50 overlap)\n## Steps" (350 tokens)
                heading_path: ["Deployment", "Steps"]

    Tiktoken Usage:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        token_count = len(tokens)

    Edge Cases:
        - Document shorter than chunk_size → return as single chunk
        - Chunk would be >chunk_size → split at sentence boundary
        - No sections provided → all chunks have heading_path = []

    Dependencies:
        - tiktoken library: pip install tiktoken

    Implementation Hints:
        1. Load tiktoken encoding: cl100k_base
        2. Count total tokens
        3. If < chunk_size, return single chunk
        4. Otherwise, split into chunks:
           - Start at position 0
           - Take chunk_size tokens
           - Next chunk starts at (position + chunk_size - chunk_overlap)
        5. Add metadata (heading_path, order)

    Testing:
        - Test with short doc (<500 tokens) → 1 chunk
        - Test with long doc (1500 tokens) → 3 chunks with overlap
        - Verify overlap works (last N tokens of chunk i = first N of chunk i+1)
        - Verify heading_path is preserved
    """
"""
Text Chunker

Splits long documents into smaller chunks for embedding and retrieval.
"""

