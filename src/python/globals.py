from dataclasses import dataclass
from xml.etree.ElementTree import C14NWriterTarget

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

WP = 0
WR = 1
WN = 2
WB = 3
WQ = 4
WK = 5
BP = 6
BR = 7
BN = 8
BB = 9
BQ = 10
BK = 11

A8 = 0
B8 = 1
C8 = 2
D8 = 3
E8 = 4
F8 = 5
G8 = 6
H8 = 7

A1 = 56
B1 = 57
C1 = 58
D1 = 59
E1 = 60
F1 = 61
G1 = 62
H1 = 63

BLACK_QUEENSIDE = 0
BLACK_KINGSIDE  = 1
WHITE_QUEENSIDE = 2
WHITE_KINGSIDE  = 3

WHITE_PIECES = [ 0,  1,  2,  3,  4,  5]
BLACK_PIECES = [ 6,  7,  8,  9, 10, 11]

NO_MOVE   = -1
NO_PIECE  = -1
NO_CASTLE = -1

INF = 10000000

@dataclass
class Board:
    pieces     : list[int]
    castles    : list[int]
    en_passant : int
    is_white   : bool


@dataclass
class Move:
    start: int
    end: int
    start_piece: int
    end_piece: int
    captured_piece: int
    is_white: bool
    castle_type: int = NO_CASTLE


@dataclass
class MPTask:
    board       : Board
    start_depth : int
    update_id   : int


@dataclass
class MPResult:
    board                   : Board
    depth                   : int
    score                   : int
    calculation_interrupted : bool
    update_id               : int
    hits                    : int
    misses                  : int
    conflicts               : int
    writes                  : int






