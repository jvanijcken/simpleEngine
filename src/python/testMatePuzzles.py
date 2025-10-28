from PyChess import time_limited_iterative_deepening_search
from testInterface import convert_test_board, print_board, Board
# from UserInterface import show_in_new_ui

IDS = time_limited_iterative_deepening_search


def test_position(string: str, depth: int):
    board: Board = convert_test_board(string)
    score = IDS(board.pieces, board.castles, board.en_passant, board.color, depth, 30.0)
    print(f"{score = }")

def main():
    test_position(
        """
        board:
        __ __ __ __ __ __ __ __
        __ __ __ __ wQ __ __ __
        __ __ wN __ __ __ bK bP
        __ __ bP __ __ __ __ __
        __ __ __ __ __ __ __ __
        __ __ __ __ __ wP __ __
        __ __ __ __ __ wK wP wP
        bR __ bQ __ __ __ __ __
        castle rights: 0000
        en passant:    -1
        color:         W
        """,
        7
    )

    test_position(
        """
        board:
        __ __ __ __ __ __ bR bK
        __ __ __ __ __ __ wR __
        __ __ wR __ __ __ wK __
        bP __ __ __ __ __ bP __
        bR __ __ __ __ __ __ __
        __ __ __ __ __ __ __ __
        __ __ __ __ __ __ __ __
        __ __ __ __ __ __ __ __
        castle rights: 0000
        en passant:    -1
        color:         W
        """,
        5
    )

    test_position(
        """
        board:
        __ __ __ __ __ __ __ __
        __ __ __ __ __ __ bP bP
        __ __ __ __ bQ __ bK __
        __ __ __ __ __ __ __ __
        __ __ bR __ bP __ wP wP
        __ __ __ __ wP wQ wK __
        __ __ __ __ __ wP __ __
        __ __ __ __ __ __ __ __
        castle rights: 0000
        en passant:    -1
        color:         W
        """,
        7
    )


if __name__ == "__main__":
    main()