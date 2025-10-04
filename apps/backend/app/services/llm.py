<<<<<<< HEAD
# LULUH

from typing import List
import os
import groq
=======
#LULUH

"""
LLM Service

This module handles generating answers using Groq's LLM inference API.
We use Groq because it's fast and cost-effective for open-source models.
"""

from typing import List
import os
import groq  #اضفته
>>>>>>> 4ab9f07 (add)


# raise NotImplementedError("TODO: Implement Groq LLM answer generation") تمت المهمة

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

<<<<<<< HEAD
=======
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
>>>>>>> 4ab9f07 (add)
