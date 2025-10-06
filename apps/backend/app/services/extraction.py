"""
Document Text Extraction

Extracts text from PDF and DOCX files and converts to Markdown format.
"""

import io
from typing import Tuple, List, Dict, Any


def extract_pdf_to_markdown(file_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts text from PDF and converts to Markdown.

    Args:
        file_bytes: PDF file content as bytes

    Returns:
        (markdown_text, sections) where sections contain heading_path

    For MVP: Simple text extraction, no advanced layout parsing
    """
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")

    # Read PDF
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

    markdown_lines = []
    sections = []

    # Extract text from each page
    for page_num, page in enumerate(pdf_reader.pages, start=1):
        text = page.extract_text()
        if text.strip():
            # Add page heading
            page_heading = f"Page {page_num}"
            markdown_lines.append(f"## {page_heading}")
            markdown_lines.append("")
            markdown_lines.append(text.strip())
            markdown_lines.append("")

            # Add to sections
            sections.append({
                "heading_path": [page_heading],
                "text": text.strip()
            })

    markdown_text = "\n".join(markdown_lines).strip()
    return markdown_text, sections


def extract_docx_to_markdown(file_bytes: bytes) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts text from DOCX and converts to Markdown.

    Args:
        file_bytes: DOCX file content as bytes

    Returns:
        (markdown_text, sections) where sections contain heading_path

    For MVP: Extract paragraphs and basic structure
    """
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")

    # Read DOCX
    doc = Document(io.BytesIO(file_bytes))

    markdown_lines = []
    sections = []
    heading_stack = []
    current_section_text = []

    def save_section():
        """Save current section if it has content"""
        if current_section_text:
            text = "\n".join(current_section_text).strip()
            if text:
                sections.append({
                    "heading_path": heading_stack.copy() if heading_stack else ["Document"],
                    "text": text
                })
            current_section_text.clear()

    # Process paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect headings (based on style)
        if para.style.name.startswith('Heading'):
            save_section()

            # Extract heading level
            level = 1
            if para.style.name.startswith('Heading '):
                try:
                    level = int(para.style.name.split()[-1])
                except ValueError:
                    level = 1

            # Add to markdown
            markdown_lines.append(f"{'#' * min(level, 3)} {text}")
            markdown_lines.append("")

            # Update heading stack
            if level == 1:
                heading_stack = [text]
            elif level == 2 and len(heading_stack) >= 1:
                heading_stack = [heading_stack[0], text]
            elif level == 3 and len(heading_stack) >= 2:
                heading_stack = [heading_stack[0], heading_stack[1], text]
            else:
                heading_stack = [text]
        else:
            # Regular paragraph
            markdown_lines.append(text)
            markdown_lines.append("")
            current_section_text.append(text)

    # Save last section
    save_section()

    # If no sections were created, create one default section
    if not sections and markdown_lines:
        sections.append({
            "heading_path": ["Document"],
            "text": "\n".join(markdown_lines).strip()
        })

    markdown_text = "\n".join(markdown_lines).strip()
    return markdown_text, sections


def extract_text_from_file(file_bytes: bytes, filename: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extracts text from PDF or DOCX file.

    Args:
        file_bytes: File content as bytes
        filename: Original filename (used to detect file type)

    Returns:
        (markdown_text, sections)

    Raises:
        ValueError: If file type is unsupported
    """
    filename_lower = filename.lower()

    if filename_lower.endswith('.pdf'):
        return extract_pdf_to_markdown(file_bytes)
    elif filename_lower.endswith('.docx'):
        return extract_docx_to_markdown(file_bytes)
    elif filename_lower.endswith('.txt') or filename_lower.endswith('.md'):
        # Plain text/markdown - just decode and wrap in section
        text = file_bytes.decode('utf-8', errors='ignore').strip()
        sections = [{
            "heading_path": ["Document"],
            "text": text
        }]
        return text, sections
    else:
        raise ValueError(f"Unsupported file type: {filename}. Supported: PDF, DOCX, TXT, MD")