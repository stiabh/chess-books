import json
import os
import re
from io import BytesIO

import pymupdf
from google.cloud import vision
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../vision_api_key.json"
os.makedirs("extracted", exist_ok=True)
os.makedirs("diagrams", exist_ok=True)


def extract_page_images(doc: pymupdf.Document, page_number: int) -> list[str]:
    page_images = doc.get_page_images(page_number - 1)
    paths = []
    for i, page_image in enumerate(page_images):
        image_index = page_image[0]
        image_data = doc.extract_image(image_index)
        path = f"extracted/page_{page_number}_{i}_{image_index}.png"
        with open(path, "wb") as f:
            f.write(image_data["image"])
        paths.append(path)

    return paths


def extract_text_from_image(file: bytes) -> list[str]:
    image = vision.Image(content=file)

    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)
    texts = response.text_annotations

    lines = []

    if texts:
        # first result contains all text
        for line in texts[0].description.split("\n"):
            if re.search(r"[a-zA-Z0-9]", line) and len(line) > 1:
                lines.append(line)

    return lines


pdf_path = "pdfs/bobby_fischer_teaches_chess.pdf"
doc = pymupdf.open(pdf_path)
page_text = []

for page in range(1, len(doc) + 1):
    log_message = ""
    try:
        paths = extract_page_images(doc, page)
        diagrams = paths[1:]

        # Load image and crop bottom 10%
        img = Image.open(paths[0])
        width, height = img.size
        cropped_img = img.crop((0, 0, width, int(height * 0.95)))

        img_byte_arr = BytesIO()
        cropped_img.save(img_byte_arr, format="PNG")
        content = img_byte_arr.getvalue()

        lines = extract_text_from_image(content)
        page_text.append({"page": page, "text": "\n".join(lines), "diagrams": diagrams})
        log_message += f"Page {page} ok"

    except Exception as e:
        log_message += f"Page {page} failed: {e}"

    finally:
        print(log_message)


with open("text.json", "w") as f:
    json.dump(page_text, f, ensure_ascii=False, indent=4)
