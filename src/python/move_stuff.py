from dataclasses import dataclass
from global_constants import WK, BK, COORD_NAMES, Move


def build_move(start, end, start_board, end_board, score):
    notation = get_notation(start, end, start_board, end_board)
    end_piece = end_board.pieces[end]
    return Move(start, end, end_piece, end_board, notation, score)


def get_notation(start: int, end: int, start_board, end_board):  # todo add castling moves and promotion


    result = ""
    pcs = [
        "♟", "♜", "♞", "♝", "♛", "♚",
        "♙", "♖", "♘", "♗", "♕", "♔",
        ""  # for index -1 (NO_PIECE)
    ]
    start_piece    = pcs[ start_board.pieces[start] ]
    end_piece      = pcs[ end_board.pieces[end]   ]
    captured_piece = pcs[ start_board.pieces[end]   ]

    if start_board.pieces[start] in [WK, BK]:
        if end - start == -2:
            return f"{start_piece}O-O-O"
        if end - start == +2:
            return f"{start_piece}O-O"

    if start_piece != end_piece:
        result += f"{start_piece}{COORD_NAMES[start]}>{end_piece}{COORD_NAMES[end]}"
    else:
        result += f"{start_piece}{COORD_NAMES[start]}>{COORD_NAMES[end]}"

    if captured_piece != "":
        result += f"x{captured_piece}"
    else:
        result += ""

    return result


