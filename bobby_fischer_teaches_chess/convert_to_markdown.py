#!/usr/bin/env python3
"""
Convert book_data.json to a single Markdown file for manual editing.
"""

import json
import re
from pathlib import Path


def load_book_data(json_path: str = "book_data.json") -> list[dict]:
    """Load and parse book_data.json."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def has_non_ascii(line: str) -> bool:
    """Check if a line contains non-ASCII characters (garbled OCR from diagrams)."""
    for char in line:
        if ord(char) > 127:
            if char in "éèêëàâäùûüôöîïç—–''""…☐☑":
                continue
            return True
    return False


def is_garbled_line(line: str) -> bool:
    """Check if a line is likely garbled OCR output from a diagram."""
    line = line.strip()
    if not line:
        return False

    if has_non_ascii(line):
        return True

    if len(line) <= 3 and not line.isdigit():
        if all(c in "xX×✗☐☑•·-–—." for c in line):
            return True

    if line in ("Black", "White", "Black:", "White:"):
        return True

    if re.match(r"^[A-Z]\d*\.?$", line):
        return True

    if re.match(r"^\d+[a-z]?$", line) and not line.isdigit():
        return True

    if re.match(r"^0+$", line):
        return True

    return False


def is_paragraph_break(prev_line: str, curr_line: str) -> bool:
    """Determine if there should be a paragraph break between two lines."""
    if not prev_line or not curr_line:
        return True

    if re.match(r"^\d+(\s*\(continued\))?$", curr_line):
        return True

    if curr_line.isupper() and len(curr_line) > 10:
        return True

    last_word = prev_line.split()[-1].upper() if prev_line.split() else ""
    if last_word in ("THE", "TO", "A", "AN", "OF", "AND", "OR", "BY", "IN", "FOR", "NEXT", "THIS"):
        return False

    if curr_line.startswith(("☐ can", "☐ cannot", "can capture", "cannot capture", "can flee", "can do")):
        return True

    if curr_line.startswith(("NOTE:", "TURN THE PAGE")):
        return True
    if curr_line.startswith("FOR THE CORRECT"):
        return True

    if curr_line.startswith(("can ", "cannot ")):
        return True

    ends_complete = prev_line[-1] in ".!?)" if prev_line else False
    starts_capital = curr_line[0].isupper() if curr_line else False

    if ends_complete and starts_capital and len(prev_line) > 50:
        return True

    return False


def clean_and_merge_text(text: str) -> list[str]:
    """Clean text by removing garbled lines and merging continuation lines."""
    if not text:
        return []

    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if is_garbled_line(line):
            continue
        clean_lines.append(line)

    if not clean_lines:
        return []

    paragraphs = []
    current_para = []

    for line in clean_lines:
        is_frame_num = re.match(r"^\d+(\s*\(continued\))?$", line.strip())

        if not current_para:
            current_para.append(line)
            if is_frame_num:
                paragraphs.append(line)
                current_para = []
            continue

        prev_line = current_para[-1]

        if is_frame_num:
            paragraphs.append(" ".join(current_para))
            paragraphs.append(line)
            current_para = []
            continue

        if prev_line.endswith("-"):
            current_para[-1] = prev_line[:-1] + line
            continue

        if is_paragraph_break(prev_line, line):
            paragraphs.append(" ".join(current_para))
            current_para = [line]
            continue

        current_para[-1] = prev_line + " " + line

    if current_para:
        paragraphs.append(" ".join(current_para))

    return paragraphs


def is_no_answer_required(box: dict) -> bool:
    """Check if this is a 'NO ANSWER REQUIRED' box."""
    text = box.get("text", "")
    return "NO ANSWER REQUIRED" in text


def extract_chapter_info(text: str) -> tuple[str, str] | None:
    """Extract chapter number and title from text."""
    match = re.match(r"Chapter\s+(\d+)\s*\n(.+)", text.strip(), re.IGNORECASE)
    if match:
        return match.group(1), match.group(2).strip()
    return None


def format_content_page(page: dict) -> str:
    """Format a content page (no boxes) as markdown."""
    page_num = page.get("page", 0)
    text = page.get("text", "")
    diagrams = page.get("diagrams", [])

    lines = [f"## Page {page_num}\n"]

    paragraphs = clean_and_merge_text(text)

    # Add first paragraph
    if paragraphs:
        lines.append(paragraphs[0])
        lines.append("")

    # Add diagrams
    for diagram in diagrams:
        lines.append(f"![Diagram]({diagram})")
        lines.append("")

    # Add remaining paragraphs
    for p in paragraphs[1:]:
        lines.append(p)
        lines.append("")

    return "\n".join(lines)


def format_box_page(page: dict, box: dict, is_answer: bool) -> str:
    """Format a box as markdown."""
    page_num = page.get("page", 0)
    box_id = box.get("box_id", 1)
    text = box.get("text", "")
    diagrams = box.get("diagrams", [])

    paragraphs = clean_and_merge_text(text)

    if not paragraphs and not diagrams:
        return ""

    lines = []

    # Check for chapter header
    chapter_info = extract_chapter_info(text)
    if chapter_info:
        ch_num, ch_title = chapter_info
        lines.append(f"# Chapter {ch_num}: {ch_title}\n")
        return "\n".join(lines)

    # Extract frame number for heading
    frame_num = None
    first_line = text.split("\n")[0].strip() if text else ""
    frame_match = re.match(r"^(\d+)(\s*\(continued\))?$", first_line)
    if frame_match:
        frame_num = frame_match.group(1)
        is_continued = frame_match.group(2) is not None
        suffix = " (continued)" if is_continued else ""
        answer_suffix = " - Answer" if is_answer else ""
        lines.append(f"### Frame {frame_num}{suffix}{answer_suffix}\n")
    else:
        box_suffix = f" Box {box_id}" if box_id > 1 else ""
        lines.append(f"## Page {page_num}{box_suffix}\n")

    # Add frame number paragraph if present, then diagrams
    for i, p in enumerate(paragraphs):
        if re.match(r"^\d+(\s*\(continued\))?$", p.strip()):
            # Skip frame number in text (already in heading)
            # Add diagrams after frame number
            for diagram in diagrams:
                lines.append(f"![Diagram]({diagram})")
                lines.append("")
        else:
            lines.append(p)
            lines.append("")

    # If no frame number was found, add diagrams at start
    if not frame_num and diagrams:
        diagram_lines = []
        for diagram in diagrams:
            diagram_lines.append(f"![Diagram]({diagram})")
            diagram_lines.append("")
        # Insert after heading
        lines = lines[:1] + diagram_lines + lines[1:]

    return "\n".join(lines)


def convert_to_markdown(pages: list[dict], output_path: str = "book.md"):
    """Convert all pages to a single markdown file."""
    md_parts = ["# Bobby Fischer Teaches Chess\n\n"]

    for page in pages:
        page_num = page.get("page", 0)

        if not page.get("has_boxes"):
            # Content page
            content = format_content_page(page)
            if content.strip():
                md_parts.append(content)
                md_parts.append("\n---\n\n")
        else:
            # Page with boxes
            boxes = page.get("boxes", [])

            for box in boxes:
                box_id = box.get("box_id", 1)

                if is_no_answer_required(box):
                    continue

                is_answer = box_id == 1 and len(boxes) > 1
                content = format_box_page(page, box, is_answer)

                if content.strip():
                    md_parts.append(content)
                    md_parts.append("\n---\n\n")

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("".join(md_parts))

    print(f"Markdown file created: {output_path}")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)

    print("Loading book data...")
    pages = load_book_data("book_data.json")
    print(f"Loaded {len(pages)} pages")

    print("Converting to markdown...")
    convert_to_markdown(pages, "book.md")

    print("Done!")


if __name__ == "__main__":
    main()
