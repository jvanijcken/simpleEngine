import PyChess
import re


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

def convert_test_board(board_string: str):
    pattern = re.compile(
        r"(?s)board:\s*(?P<board>(?:[bwPRNBKQ_]{2}(?:\s+|$)){64})"
        r".*?castle\s+rights:\s*(?P<castle>\d+)"
        r".*?en\s+passant:\s*(?P<enpassant>-?\d+)"
        r".*?color:\s*(?P<color>[WB])"
    )

    if not (match := pattern.search(board_string)):
        raise ValueError("Invalid board string as input")

    pieces:       list[str] = match.group("board").split()
    number_board: list[int] = [PIECE_NUMBERS[x] for x in pieces]

    castles:      list[int] = [int (x) for x in match.group("castle")]
    en_passant:         int = int(match.group("enpassant"))
    color:              int = 1 if match.group("color") == "B" else 0

    board = PyChess.Board(number_board, castles, en_passant, color)
    return board


def print_board(board: PyChess.Board):
    print("Board: ")
    for i in range(64):
        piece_number: int  = board.board[i]
        add_newline:  bool = (i % 8 == 7)
        print(f"{PIECE_STRINGS[piece_number]} ", end = "\n" if add_newline else "")

    print(f"castle rights: ", end = "")
    for i in range(4):
        print(board.castles[i], end = "\n" if i == 3 else "")

    print(f"en passant: {board.en_passant}")
    print(f"color: " + "W" if board.color == 0 else "B")


TEST_BOARD = \
    """
    board:
    bR bN bB bQ bK bB bN bK
    bP bP bP bP bP bP bP bP
    __ __ __ __ __ __ __ __
    __ __ __ __ __ __ __ __
    __ __ __ __ __ __ __ __
    __ __ __ __ __ __ __ __
    wP wP wP wP wP wP wP wP
    wR wN wB wQ wK wB wN wK
    
    castle rights: 1111
    en passant:    -1
    color:         W
    """


if __name__ == "__main__":
    test_board: PyChess.Board = convert_test_board(TEST_BOARD)
    result = PyChess.pyIDS(test_board, 0, 12, 1)


    print(f"{result = }")
    for ii in result[1]:
        print_board(ii)

