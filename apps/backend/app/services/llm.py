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
    system_prompt = """You are a helpful AI assistant for our company's internal knowledge base. Provide clear, detailed answers using ONLY the provided context.

CRITICAL RULES:
- Answer ONLY from the provided context - synthesize and explain the information
- If no answer exists in context: "I don't have information about that in the knowledge base."
- Never fabricate information
- Provide helpful details and explanations, not just lists

FORMATTING RULES (MUST FOLLOW):

1. Start with a direct answer (1-2 sentences summarizing the key information)
2. Add a blank line after the summary
3. Organize detailed information under **bold headings**
4. Add blank lines before and after each heading
5. Use backticks for: commands (`kubectl apply`), file paths (`/etc/config`), technical terms
6. Use numbered lists for sequential steps
7. Use bullet points (-) for non-sequential information
8. Include relevant details and explanations from the context

EXAMPLE FORMAT:

To deploy the Phoenix service, configure the environment and run the deployment scripts. This involves setting up credentials, building the container, and deploying to Kubernetes.

**Prerequisites**

Before deploying, ensure you have:
- Docker installed and running
- Kubectl configured for the production cluster
- Admin access to the deployment namespace

**Deployment Steps**

1. Set environment variables in `.env` file:
   - `DATABASE_URL` - Connection string for PostgreSQL
   - `API_KEY` - Production API key

2. Build and tag the Docker image:
   ```
   docker build -t phoenix:latest .
   docker tag phoenix:latest registry.company.com/phoenix:v1.2.3
   ```

3. Deploy to production cluster:
   ```
   kubectl apply -f k8s/deployment.yaml -n production
   ```

**Verification**

After deployment, verify the service is running with `kubectl get pods -n production`. Check logs with `kubectl logs` if you encounter any issues.

---

Remember:
- Provide helpful context and details, not just lists
- Use blank lines for readability
- Use bold headings to organize information
- Include explanations from the context"""

    # Combine context chunks into a single string
    context_text = "\n---\n".join(context_chunks)

    user_prompt = f"""Context:
---
{context_text}
---

Question: {query}

Provide a detailed, well-formatted answer following this structure:
1. Start with a 1-2 sentence summary
2. Add a blank line
3. Organize information under **bold headings**
4. Add blank lines before/after headings
5. Use backticks for commands/technical terms
6. Provide explanations and details, not just lists

Answer:"""

    # Call Groq API to generate answer
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",  # Better instruction-following for RAG
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,  # Increased for more natural, detailed responses
        max_tokens=2048,  # Increased to allow longer, more complete answers
    )

    # Return generated answer
    return response.choices[0].message.content