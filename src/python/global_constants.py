from dataclasses import dataclass

START_PIECES = [
    7,  8,  9, 10, 11,  9,  8,  7,
    6,  6,  6,  6,  6,  6,  6,  6,
    -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1,
    -1, -1, -1, -1, -1, -1, -1, -1,
    0,  0,  0,  0,  0,  0,  0,  0,
    1,  2,  3,  4,  5,  3,  2,  1,
]


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

RANK1 = [A1, B1, C1, D1, E1, F1, G1, H1]
RANK8 = [A8, B8, C8, D8, E8, F8, G8, H8]

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

COORD_NAMES = [
    'A8', 'B8', 'C8', 'D8', 'E8', 'F8', 'G8', 'H8',
    'A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'H7',
    'A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6',
    'A5', 'B5', 'C5', 'D5', 'E5', 'F5', 'G5', 'H5',
    'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'G4', 'H4',
    'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3',
    'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
    'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1',
]

@dataclass(frozen=True)
class Board:
    pieces     : list[int]
    castles    : list[int]
    en_passant : int
    is_white   : bool

    def __repr__(self):
        s = ""
        for i, p in enumerate(self.pieces):
            s+= f"{PIECE_STRINGS[p]} "
            if i % 8 == 7:
                s += "\n"
        return s


@dataclass
class Move:
    start          : int
    end            : int
    end_piece      : int
    board          : Board
    notation       : str
    score          : int

    def __lt__(self, other):
        return self.score < other.score

    def __mt__(self, other):
        return self.score > other.score

    def __eq__(self, other):
        return self.score == other.score


START_BOARD = Board(
    pieces     = START_PIECES,
    castles    = [1, 1, 1, 1],
    en_passant = -1,
    is_white   = True
)






