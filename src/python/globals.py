from dataclasses import dataclass


PIECE_NUMBERS = {
    "wP": 0,
    "wR": 1,
    "wN": 2,
    "wB": 3,
    "wQ": 4,
    "wK": 5,
    "bP": 6,
    "bR": 7,
    "bN": 8,
    "bB": 9,
    "bQ": 10,
    "bK": 11,
    "__": -1
}
PIECE_STRINGS = [
    "wP",
    "wR",
    "wN",
    "wB",
    "wQ",
    "wK",
    "bP",
    "bR",
    "bN",
    "bB",
    "bQ",
    "bK",
    "__",
]

CHESS_SYMBOLS = [
    "♙", "♖", "♘", "♗", "♕", "♔",
    "♟", "♜", "♞", "♝", "♛", "♚",
    ""  # for index -1 (NO_PIECE)
]

@dataclass
class Board:
    pieces: list[int]
    castles: list[int]
    en_passant: int
    color: int