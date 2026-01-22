import json
import os
from tempfile import NamedTemporaryFile

import requests
from google.cloud import vision
from PIL import Image

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../vision_api_key.json"
url = "https://helpman.komtera.lt/predict"

session = requests.Session()
client = vision.ImageAnnotatorClient()

image_directory = "epub/OEBPS/Images/"
images = os.listdir(image_directory)

puzzles = []

with open("puzzles.log", "w") as f:
    pass

for image in images:
    try:
        img = Image.open(f"{image_directory}/{image}")

        # get player
        color = img.getpixel((30, 260))
        player = ""
        if isinstance(color, tuple):
            player = "black" if sum(color) / 3 < 128 else "white"

        # (left, top, right, bottom)
        with NamedTemporaryFile("wb") as fp:
            cropped = img.crop((75, 0, img.width, img.height - 20))
            cropped.save(fp, format="png")

            with open(fp.name, "rb") as f:
                response = session.post(
                    url,
                    files={"file": (f"{fp.name}.png", f, "image/png")},
                )

        response.raise_for_status()
        fen = response.json()["results"][0]["fen"]

        with NamedTemporaryFile("wb") as fp:
            cropped = img.crop((0, 20, 40, 40))
            cropped.save(fp, format="png")

            with open(fp.name, "rb") as f:
                vision_image = vision.Image(content=f.read())

        response = client.text_detection(image=vision_image)
        number = response.full_text_annotation.text

        if player == "black":
            fen += " b - - 0 1"
        else:
            fen += " w - - 0 1"

        puzzles.append({"number": int(number), "fen": fen, "filename": image})

        log_message = f"{image} successful"

    except Exception as e:
        log_message = f"{image} failed: {e}"

    finally:
        print(log_message)
        with open("puzzles.log", "a") as f:
            f.write(f"{log_message}\n")

with open("puzzles.json", "w") as f:
    json.dump(puzzles, f, ensure_ascii=False, indent=4)
