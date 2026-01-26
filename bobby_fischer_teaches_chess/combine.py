import json
import re
from collections import defaultdict

with open("text.json") as f:
    data = json.load(f)

data = [d for d in data if d["page"] >= 43 and d["page"] < 100]

pairs = defaultdict(list)

for d in data:
    puzzle = 0
    text = []
    for t in d["text"].split("\n"):
        if re.match(r"^\d+$", t):
            if puzzle > 0:
                pairs[puzzle].append(" ".join(text))
            puzzle = int(t)
            text = []
        else:
            text.append(t)
    if text:
        pairs[puzzle].append(" ".join(text))
    if len(d["diagrams"]) == 2:
        pairs[puzzle - 1].append(d["diagrams"][0])
        pairs[puzzle].append(d["diagrams"][1])
    else:
        pairs[puzzle] += d["diagrams"]

with open("combined.json", "w") as f:
    json.dump(pairs, f, ensure_ascii=False, indent=4)
