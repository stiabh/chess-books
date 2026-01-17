# https://www.datacamp.com/tutorial/mistral-ocr

import os

import datauri
from dotenv import load_dotenv
from mistralai import Mistral, OCRImageObject, OCRResponse

load_dotenv()


def save_image(image: OCRImageObject):
    parsed = datauri.parse(image.image_base64)
    with open(image.id, "wb") as file:
        file.write(parsed.data)


def create_markdown_file(ocr_response: OCRResponse, output_filename: str = "output.md"):
    with open(output_filename, "wt") as f:
        for page in ocr_response.pages:
            f.write(page.markdown)
            for image in page.images:
                save_image(image)


def upload_file(filename: str):
    uploaded_pdf = client.files.upload(
        file={
            "file_name": filename,
            "content": open(filename, "rb"),
        },
        purpose="ocr",
    )
    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

    return signed_url.url


api_key = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

filename = "solutions.pdf"

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": upload_file(filename),
    },
    include_image_base64=True,
)

create_markdown_file(ocr_response, "solutions.md")
