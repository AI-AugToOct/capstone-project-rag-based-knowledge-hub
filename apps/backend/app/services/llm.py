# LULUH

"""
LLM Service

This module handles generating answers using Groq's LLM inference API.
We use Groq because it's fast and cost-effective for open-source models.
"""

from typing import List
import os
import groq


def call_llm(query: str, context_chunks: List[str]) -> str:
    """Generates an answer using Groq LLM based on context chunks."""

    # Initialize Groq client
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Build system + user prompts
    system_prompt = (
        "You are a helpful assistant for our company's knowledge base.\n"
        "Answer questions using ONLY the provided context.\n"
        "If context is insufficient, say you don't know.\n"
        "Always cite which documents you used.\n"
        "Be concise but complete."
    )

    # Combine context chunks into a single string
    context_text = "\n---\n".join(context_chunks)

    user_prompt = f"""
    Context:
    ---
    {context_text}
    ---

    Question: {query}

    Answer:
    """

    # Call Groq API to generate answer
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Updated model (3.1 deprecated)
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    # Return generated answer
    return response.choices[0].message.content