import os
import re
from tempfile import NamedTemporaryFile

import requests
from PIL import Image

BASE_PATH = "epub/OEBPS/Text"
FEN_API_URL = "https://helpman.komtera.lt/predict"


def fen_from_image(session: requests.Session, image_path: str) -> str:
    img = Image.open(image_path)
    if img.width / img.height > 2:
        cropped = img.crop((0, 0, img.height, img.height))
    else:
        cropped = img.crop((0, 0, img.height / 2, img.height / 2))

    with NamedTemporaryFile("wb") as fp:
        cropped.save(fp, format="png")

        with open(fp.name, "rb") as f:
            response = session.post(
                FEN_API_URL,
                files={"file": (f"{fp.name}.png", f, "image/png")},
            )

    response.raise_for_status()
    fen = response.json()["results"][0]["fen"]

    return fen


session = requests.Session()

os.makedirs("chapter_intros", exist_ok=True)

for filename in os.listdir(BASE_PATH):
    if not filename.endswith("_split_000.html"):
        continue

    with open(f"{BASE_PATH}/{filename}") as f:
        data = f.readlines()

    data = " ".join([d.strip() for d in data])

    title = re.findall(r"<title>(.*?)</title>", data)[0]
    text = re.findall(r"<p .*?>(.*?)</p>", data)
    text = [t for t in text if t != "\xa0"]
    images = re.findall(r'<img src="(.*?)".*?/>', data)

    image_paths = [f"{BASE_PATH}/{img}" for img in images]

    fens = [fen_from_image(session, img) for img in image_paths]

    chapter_filename = (
        title.lower().replace(" ", "_").replace(":", "").replace("/", "_")
    ) + ".txt"

    with open(f"chapter_intros/{chapter_filename}", "w") as f:
        for fen in fens:
            f.write(f'[Event "{title}"]\n')
            f.write(f'[FEN "{fen} w - - 0 1"]\n')
            f.write("{\n\n}\n\n")
        f.write("\n" + "\n\n".join(text))

    print(chapter_filename)
