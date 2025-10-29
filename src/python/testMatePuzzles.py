from PyChess import time_limited_iterative_deepening_search
from testInterface import convert_test_board, print_board, Board
from UserInterface import show_in_new_ui, CTk
from moveGeneration import generate_moves
from globals import *


IDS = time_limited_iterative_deepening_search


def get_move_seq(string: str, depth: int):
    result: list[Board] = []
    board: Board = convert_test_board(string)

    best_position: board = board
    result.append(best_position)

    _ = IDS(board.pieces, board.castles, board.en_passant, 0 if board.is_white else 1, depth, 30)  # should cause caching of all positions

    for i in range(1, depth):

        best_score:    int         = -INF
        new_positions: list[Board] = generate_moves(best_position)[1]

        if len(new_positions) == 0:
            print("WARNING: early return")
            return result

        for new_position in new_positions:

            pieces:     list[int] = new_position.pieces
            castles:    list[int] = new_position.castles
            en_passant:       int = new_position.en_passant
            color:            int = 0 if new_position.is_white else 1

            score = IDS(pieces, castles, en_passant, color, depth - i, 30)
            if not best_position.is_white:
                score *= -1

            if score > best_score:
                best_score = score
                best_position = new_position

        result.append(best_position)

    return result


def test_position(board_string: str, depth: int):
    # best_sequence: list[Board] = get_move_seq(board_string, depth)
    # ui: CTk = show_in_new_ui(best_sequence)

    board: Board = convert_test_board(board_string)
    score: int   = IDS(board.pieces, board.castles, board.en_passant, 0 if board.is_white else 1, depth, 1)
    print(f"{score = }")
    return CTk()

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
    ).mainloop()

    test_position(
        """
        board:
        __ __ __ __ __ __ __ __
        __ __ __ __ wQ __ __ __
        __ __ __ __ __ __ bK bP
        __ __ bP __ __ __ __ __
        __ __ __ __ __ __ __ __
        __ __ __ __ __ wP __ __
        __ __ __ __ __ wK wP wP
        bR __ bQ __ __ __ __ __
        castle rights: 0000
        en passant:    -1
        color:         W
        """,
        11
    ).mainloop()

    #test_position(
    #    """
    #    board:
    #    __ __ __ __ __ __ bR bK
    #    __ __ __ __ __ __ wR __
    #    __ __ wR __ __ __ wK __
    #    bP __ __ __ __ __ bP __
    #    bR __ __ __ __ __ __ __
    #    __ __ __ __ __ __ __ __
    #    __ __ __ __ __ __ __ __
    #    __ __ __ __ __ __ __ __
    #    castle rights: 0000
    #    en passant:    -1
    #    color:         W
    #    """,
    #    5
    #).mainloop()
    #
    #test_position(
    #    """
    #    board:
    #    __ __ __ __ __ __ __ __
    #    __ __ __ __ __ __ bP bP
    #    __ __ __ __ bQ __ bK __
    #    __ __ __ __ __ __ __ __
    #    __ __ bR __ bP __ wP wP
    #    __ __ __ __ wP wQ wK __
    #    __ __ __ __ __ wP __ __
    #    __ __ __ __ __ __ __ __
    #    castle rights: 0000
    #    en passant:    -1
    #    color:         W
    #    """,
    #    7
    #).mainloop()


if __name__ == "__main__":
    main()

