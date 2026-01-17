import json
import os
import re
from collections import defaultdict

chapter_dir = "epub/OEBPS/Text"

chapters = defaultdict(list)

for filename in os.listdir(chapter_dir):
    with open(f"{chapter_dir}/{filename}") as f:
        data = f.read()
    matches = re.findall(r'<h2 class="style2">(.*?) – Guided', data)
    if matches:
        theme = matches[0]
        first_exercise = re.findall(r'<a href=".*?">Exercise (\d+)</a>', data)[0]
        chapter_number, chapter_name = re.findall(
            r"<title>Chapter (\d+): (.*?)</title>", data
        )[0]
        chapter = f"{int(chapter_number):02}. {chapter_name}"
        chapters[chapter].append(
            {"theme": theme, "first_exercise": int(first_exercise)}
        )

chapters = [{"chapter": k, "themes": v} for k, v in chapters.items()]
chapters.sort(key=lambda x: x["chapter"])
for i in range(len(chapters)):
    chapters[i]["themes"].sort(key=lambda x: x["first_exercise"])
with open("chapters.json", "w") as f:
    json.dump(chapters, f, ensure_ascii=False, indent=4)
