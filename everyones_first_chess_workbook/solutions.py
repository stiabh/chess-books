import json
import re

PIECE_REGEX = r"[KQNBRa-h]?[a-h]?x?[a-h][1-8][\+#]?[\?!]?[\?!]?"
MOVE_PAIR_REGEX = rf"\s(\d+\.(\.\.)?(({PIECE_REGEX})(\s+{PIECE_REGEX})?))"

with open("epub/OEBPS/Text/chapter0032.html") as f:
    html = f.read()

matches = re.findall(r'<a href="chapter.*?">(.*?)</a>', html)
solutions = []

for match in matches:
    match = re.sub(MOVE_PAIR_REGEX, r";\1;", match)
    match = re.sub(r"([^\d\.][\.!])", r"\1;", match)
    match_split = match.split(";")
    match_split = [m.strip() for m in match_split if m]
    puzzle = match_split.pop(0)

    puzzle_info = ""
    if len(match_split) > 1:
        if "-?" in match_split[-1]:
            puzzle_info = match_split.pop(-1)

    solution = {"puzzle": int(puzzle), "puzzle_info": puzzle_info, "moves": []}
    moves = []
    move = ""
    annotation = ""
    while len(match_split) > 0:
        part = match_split.pop()
        if re.match(r"^\d", part):
            move = part
            moves.insert(0, {"move": move, "annotation": annotation})
            annotation = ""
        else:
            annotation = part
    if annotation:
        moves.insert(0, {"move": move, "annotation": annotation})

    solution["moves"] = moves
    solutions.append(solution)

with open("matches.txt", "w") as f:
    f.write("\n".join(matches))

with open("solutions.json", "w") as f:
    json.dump(solutions, f, ensure_ascii=False, indent=4)
