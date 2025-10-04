"""
Markdown Normalizer

Converts Notion blocks to clean Markdown format.
Preserves structure (headings, lists, code blocks) while cleaning up formatting.
"""
#Raghad

from typing import List, Dict, Any, Tuple


def normalize_to_markdown(blocks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    
    
    """
    Converts Notion blocks to Markdown and extracts structured metadata.

    Args:
        blocks (List[Dict[str, Any]]): List of Notion block objects
            Example: [
                {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "Deployment"}]}},
                {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "To deploy..."}]}}
            ]

    Returns:
        Tuple[str, List[Dict[str, Any]]]: (markdown_text, sections)
            markdown_text (str): Clean Markdown representation
                Example: "# Deployment\n\nTo deploy Atlas API...\n\n## Steps\n\n1. Configure..."

            sections (List[Dict]): Structured sections with heading paths
                Example: [
                    {
                        "heading_path": ["Deployment"],
                        "text": "To deploy Atlas API..."
                    },
                    {
                        "heading_path": ["Deployment", "Steps"],
                        "text": "1. Configure environment\n2. Run make deploy"
                    }
                ]

    What This Does:
        1. Iterates through Notion blocks
        2. Converts each block type to Markdown
        3. Tracks heading hierarchy (for heading_path)
        4. Builds sections grouped by headings
        5. Returns both raw Markdown and structured sections

    Example Usage:
        >>> blocks = fetch_blocks("page-uuid-123")
        >>> markdown, sections = normalize_to_markdown(blocks)
        >>> print(markdown[:100])
        "# Deployment\n\nTo deploy Atlas API, follow these steps:\n\n## Prerequisites\n\n- Kubernetes cluster..."
        >>> print(sections[0])
        {"heading_path": ["Deployment"], "text": "To deploy Atlas API..."}

    Why We Need This:
        - Notion blocks are complex nested JSON
        - Markdown is simple, human-readable, easy to chunk
        - Preserving structure (headings) helps with context
        - heading_path helps users understand where content came from

    Block Type Conversions:

        heading_1 → # Heading
        heading_2 → ## Heading
        heading_3 → ### Heading

        paragraph → Plain text with newlines

        bulleted_list_item → - Item
        numbered_list_item → 1. Item

        code → ```language\ncode\n```

        quote → > Quote text

        divider → ---

        table → Markdown table:
            | Col1 | Col2 |
            |------|------|
            | Val1 | Val2 |

    Heading Path Tracking:

        Example document:
            # Deployment
            Some text here.
            ## Prerequisites
            Need Kubernetes.
            ## Steps
            1. Configure
            2. Deploy

        heading_path values:
            - "Some text here" → ["Deployment"]
            - "Need Kubernetes" → ["Deployment", "Prerequisites"]
            - "1. Configure..." → ["Deployment", "Steps"]

    Why heading_path Matters:
        - Helps users understand context
        - "Deploy Atlas API" (under Deployment > Steps) is clear
        - Same text without heading would be confusing

    Markdown Cleaning:
        - Remove extra blank lines (max 2 consecutive)
        - Strip leading/trailing whitespace
        - Normalize line endings (\r\n → \n)
        - Remove Notion-specific formatting artifacts

    Example Output:

        Input (Notion blocks):
            [
                {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "Deploy"}]}},
                {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "Run make deploy"}]}}
            ]

        Output (Markdown):
            "# Deploy\n\nRun make deploy"

        Output (Sections):
            [{"heading_path": ["Deploy"], "text": "Run make deploy"}]

    Dependencies:
        - No external libraries needed (pure Python)

    Implementation Hints:
        - Use a stack to track current heading path
        - When you see heading_1, reset stack to [heading_text]
        - When you see heading_2, stack becomes [h1_text, h2_text]
        - Text blocks use current stack as heading_path
        - Build Markdown string incrementally

    Edge Cases:
        - Empty blocks → skip
        - Blocks with no rich_text → skip
        - Multiple consecutive headings → each starts new section
        - Page starts with text (no heading) → use heading_path = []

    Testing:
        - Test with document that has: headings, paragraphs, lists, code
        - Verify Markdown is clean and readable
        - Verify heading_path correctly reflects nesting
        - Test with nested headings (h1 → h2 → h3)
    """



    """
    Converts Notion blocks to Markdown and extracts structured metadata.

    Args:
        blocks (List[Dict[str, Any]]): List of Notion block objects
            Example: [
                {"type": "heading_1", "heading_1": {"rich_text": [{"plain_text": "Deployment"}]}},
                {"type": "paragraph", "paragraph": {"rich_text": [{"plain_text": "To deploy..."}]}}
            ]

    Returns:
        Tuple[str, List[Dict[str, Any]]]: (markdown_text, sections)
            markdown_text (str): Clean Markdown representation
                Example: "# Deployment\n\nTo deploy Atlas API...\n\n## Steps\n\n1. Configure..."

            sections (List[Dict]): Structured sections with heading paths
                Example: [
                    {
                        "heading_path": ["Deployment"],
                        "text": "To deploy Atlas API..."
                    },
                    {
                        "heading_path": ["Deployment", "Steps"],
                        "text": "1. Configure environment\n2. Run make deploy"
                    }
                ]
    """
    markdown_lines = []
    sections = []
    heading_stack = []
    current_section_text = []
    
    def extract_text(rich_text_list):
        """Extract plain text from Notion rich_text array"""
        if not rich_text_list:
            return ""
        return "".join([item.get("plain_text", "") for item in rich_text_list])
    
    def save_section():
        """Save current section if it has content"""
        if current_section_text:
            text = "\n".join(current_section_text).strip()
            if text:
                sections.append({
                    "heading_path": heading_stack.copy(),
                    "text": text
                })
            current_section_text.clear()
    
    for block in blocks:
        block_type = block.get("type", "")
        
        # Skip empty blocks
        if not block_type or block_type not in block:
            continue
        
        block_content = block[block_type]
        
        # Handle heading_1
        if block_type == "heading_1":
            save_section()
            text = extract_text(block_content.get("rich_text", []))
            if text:
                markdown_lines.append(f"# {text}")
                markdown_lines.append("")
                heading_stack = [text]
        
        # Handle heading_2
        elif block_type == "heading_2":
            save_section()
            text = extract_text(block_content.get("rich_text", []))
            if text:
                markdown_lines.append(f"## {text}")
                markdown_lines.append("")
                if len(heading_stack) >= 1:
                    heading_stack = [heading_stack[0], text]
                else:
                    heading_stack = [text]
        
        # Handle heading_3
        elif block_type == "heading_3":
            save_section()
            text = extract_text(block_content.get("rich_text", []))
            if text:
                markdown_lines.append(f"### {text}")
                markdown_lines.append("")
                if len(heading_stack) >= 2:
                    heading_stack = [heading_stack[0], heading_stack[1], text]
                elif len(heading_stack) == 1:
                    heading_stack = [heading_stack[0], text]
                else:
                    heading_stack = [text]
        
        # Handle paragraph
        elif block_type == "paragraph":
            text = extract_text(block_content.get("rich_text", []))
            if text:
                markdown_lines.append(text)
                markdown_lines.append("")
                current_section_text.append(text)
        
        # Handle bulleted_list_item
        elif block_type == "bulleted_list_item":
            text = extract_text(block_content.get("rich_text", []))
            if text:
                markdown_lines.append(f"- {text}")
                current_section_text.append(f"- {text}")
        
        # Handle numbered_list_item
        elif block_type == "numbered_list_item":
            text = extract_text(block_content.get("rich_text", []))
            if text:
                markdown_lines.append(f"1. {text}")
                current_section_text.append(f"1. {text}")
        
        # Handle code
        elif block_type == "code":
            text = extract_text(block_content.get("rich_text", []))
            language = block_content.get("language", "")
            if text:
                markdown_lines.append(f"{language}")
                markdown_lines.append(text)
                markdown_lines.append("")
                markdown_lines.append("")
                current_section_text.append(f"{language}\n{text}\n")
        
        # Handle quote
        elif block_type == "quote":
            text = extract_text(block_content.get("rich_text", []))
            if text:
                markdown_lines.append(f"> {text}")
                markdown_lines.append("")
                current_section_text.append(f"> {text}")
        
        # Handle divider
        elif block_type == "divider":
            markdown_lines.append("---")
            markdown_lines.append("")
            current_section_text.append("---")
        
        # Handle table
        elif block_type == "table":
            # Note: Full table implementation would require processing table_row children
            # This is a placeholder as tables need child blocks
            pass
    
    # Save last section
    save_section()
    
    # Join markdown lines
    markdown_text = "\n".join(markdown_lines)
    
    # Clean up: Remove more than 2 consecutive newlines
    while "\n\n\n" in markdown_text:
        markdown_text = markdown_text.replace("\n\n\n", "\n\n")
    
    # Normalize line endings
    markdown_text = markdown_text.replace("\r\n", "\n")
    
    # Strip leading/trailing whitespace
    markdown_text = markdown_text.strip()
    
    return markdown_text, sections