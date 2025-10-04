#LULUH

"""
LLM Service

This module handles generating answers using Groq's LLM inference API.
We use Groq because it's fast and cost-effective for open-source models.
"""

from typing import List
import os
import groq  #اضفته


# raise NotImplementedError("TODO: Implement Groq LLM answer generation") تمت المهمة

def call_llm(query: str, context_chunks: List[str]) -> str:
    """
    Generates an answer to the user's query using relevant context chunks.

    Args:
        query (str): The user's original question
            Example: "How do I deploy the Atlas API?"

        context_chunks (List[str]): Relevant text chunks from documents (after reranking)
            Example: [
                "To deploy Atlas API: 1. Run `make deploy`...",
                "Before deployment, ensure environment variables are set...",
                "Atlas uses Kubernetes for deployment..."
            ]
            Length: Usually 12 chunks

    Returns:
        str: Generated answer from the LLM
            Example: "To deploy the Atlas API, follow these steps:\n\n1. First, ensure all environment variables are configured...\n\n2. Run `make deploy` from the atlas/ directory...\n\nRefer to the Atlas Deploy Guide for detailed instructions."

    Raises:
        Exception: If Groq API call fails

    What This Does:
        1. Constructs a prompt with:
           - System instructions (how to behave)
           - Context chunks (relevant knowledge)
           - User's query
        2. Calls Groq API with:
           - model: "llama-3.1-70b-versatile" or "mixtral-8x7b-32768"
           - messages: [system, user]
           - temperature: 0.1 (low = more factual, less creative)
        3. Extracts the generated answer
        4. Returns it as a string

    Example Usage:
        >>> query = "How do I deploy the Atlas API?"
        >>> chunks = [
        ...     "To deploy Atlas: run make deploy...",
        ...     "Atlas uses Kubernetes..."
        ... ]
        >>> answer = call_llm(query, chunks)
        >>> print(answer)
        "To deploy the Atlas API, follow these steps: 1. Run make deploy..."

    Prompt Template:
        System Message:
            You are a helpful assistant for our company's knowledge base.
            Your job is to answer questions using ONLY the provided context.
            If the context doesn't contain enough information, say so.
            Always cite which documents you used.
            Be concise but complete.

        User Message:
            Context:
            ---
            [Chunk 1 text]
            ---
            [Chunk 2 text]
            ---
            ...
            ---

            Question: {query}

            Answer:

    Why We Need This:
        - Vector search finds relevant chunks, but doesn't synthesize an answer
        - LLM reads all chunks and generates a coherent, natural language response
        - LLM can combine information from multiple chunks
        - LLM can format the answer nicely (lists, steps, etc.)

    Model Choice:
        - Llama 3.1 70B: Best quality, slower (~1-2 seconds)
        - Mixtral 8x7B: Good quality, faster (~500ms)
        - Choose based on latency vs quality tradeoff

    Temperature Explained:
        - 0.0: Deterministic (same input → same output)
        - 0.1: Mostly deterministic, slight variation (RECOMMENDED)
        - 1.0: Creative, but might hallucinate

    Why temperature = 0.1?
        - We want factual answers, not creative writing
        - Low temperature = sticks close to context
        - Reduces hallucination risk

    Groq API Parameters:
        - model: "llama-3.1-70b-versatile"
        - messages: [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
          ]
        - temperature: 0.1
        - max_tokens: 1024 (limit response length)

    Token Limits:
        - Llama 3.1: 128K context window (huge!)
        - Mixtral: 32K context window
        - Our chunks + prompt ≈ 8K tokens (well within limit)

    Hallucination Prevention:
        - Explicit instruction: "use ONLY the provided context"
        - Low temperature (0.1)
        - Ask LLM to cite sources
        - If context insufficient, admit it

    Example Response Formats:
        Good (factual):
        "To deploy the Atlas API: 1. Ensure environment variables are set...
        2. Run make deploy... Refer to the Atlas Deploy Guide."

        Good (admits lack of info):
        "The provided context doesn't contain specific deployment steps for Atlas.
        Please check the deployment documentation."

        Bad (hallucinated):
        "First, install Docker and Node.js..." ← Not in context!

    Dependencies:
        - groq Python library: pip install groq
        - Environment variable: GROQ_API_KEY

    API Documentation:
        https://console.groq.com/docs
        https://console.groq.com/docs/models

    Implementation Hints:
        - import groq
        - client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        - Construct system and user prompts
        - Call client.chat.completions.create(...)
        - Extract response.choices[0].message.content

    Prompt Engineering Tips:
        - Be explicit about what you want
        - Give examples of good answers (few-shot prompting)
        - Ask for citations
        - Specify format (e.g., "use numbered lists for steps")

    Testing:
        - Mock Groq API in tests
        - Verify answer contains information from context
        - Verify answer doesn't hallucinate facts not in context
        - Test with insufficient context (should admit lack of info)

    Performance:
        - Llama 3.1 70B: ~1-2 seconds
        - Mixtral 8x7B: ~300-500ms
        - Groq is much faster than OpenAI for same models
    """


    # هنا Initialize Groq client
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    # بخصوص Build system + user prompts
    system_prompt = (
        "You are a helpful assistant for our company's knowledge base.\n"
        "Answer questions using ONLY the provided context.\n"
        "If context is insufficient, say you don't know.\n"
        "Always cite which documents you used.\n"
        "Be concise but complete."
    )

    # Join context chunks into one string
    context_text = "\n---\n".join(context_chunks)

    user_prompt = f"""
    Context:
    ---
    {context_text}
    ---

    Question: {query}

    Answer:
    """

    #  Call Groq API
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=1024,
    )

    # اخر شي يرجع لنا الاجابة
    return response.choices[0].message.content