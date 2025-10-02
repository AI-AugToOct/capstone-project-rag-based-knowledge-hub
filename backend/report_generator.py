import google.generativeai as genai
from backend.config import GOOGLE_API_KEY

# Configure the Gemini model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

def generate_report(context, query=None):
    """
    Generate a professional project report or answer using Gemini.
    
    :param context: Retrieved chunks of text from the knowledge base.
    :param query: (Optional) The user's query, used to focus the report.
    :return: Markdown-formatted report text.
    """
    if not context.strip():
        return "⚠️ No context provided for report generation."

    prompt = f"""
    You are a senior project manager AI assistant. Use the provided context to generate a professional, management-ready response.

    User Query (if provided):
    {query if query else "No specific query. Provide a general report."}

    Context:
    {context}

    Requirements:
    - Write in a formal corporate tone, no emojis.
    - Use clear Markdown headings and subsections.
    - Target ~2 pages of content when printed (concise but detailed).
    - Include these sections in order if relevant:
      1) Title block (Project name: "Secure Contract Exchange Platform", Date, Prepared by)
      2) Executive Summary
      3) Project Scope
      4) Detailed Task Breakdown
      5) Project Statistics
      6) Timeline Overview
      7) Risks & Mitigations
      8) Next Steps
    - If the query is specific (e.g., "Summarize milestones"), focus on answering it first.
    - Keep the output in Markdown ONLY (headings, bullet lists, short paragraphs).
    - Avoid code blocks and images.
    """

    response = model.generate_content(prompt)
    return response.text.strip()
