# import re

# with open("solutions_replaced.md") as f:
#     text = f.read()

# diagrams = re.findall(r"(Diagram .*?)[Diagram|$]", text, flags=re.DOTALL)

# for diagram in diagrams[:60]:
#     diagram = diagram.strip().split("\n")
#     main_line = [d.split("\t")[0] for d in diagram]
#     print(" ".join(main_line))

import json
import re

with open("solutions_replaced.md") as f:
    lines = f.readlines()

diagram = 0
diagrams = {0: ""}

for line in lines:
    if line.startswith("Diagram"):
        diagram = int(line.replace("Diagram ", "").strip())
        diagrams[diagram] = ""
    else:
        diagrams[diagram] += f"\n{line}"

diagrams.pop(0)

solutions = []
for diagram, moves in diagrams.items():
    moves = re.sub(r"\n\n+", r"\n", moves)
    moves = re.sub(r"  +", " ", moves)
    moves = moves.strip().split("\n")
    main_line = [m.split("\t")[0].strip() for m in moves]
    try:
        variation = [m.split("\t")[1].strip() for m in moves]
    except Exception:
        variation = []

    solutions.append(
        {
            "diagram": diagram,
            "main_line": main_line,
            "variation": variation,
        }
    )

with open("solutions.json", "w") as f:
    json.dump(solutions, f, ensure_ascii=False, indent=4)
