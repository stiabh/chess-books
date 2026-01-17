import json
import re

import chess
import chess.pgn
from chess.pgn import (
    NAG_BLUNDER,
    NAG_BRILLIANT_MOVE,
    NAG_DUBIOUS_MOVE,
    NAG_GOOD_MOVE,
    NAG_MISTAKE,
    NAG_SPECULATIVE_MOVE,
)


def combine_jsons():
    with open("fens.json") as f:
        fens: list[dict] = json.load(f)

    with open("solutions.json") as f:
        solutions: list[dict] = json.load(f)

    puzzles = []

    for i, fen in enumerate(fens):
        solution = [s for s in solutions if s["diagram"] == fen["diagram"]][0]
        puzzles.append(fen | solution)

    puzzles.sort(key=lambda x: x["diagram"])

    return puzzles


def convert_to_pgn(puzzle: dict, chapter: str = "") -> chess.pgn.Game:
    fen = puzzle["fen"]
    main_line = puzzle["main_line"]

    moves = []
    for line in main_line:
        line = line.replace(" move", "_move")
        line = re.sub(r"\d\. ", "", line)
        moves += line.split()

    if moves[0] == "...":
        fen += " b"
    else:
        fen += " w"

    if any(re.findall(r"[^\.] 0-0", line) for line in main_line):
        # black can castle kingside
        fen += " k -"
    elif any(re.findall(r"\d\. 0-0", line) for line in main_line):
        # white can castle kingside
        fen += " K -"
    else:
        # castling unknown or irrelevant
        fen += " - -"

    fen += " 0 1"

    board = chess.Board(fen)
    game = chess.pgn.Game()
    game.setup(board)
    diagram = puzzle["diagram"]
    event = f"Diagram {diagram}"
    if chapter:
        event = f"{event} - {chapter}"
    game.headers["Event"] = event
    node = game

    for move in moves:
        if move == "...":
            continue

        elif move == "stalemate" or move == "draw":
            game.headers["result"] = "1/2-1/2"
            break

        elif "move" in move:
            symbol = move.split("_")[0]
            legal_moves = [
                m
                for m in board.legal_moves
                if board.piece_at(m.from_square).symbol().lower() == symbol.lower()
                or symbol == "Any"
            ]
            move = legal_moves[0]
            board.push(move)
            node = node.add_variation(board.move_stack[-1])

        else:
            # in case of alternatives, select first alternative
            # example: Qg4/d6/b6 -> Qg4
            move = re.sub(r"(\w\w?\d)/.*", r"\1", move, flags=re.IGNORECASE)

            # example: dxe8=Q/R# -> dxe8=Q#
            move = re.sub(r"(\w)/\w", r"\1", move, flags=re.IGNORECASE)

            nags = []
            nag_map = {
                "!!": NAG_BRILLIANT_MOVE,
                "??": NAG_BLUNDER,
                "!?": NAG_SPECULATIVE_MOVE,
                "?!": NAG_DUBIOUS_MOVE,
                "!": NAG_GOOD_MOVE,
                "?": NAG_MISTAKE,
            }
            for annotation, nag in nag_map.items():
                if annotation in move:
                    move = move.replace(annotation, "")
                    nags = [nag]
            board.push_san(move)
            node = node.add_variation(board.move_stack[-1], nags=nags)

    return game


if __name__ == "__main__":
    puzzles = combine_jsons()

    chapters = [
        ["Pins", 2, 31],
        ["Back Rank Combinations", 33, 62],
        ["Knight Forks", 64, 93],
        ["Other Forks/Discovered Attacks", 95, 124],
        ["Discovered Checks", 126, 155],
        ["Double Checks", 157, 186],
        ["Discovered Attacks", 188, 217],
        ["Skewers", 219, 248],
        ["Double Threats", 250, 279],
        ["Promoting Pawns", 281, 310],
        ["Removing the Guard", 312, 341],
        ["Perpetual Check", 343, 372],
        ["Zugzwang/Stalemate", 374, 403],
        # ["quizzes", 404, 434],
    ]

    for i, chapter in enumerate(chapters):
        games = []
        chapter_name, first_diagram, last_diagram = chapter
        print(chapter_name)
        for puzzle in puzzles:
            if first_diagram <= puzzle["diagram"] and puzzle["diagram"] <= last_diagram:
                games.append(convert_to_pgn(puzzle, chapter_name))

        chapter_name = chapter_name.lower().replace(" ", "_").replace("/", "_")
        filename = f"pgn/{(i + 1):02}_{chapter_name}.pgn"

        with open(filename, "w"):
            pass

        for game in games:
            print(game, file=open(filename, "a"), end="\n\n")
