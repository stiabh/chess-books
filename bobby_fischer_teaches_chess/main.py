import json
import os
import re
from io import BytesIO

import cv2
import numpy as np
import pymupdf
from google.cloud import vision
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../vision_api_key.json"
os.makedirs("extracted", exist_ok=True)
os.makedirs("diagrams", exist_ok=True)


def extract_page_images(doc: pymupdf.Document, page_number: int) -> list[dict]:
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


# page = doc[59]
# page_images = page.get_images()
# image_index = page_image[-1][0]
# page.get_image_rects(image_index)


def extract_text_from_image(file: bytes) -> list[str]:
    image = vision.Image(content=file)

    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # lines = []

    # if texts:
    #     # first result contains all text
    #     for line in texts[0].description.split("\n"):
    #         if re.search(r"[a-zA-Z0-9]", line):  # and len(line) > 1:
    #             lines.append(line)

    return texts


def extract_boxes(filename: str) -> list[dict]:
    # Load your PNG file
    img = Image.open(filename)

    # Set minimum dimensions (adjust these based on your image)
    min_height = 100  # adjust based on your box sizes
    min_width = 200  # adjust based on your box sizes

    # Convert PIL image to OpenCV format
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)

    # Threshold to binary
    _, binary = cv2.threshold(img_cv, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by y position (top to bottom)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    box_data = []

    # Get bounding boxes and save each one
    box_num = 1
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        filename = f"box_{box_num}.png"

        if w > min_width and h > min_height:
            box_img = img.crop((x, y, x + w, y + h))
            box_img.save(filename)

            box_data.append(
                {
                    "coords": [(x, y), (x + w, y + h)],
                    "filename": filename,
                }
            )
            box_num += 1

    return box_data


def is_contained(inner_coords: list[tuple], outer_coords: list[tuple]) -> bool:
    """
    Check if inner box is completely contained within outer box.
    Coords format: [(x0, y0), (x1, y1)] where (x0, y0) is top-left and (x1, y1) is bottom-right
    """
    inner_x0, inner_y0 = inner_coords[0]
    inner_x1, inner_y1 = inner_coords[1]
    outer_x0, outer_y0 = outer_coords[0]
    outer_x1, outer_y1 = outer_coords[1]

    return (
        inner_x0 >= outer_x0
        and inner_y0 >= outer_y0
        and inner_x1 <= outer_x1
        and inner_y1 <= outer_y1
    )


if __name__ == "__main__":
    pdf_path = "pdfs/bobby_fischer_teaches_chess.pdf"
    doc = pymupdf.open(pdf_path)
    page_images = extract_page_images(doc, 156)
    boxes = extract_boxes(page_images[0]["filename"])
    for i, image in enumerate(page_images[1:]):
        for box in boxes:
            if is_contained(image["coords"], box["coords"]):
                page_images[i + 1]["box"] = box["filename"]

    breakpoint()


# page_text = []


# for page in range(1, len(doc) + 1):
#     log_message = ""
#     try:
#         paths = extract_page_images(doc, page)
#         diagrams = paths[1:]

#         # Load image and crop bottom 10%
#         img = Image.open(paths[0])
#         width, height = img.size
#         cropped_img = img.crop((0, 0, width, int(height * 0.95)))

#         img_byte_arr = BytesIO()
#         cropped_img.save(img_byte_arr, format="PNG")
#         content = img_byte_arr.getvalue()

#         lines = extract_text_from_image(content)
#         page_text.append({"page": page, "text": "\n".join(lines), "diagrams": diagrams})
#         log_message += f"Page {page} ok"

#     except Exception as e:
#         log_message += f"Page {page} failed: {e}"

#     finally:
#         print(log_message)


# with open("text.json", "w") as f:
#     json.dump(page_text, f, ensure_ascii=False, indent=4)
