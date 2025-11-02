from dataclasses import dataclass
from threading import Thread
from queue import Empty
from moveGeneration import generate_moves
from globals import *
from collections import namedtuple
from random import randint
from multiprocessing import Process, Queue
from score_calculation import start_score_calculation


Result = namedtuple("Result", ["move", "board", "move_nr"])


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
START_BOARD = Board(
    pieces     = START_PIECES,
    castles    = [1, 1, 1, 1],
    en_passant = -1,
    is_white   = True
)


@dataclass
class App:
    board:              Board
    selected_fields:    list[int]
    highlighted_fields: list[int]
    last_start_fields:  list[int]
    last_end_fields:    list[int]
    score:              int
    move_nr:            int
    eval:               tuple[int, int, float]
    history:            list[Board]


@dataclass
class Buffer:
    next_moves:     list[Move]
    next_positions: list[Board]



APP = App(  # this is read by UI
    board              = START_BOARD,
    selected_fields    = [],
    highlighted_fields = [],
    last_start_fields  = [],
    last_end_fields    = [],
    score              = 0,
    move_nr            = 0,
    eval               = (0, 0, 0),
    history            = []
)

_moves, _boards = generate_moves(APP.board)
BUFFER = Buffer(
    next_moves     = _moves,
    next_positions = _boards
)


UPDATE_ID = randint(0, 10**10)
UPDATE_QUEUE = Queue()


def check_for_app_updates(dt) -> bool:
    updates = False

    while True:
        try:
            property_name, value = UPDATE_QUEUE.get_nowait()
            updates = True

            if not hasattr(APP, property_name):
                raise ValueError()

            setattr(APP, property_name, value)
        except Empty:
            break

    return updates


def square_click(index: int) -> None:
    own_pieces = [0, 1, 2, 3, 4, 5] if APP.board.is_white else [6, 7, 8, 9, 10, 11]
    piece: int = APP.board.pieces[index]

    if not APP.selected_fields and piece != NO_PIECE:  # just select a piece
        if piece in own_pieces:
            APP.selected_fields    = [index]
            APP.highlighted_fields = [m.end for m in BUFFER.next_moves if m.start == index]
        else:
            APP.selected_fields    = []
            APP.highlighted_fields = []
        return


    for move, board in zip(BUFFER.next_moves, BUFFER.next_positions):
        is_selected_move: bool = move.start in APP.selected_fields and move.end == index

        if is_selected_move:
            make_move(move, board)
            break

    # No moves found
    else:
        if piece in own_pieces:
            APP.selected_fields    = [index]
            APP.highlighted_fields = [m.end for m in BUFFER.next_moves if m.start == index]
        else:
            APP.selected_fields    = []
            APP.highlighted_fields = []

    return


def make_move(move: Move, board: Board):
    global UPDATE_ID
    UPDATE_ID = randint(0, 10**10)

    APP.board                = board
    APP.selected_fields      = []
    APP.highlighted_fields   = []
    APP.last_start_fields    = [move.start]
    APP.last_end_fields      = [move.end]
    APP.score                = 0

    moves, boards = generate_moves(APP.board)
    BUFFER.next_moves        = moves
    BUFFER.next_positions    = boards
    update_score()


def update_score():
    start_score_calculation(
        APP.board.pieces[:],
        APP.board.castles[:],
        APP.board.en_passant,
        0 if APP.board.is_white else 1,
        UPDATE_QUEUE)



