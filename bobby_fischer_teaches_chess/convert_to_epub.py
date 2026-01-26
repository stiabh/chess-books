#!/usr/bin/env python3
"""
Convert book_data.json to EPUB format.

This script converts the extracted chess book data into an EPUB file,
handling the unique Q&A format where questions and answers appear in
separate boxes across pages.
"""

import io
import json
import os
import re
from pathlib import Path

from ebooklib import epub
from PIL import Image


def load_book_data(json_path: str = "book_data.json") -> list[dict]:
    """Load and parse book_data.json."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def has_non_ascii(line: str) -> bool:
    """Check if a line contains non-ASCII characters (garbled OCR from diagrams)."""
    # Allow common punctuation and accented characters that might be legitimate
    for char in line:
        if ord(char) > 127:
            # Allow some common legitimate characters and checkbox symbols
            if char in "éèêëàâäùûüôöîïç—–''""…☐☑":
                continue
            return True
    return False


def is_garbled_line(line: str) -> bool:
    """Check if a line is likely garbled OCR output from a diagram."""
    line = line.strip()
    if not line:
        return False

    # Lines with non-ASCII are likely diagram artifacts
    if has_non_ascii(line):
        return True

    # Very short lines with just symbols/single chars (but not frame numbers)
    if len(line) <= 3 and not line.isdigit():
        # Check if it's just punctuation or symbols
        if all(c in "xX×✗☐☑•·-–—." for c in line):
            return True

    # Standalone "Black" or "White" are diagram labels
    if line in ("Black", "White", "Black:", "White:"):
        return True

    # Single letters or diagram position markers (like "A", "B", "A1.", "B2.")
    if re.match(r"^[A-Z]\d*\.?$", line):
        return True

    # Short numeric strings that aren't frame numbers (like "00", "11t")
    if re.match(r"^\d+[a-z]?$", line) and not line.isdigit():
        return True

    # Just zeros or repeated digits (likely OCR artifacts)
    if re.match(r"^0+$", line):
        return True

    return False


def is_paragraph_break(prev_line: str, curr_line: str) -> bool:
    """
    Determine if there should be a paragraph break between two lines.
    Returns True if curr_line starts a new paragraph.
    """
    if not prev_line or not curr_line:
        return True

    # Frame numbers are always separate
    if re.match(r"^\d+(\s*\(continued\))?$", curr_line):
        return True

    # All caps headings start new paragraphs (but not single short words)
    if curr_line.isupper() and len(curr_line) > 10:
        return True

    # Checkbox options are separate lines (check early before incomplete phrase merging)
    if curr_line.startswith(("☐ can", "☐ cannot", "can capture", "cannot capture", "can flee", "can do")):
        return True

    # But don't break if previous line ends with an incomplete phrase
    last_word = prev_line.split()[-1].upper() if prev_line.split() else ""
    if last_word in ("THE", "TO", "A", "AN", "OF", "AND", "OR", "BY", "IN", "FOR", "NEXT", "THIS"):
        return False

    # Lines starting with special markers (but merge "PAGE" with previous)
    if curr_line.startswith(("NOTE:", "TURN THE PAGE")):
        return True
    if curr_line.startswith("FOR THE CORRECT"):
        return True

    # More checkbox options
    if curr_line.startswith(("can ", "cannot ")):
        return True

    # Previous line ends with complete sentence AND current starts with capital
    # But only if previous line is reasonably long (not a short label)
    ends_complete = prev_line[-1] in ".!?)" if prev_line else False
    starts_capital = curr_line[0].isupper() if curr_line else False

    if ends_complete and starts_capital and len(prev_line) > 50:
        return True

    # Short standalone labels (like "Black" or "White" or diagram labels)
    if len(curr_line) < 15 and curr_line[0].isupper() and not curr_line.endswith((",", "-")):
        # Check if it looks like a label
        if curr_line in ("Black", "White", "Black:", "White:") or re.match(r"^[A-Z]\d*\.$", curr_line):
            return True

    return False


def clean_and_merge_text(text: str) -> list[str]:
    """
    Clean text by removing garbled lines and merging continuation lines.
    Returns list of clean paragraphs.
    """
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

    # Merge lines into paragraphs
    paragraphs = []
    current_para = []

    for line in clean_lines:
        # Frame numbers always stay as their own paragraph
        is_frame_num = re.match(r"^\d+(\s*\(continued\))?$", line.strip())

        if not current_para:
            current_para.append(line)
            # If this is a frame number, flush it immediately
            if is_frame_num:
                paragraphs.append(line)
                current_para = []
            continue

        prev_line = current_para[-1]

        # If current line is a frame number, flush previous and start new
        if is_frame_num:
            paragraphs.append(" ".join(current_para))
            paragraphs.append(line)  # Frame number as its own paragraph
            current_para = []
            continue

        # Check if previous line ends with hyphen (word continuation)
        if prev_line.endswith("-"):
            # Remove hyphen and merge
            current_para[-1] = prev_line[:-1] + line
            continue

        # Check if this should be a paragraph break
        if is_paragraph_break(prev_line, line):
            paragraphs.append(" ".join(current_para))
            current_para = [line]
            continue

        # Otherwise, merge with previous line
        current_para[-1] = prev_line + " " + line

    # Don't forget the last paragraph
    if current_para:
        paragraphs.append(" ".join(current_para))

    return paragraphs


def resize_image(image_path: str, max_size: int = 300) -> bytes:
    """
    Resize an image to fit within max_size pixels (width or height).
    Returns the resized image as PNG bytes.
    """
    with Image.open(image_path) as img:
        # Calculate new size maintaining aspect ratio
        width, height = img.size
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()


def create_image_tag(image_path: str, epub_images: dict) -> str:
    """Create an HTML img tag for a diagram image."""
    filename = os.path.basename(image_path)
    epub_path = f"images/{filename}"
    epub_images[image_path] = epub_path

    # Images are pre-resized, so just use auto sizing
    return f'<img src="{epub_path}" alt="Chess diagram" style="max-width: 100%; height: auto; display: block; margin: 0.5em auto;"/>'


def create_content_with_diagrams(text: str, diagrams: list, epub_images: dict) -> str:
    """
    Generate HTML content with diagrams placed after the first sentence.
    For content pages (no frame numbers).
    """
    paragraphs = clean_and_merge_text(text)

    if not paragraphs and not diagrams:
        return ""

    html_parts = []

    # For content pages, put diagrams after first paragraph
    if paragraphs:
        html_parts.append(f"<p>{escape_html(paragraphs[0])}</p>")

    # Add diagrams
    for diagram in diagrams:
        html_parts.append(create_image_tag(diagram, epub_images))

    # Add remaining paragraphs
    for p in paragraphs[1:]:
        html_parts.append(f"<p>{escape_html(p)}</p>")

    return "\n".join(html_parts)


def create_box_content_with_diagrams(text: str, diagrams: list, epub_images: dict, is_answer: bool = False) -> str:
    """
    Generate HTML for a box with diagrams placed immediately after frame number heading.
    Frame numbers become headings on both question and answer pages.
    """
    paragraphs = clean_and_merge_text(text)

    if not paragraphs and not diagrams:
        return ""

    html_parts = []
    diagrams_inserted = False

    for p in paragraphs:
        # Check if this is the frame number line
        frame_match = re.match(r"^(\d+)(\s*\(continued\))?$", p.strip())

        if frame_match:
            # Make frame number a heading
            frame_num = frame_match.group(1)
            continued = " (continued)" if frame_match.group(2) else ""
            html_parts.append(f"<h2>Frame {frame_num}{continued}</h2>")

            # Insert diagrams immediately after frame number heading
            if diagrams and not diagrams_inserted:
                for diagram in diagrams:
                    html_parts.append(create_image_tag(diagram, epub_images))
                diagrams_inserted = True
        else:
            html_parts.append(f"<p>{escape_html(p)}</p>")

    # If no frame number was found, add diagrams at the start (after any existing content)
    if not diagrams_inserted and diagrams:
        # Insert diagrams at position 1 (after first element) or at start
        insert_pos = 1 if html_parts else 0
        for idx, diagram in enumerate(diagrams):
            html_parts.insert(insert_pos + idx, create_image_tag(diagram, epub_images))

    return "\n".join(html_parts)


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


def has_real_content(content: str) -> bool:
    """Check if content has actual visible content (text or images)."""
    text_only = re.sub(r"<[^>]+>", "", content)
    has_text = bool(text_only.strip())
    has_images = "<img" in content
    return has_text or has_images


def wrap_in_html(content: str, title: str = "") -> str:
    """Wrap content in basic HTML structure."""
    if not has_real_content(content):
        content = f"<p>{escape_html(title)}</p>"

    return f"""<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{escape_html(title)}</title>
