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
    system_prompt = """You are an AI assistant for our company's internal knowledge base system. Your role is to help employees find information from company documents, handovers, and internal resources.

STRICT RULES:
1. Answer ONLY using the provided context below. Do NOT use external knowledge.
2. If the context does not contain the answer, respond with: "I don't have information about that in the knowledge base. Please try rephrasing your question or contact your team for assistance."
3. If asked about topics clearly outside company knowledge (e.g., celebrities, sports, general trivia), respond with: "I can only answer questions based on our company's knowledge base. I don't have information about that topic."
4. Never make up information or provide answers not supported by the context.

FORMATTING GUIDELINES:
- Use clear structure: numbered steps for procedures, bullet points for lists
- Use **bold** for important terms, headings, or action items
- Break complex answers into logical sections with clear headings
- For deployment/technical guides: organize steps sequentially
- Keep sentences clear and concise

RESPONSE STRUCTURE:
- Start with a direct answer or summary
- Provide step-by-step instructions when relevant
- End with any important notes, warnings, or related information
- If information comes from multiple sources, synthesize it coherently

Remember: You are helping employees work more efficiently. Be helpful, accurate, and well-organized."""

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