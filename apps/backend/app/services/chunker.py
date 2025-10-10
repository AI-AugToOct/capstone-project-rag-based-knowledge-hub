"""
Text Chunker

Splits long documents into smaller chunks for embedding and retrieval.
"""

from typing import List, Dict, Any
import tiktoken


def chunk_markdown(
    markdown: str,
    sections: List[Dict[str, Any]] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Splits Markdown text into overlapping chunks of approximately chunk_size tokens.
    """
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

        # Try to find a natural sentence or paragraph boundary
        SOFT_SEPS = ["\n\n", "\n", ". ", "! ", "? "]
        extra_tokens = 80
        window_end = min(end_position + extra_tokens, total_tokens)
        window_text = encoding.decode(tokens[position:window_end])

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