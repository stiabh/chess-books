import os
import re
import shutil

chapters = [
    ["Pins", 2, 31],
    ["Back Rank Combin.", 33, 62],
    ["Knight Forks", 64, 93],
    ["Other Forks/D. Attacks", 95, 124],
    ["Discovered Checks", 126, 155],
    ["Double Checks", 157, 186],
    ["Discovered Attacks", 188, 217],
    ["Skewers", 219, 248],
    ["Double Threats", 250, 279],
    ["Promoting Pawns", 281, 310],
    ["Removing the Guard", 312, 341],
    ["Perpetual Check", 343, 372],
    ["Zugzwang/Stalemate", 374, 403],
    ["Quizzes", 404, 434],
]

diagrams = [f"diagram_{i}" for c in chapters for i in range(c[1], c[2] + 1)]

filenames = os.listdir("diagrams")
filenames.sort()

assert len(diagrams) == len(filenames)

for i, filename in enumerate(filenames):
    page = re.findall(r"page_\d+", filename)[0]
    shutil.copy(f"diagrams/{filename}", f"renamed/{page}_{diagrams[i]}.png")
