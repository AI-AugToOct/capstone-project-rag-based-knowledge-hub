# LULUH

from typing import List
import os
import groq


def call_llm(query: str, context_chunks: List[str]) -> str:
    """Generates an answer using Groq LLM based on context chunks."""
    
    # Initialization Groq client configuration
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Building system + user prompts for LLM
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

    # Here for Calling Groq API to generate answer
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",  # or "mixtral-8x7b-32768"
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    # Finally, return generated answer
    return response.choices[0].message.content

