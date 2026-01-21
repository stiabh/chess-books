import json
import os

with open("puzzles.json") as f:
    puzzles = json.load(f)

with open("solutions.json") as f:
    solutions = json.load(f)

with open("chapters.json") as f:
    chapters = json.load(f)

puzzles = {p["number"]: p for p in puzzles}
solutions = {s["puzzle"]: s for s in solutions}
themes = []
for chapter in chapters:
    for theme in chapter["themes"]:
        theme["chapter"] = chapter["chapter"]
        themes.append(theme)
themes.sort(key=lambda x: x["first_exercise"])

os.makedirs("chapters", exist_ok=True)
for i in range(len(themes)):
    current_theme_exercise = themes[i]["first_exercise"]
    if i == len(themes) - 1:
        next_theme_exercise = len(solutions) + 1
    else:
        next_theme_exercise = themes[i + 1]["first_exercise"]
    chapter_filename = (
        "chapter_"
        + themes[i]["chapter"]
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("/", "_")
        + ".pgn"
    )
    with open(f"chapters/{chapter_filename}", "a") as f:
        f.write("\n")
        for j in range(current_theme_exercise, next_theme_exercise):
            try:
                f.write(f'[Event "Exercise {j} - {themes[i]["theme"]}"]\n')
                f.write(f'[FEN "{puzzles[j]["fen"]}"]\n')
                for move in solutions[j]["moves"]:
                    f.write(f"{move['move']} {{{move['annotation']}}}\n")
                f.write("\n")
            except Exception as e:
                print(f"error: {e}")
