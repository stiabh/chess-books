import json
import os
from io import BytesIO

import cv2
import numpy as np
import pymupdf
from google.cloud import vision
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../vision_api_key.json"
os.makedirs("extracted", exist_ok=True)
os.makedirs("boxes", exist_ok=True)


def extract_page_images(doc: pymupdf.Document, page_number: int) -> list[dict]:
    """Extract all images from a PDF page. First image is the background scan."""
    page = doc[page_number - 1]
    page_images = page.get_images()
    images = []
    for i, page_image in enumerate(page_images):
        image_index = page_image[0]
        image_data = doc.extract_image(image_index)
        x0, y0, x1, y1 = page.get_image_rects(image_index)[0]
        path = f"extracted/page_{page_number}_{i}_{image_index}.png"
        with open(path, "wb") as f:
            f.write(image_data["image"])

        images.append(
            {
                "coords": [(x0, y0), (x1, y1)],
                "filename": path,
            }
        )

    return images


def extract_text_from_image(file: bytes) -> str:
    """Extract text from an image using Google Cloud Vision API."""
    image = vision.Image(content=file)
    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        return texts[0].description.strip()
    return ""


def extract_boxes(filename: str, page_number: int) -> list[dict]:
    """
    Detect rectangular bounding boxes on a page image.
    Returns list of boxes with their coordinates and cropped image paths.
    """
    img = Image.open(filename)
    img_width, img_height = img.size

    # Minimum dimensions for a valid box (question/answer boxes)
    min_height = 100
    min_width = 200

    # Convert to grayscale for processing
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

    # Apply threshold to create binary image
    _, binary = cv2.threshold(img_cv, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by y position (top to bottom)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    box_data = []
    box_num = 1

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Filter: must be large enough and not the entire page
        if w > min_width and h > min_height:
            # Skip if this is essentially the whole page (within 5% margin)
            if w > img_width * 0.95 and h > img_height * 0.95:
                continue

            box_filename = f"boxes/page_{page_number}_box_{box_num}.png"
            box_img = img.crop((x, y, x + w, y + h))
            box_img.save(box_filename)

            box_data.append(
                {
                    "box_id": box_num,
                    "coords": [(x, y), (x + w, y + h)],
                    "filename": box_filename,
                    "diagrams": [],
                    "text": "",
                }
            )
            box_num += 1

    return box_data


def is_contained(inner_coords: list[tuple], outer_coords: list[tuple], tolerance: int = 5) -> bool:
    """
    Check if inner box is contained within outer box (with tolerance for edge cases).
    Coords format: [(x0, y0), (x1, y1)] where (x0, y0) is top-left and (x1, y1) is bottom-right
    """
    inner_x0, inner_y0 = inner_coords[0]
    inner_x1, inner_y1 = inner_coords[1]
    outer_x0, outer_y0 = outer_coords[0]
    outer_x1, outer_y1 = outer_coords[1]

    return (
        inner_x0 >= outer_x0 - tolerance
        and inner_y0 >= outer_y0 - tolerance
        and inner_x1 <= outer_x1 + tolerance
        and inner_y1 <= outer_y1 + tolerance
    )


def get_image_bytes(filename: str) -> bytes:
    """Load an image file and return its bytes."""
    with open(filename, "rb") as f:
        return f.read()


def process_page(doc: pymupdf.Document, page_number: int) -> dict:
    """
    Process a single page from the PDF.
    Returns a dict with page data including boxes, diagrams, and text.
    """
    print(f"Processing page {page_number}...")

    # Extract all images from the page
    page_images = extract_page_images(doc, page_number)

    if not page_images:
        return {
            "page": page_number,
            "has_boxes": False,
            "boxes": [],
            "diagrams": [],
            "text": "",
        }

    background_image = page_images[0]
    overlay_diagrams = page_images[1:]  # Higher quality chess diagrams

    # Detect bounding boxes on the background image
    boxes = extract_boxes(background_image["filename"], page_number)

    page_data = {
        "page": page_number,
        "has_boxes": len(boxes) > 0,
        "boxes": boxes,
        "diagrams": [],
        "text": "",
    }

    if boxes:
        # Link each overlay diagram to its containing box
        for diagram in overlay_diagrams:
            assigned = False
            for box in boxes:
                if is_contained(diagram["coords"], box["coords"]):
                    box["diagrams"].append(diagram["filename"])
                    assigned = True
                    break
            if not assigned:
                # Diagram not in any box - add to page-level diagrams
                page_data["diagrams"].append(diagram["filename"])

        # Extract text from each box
        for box in boxes:
            try:
                img_bytes = get_image_bytes(box["filename"])
                box["text"] = extract_text_from_image(img_bytes)
            except Exception as e:
                print(f"  Error extracting text from box {box['box_id']}: {e}")
                box["text"] = ""
    else:
        # No boxes - extract text from the whole page and list all diagrams
        page_data["diagrams"] = [d["filename"] for d in overlay_diagrams]
        try:
            # Crop bottom 5% to avoid page numbers
            img = Image.open(background_image["filename"])
            width, height = img.size
            cropped_img = img.crop((0, 0, width, int(height * 0.95)))

            img_byte_arr = BytesIO()
            cropped_img.save(img_byte_arr, format="PNG")
            page_data["text"] = extract_text_from_image(img_byte_arr.getvalue())
        except Exception as e:
            print(f"  Error extracting text from page: {e}")
            page_data["text"] = ""

    return page_data


def process_pdf(pdf_path: str, start_page: int = 1, end_page: int = None) -> list[dict]:
    """
    Process all pages of a PDF and extract structured data.
    """
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)

    if end_page is None:
        end_page = total_pages

    end_page = min(end_page, total_pages)

    results = []
    for page_num in range(start_page, end_page + 1):
        try:
            page_data = process_page(doc, page_num)
            results.append(page_data)
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
            results.append({
                "page": page_num,
                "has_boxes": False,
                "boxes": [],
                "diagrams": [],
                "text": "",
                "error": str(e),
            })

    doc.close()
    return results


if __name__ == "__main__":
    pdf_path = "pdfs/bobby_fischer_teaches_chess.pdf"

    # Process all pages
    results = process_pdf(pdf_path)

    # Save results to JSON
    with open("book_data.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nProcessed {len(results)} pages. Output saved to book_data.json")