</head>
<body>
<div class="content">
{content}
</div>
</body>
</html>"""


def process_book(pages: list[dict]) -> tuple[list[tuple[str, str, str]], dict]:
    """
    Process book pages into EPUB chapters.
    """
    chapters = []
    epub_images = {}

    for page in pages:
        page_num = page.get("page", 0)

        if not page.get("has_boxes"):
            # Content page without boxes
            text = page.get("text", "")
            diagrams = page.get("diagrams", [])
            content = create_content_with_diagrams(text, diagrams, epub_images)

            if content.strip():
                chapter_id = f"page_{page_num}"
                title = f"Page {page_num}"

                # Check for special pages
                if "Bobby\nFischer\nTeaches\nChess" in text:
                    title = "Title Page"
                elif "CONTENTS" in text:
                    title = "Contents"
                elif "A WORD FROM BOBBY FISCHER" in text:
                    title = "A Word from Bobby Fischer"
                elif "THE PHENOMENAL BOBBY FISCHER" in text:
                    title = "The Phenomenal Bobby Fischer"
                elif "ABOUT THE COAUTHORS" in text:
                    title = "About the Coauthors"
                elif "INTRODUCTION: HOW TO PLAY" in text:
                    title = "Introduction: How to Play Chess"

                html = wrap_in_html(content, title)
                chapters.append((chapter_id, title, html))
        else:
            # Page with boxes
            boxes = page.get("boxes", [])

            for box in boxes:
                box_id = box.get("box_id", 1)

                if is_no_answer_required(box):
                    continue

                text = box.get("text", "")
                diagrams = box.get("diagrams", [])
                is_answer = box_id == 1 and len(boxes) > 1
                content = create_box_content_with_diagrams(text, diagrams, epub_images, is_answer)

                if not content.strip():
                    continue

                chapter_id = f"page_{page_num}_box_{box_id}"

                # Check for chapter headers
                chapter_info = extract_chapter_info(text)
                if chapter_info:
                    ch_num, ch_title = chapter_info
                    title = f"Chapter {ch_num}: {ch_title}"
                    content = f"<h1>{escape_html(title)}</h1>\n{content}"
                else:
                    # Extract frame number for title
                    first_line = text.split("\n")[0].strip() if text else ""
                    frame_match = re.match(r"^(\d+)(\s*\(continued\))?$", first_line)

                    if frame_match:
                        frame_num = frame_match.group(1)
                        is_continued = frame_match.group(2) is not None
                        suffix = " (continued)" if is_continued else ""

                        if is_answer:
                            title = f"Frame {frame_num} - Answer"
                        else:
                            title = f"Frame {frame_num}{suffix}"
                    else:
                        title = f"Page {page_num}"
                        if box_id > 1:
                            title += f" (Part {box_id})"

                html = wrap_in_html(content, title)
                chapters.append((chapter_id, title, html))

    return chapters, epub_images


def build_epub(
    chapters: list[tuple[str, str, str]],
    epub_images: dict,
    output_path: str = "bobby_fischer_teaches_chess.epub"
):
    """Assemble the EPUB file."""
    book = epub.EpubBook()

    book.set_identifier("bobby-fischer-teaches-chess")
    book.set_title("Bobby Fischer Teaches Chess")
    book.set_language("en")
    book.add_author("Bobby Fischer")
    book.add_author("Stuart Margulies")
    book.add_author("Donn Mosenfelder")

    css_content = """
        body {
            font-family: Georgia, serif;
            line-height: 1.5;
            padding: 0.5em;
        }
        p {
            margin: 0.5em 0;
        }
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0.5em auto;
        }
        h1 {
            text-align: center;
            font-size: 1.5em;
            margin: 0.5em 0;
        }
        h2 {
            font-size: 1.2em;
            margin: 0.3em 0;
            color: #333;
        }
    """
    css = epub.EpubItem(
        uid="style",
        file_name="style/main.css",
        media_type="text/css",
        content=css_content
    )
    book.add_item(css)

    print("Resizing images...")
    for source_path, epub_path in epub_images.items():
        if os.path.exists(source_path):
            # Resize image to max 300px (preserves originals)
            img_content = resize_image(source_path, max_size=300)

            img_item = epub.EpubItem(
                uid=epub_path.replace("/", "_").replace(".", "_"),
                file_name=epub_path,
                media_type="image/png",  # All resized images are saved as PNG
                content=img_content
            )
            book.add_item(img_item)

    epub_chapters = []
    toc_entries = []

    for chapter_id, title, html_content in chapters:
        chapter = epub.EpubHtml(
            title=title,
            file_name=f"{chapter_id}.xhtml",
            lang="en"
        )
        chapter.content = html_content.encode("utf-8")
        chapter.add_item(css)
        book.add_item(chapter)
        epub_chapters.append(chapter)

        if any(keyword in title for keyword in [
            "Title Page", "Contents", "A Word from", "Phenomenal",
            "About the", "Introduction", "Chapter"
        ]):
            toc_entries.append(chapter)

    book.toc = toc_entries if toc_entries else epub_chapters[:10]

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.spine = ["nav"] + epub_chapters

    epub.write_epub(output_path, book, {})
    print(f"EPUB created: {output_path}")
    print(f"Total chapters: {len(epub_chapters)}")
    print(f"Total images: {len(epub_images)}")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("Loading book data...")
    pages = load_book_data("book_data.json")
    print(f"Loaded {len(pages)} pages")

    print("Processing pages...")
    chapters, epub_images = process_book(pages)
    print(f"Created {len(chapters)} chapters")
    print(f"Found {len(epub_images)} images")

    print("Building EPUB...")
    build_epub(chapters, epub_images)

    print("Done!")


if __name__ == "__main__":
    main()
