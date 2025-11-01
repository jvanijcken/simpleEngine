from threading import Thread
from PyChess import direct_search
from globals import *


def pick_best_move(
        moves:     list[Move],
        positions: list[Board],
        max_depth: int,
        max_time:  float) -> tuple[Move, Board] | tuple[None, None]:
    best_move:       None | Move  = None
    nest_position:   None | Board = None


    for depth in range(max_depth):
        best_score = -INF

        for move, position in zip(moves, positions):
            score, _ = direct_search(
                position.pieces,
                position.castles,
                position.en_passant,
                0 if position.is_white else 1,
                depth,
            )

            if score > best_score:
                best_score     = score
                best_move      = move
                nest_position  = position

    return best_move, nest_position

