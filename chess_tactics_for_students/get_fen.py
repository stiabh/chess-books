import json
import os
import re

import requests

url = "https://helpman.komtera.lt/predict"

filenames = os.listdir("renamed")

fens = []

session = requests.Session()

with open("get_fen.log", "w") as f:
    pass

for filename in filenames:
    try:
        response = session.post(
            url,
            files={"file": (filename, open(f"renamed/{filename}", "rb"), "image/png")},
        )
        response.raise_for_status()

        fen = response.json()["results"][0]["fen"]

        page = int(re.findall(r"page_(\d+)", filename)[0])
        diagram = int(re.findall(r"diagram_(\d+)", filename)[0])

        fens.append(
            {"filename": filename, "page": page, "diagram": diagram, "fen": fen}
        )
        log_message = f"{filename} successful"

    except Exception as e:
        log_message = f"{filename} failed: {e}"

    finally:
        print(log_message)
        with open("get_fen.log", "a") as f:
            f.write(f"{log_message}\n")

with open("fens.json", "w") as f:
    json.dump(fens, f, ensure_ascii=False, indent=4)
