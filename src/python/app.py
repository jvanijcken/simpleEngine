from dataclasses import dataclass
from threading import Thread
from queue import Queue
from moveGeneration import generate_moves
from globals import *
from collections import namedtuple
from comp import pick_best_move


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


@dataclass
class Buffer:
    next_moves:     list[Move]
    next_positions: list[Board]


APP = App(
    board              = START_BOARD,
    selected_fields    = [],
    highlighted_fields = [],
    last_start_fields  = [],
    last_end_fields    = [],
    score              = 0,
    move_nr            = 0,
)

_moves, _boards = generate_moves(APP.board)
BUFFER = Buffer(
    next_moves     = _moves,
    next_positions = _boards
)

SCORE_QUEUE = Queue()
MOVE_QUEUE  = Queue()


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
    APP.board                = board
    APP.selected_fields      = []
    APP.highlighted_fields   = []
    APP.last_start_fields    = [move.start]
    APP.last_end_fields      = [move.end]
    APP.score                = 0

    moves, boards = generate_moves(APP.board)
    BUFFER.next_moves        = moves
    BUFFER.next_positions    = boards


def app_update(dt) -> bool:
    if MOVE_QUEUE.empty():
        return False

    result: Result = MOVE_QUEUE.get()
    if result.move_nr != APP.move_nr:
        return False

    make_move(result.move, result.board)
    return True

def move_calculation_process(next_moves, next_positions, move_nr, max_depth, max_time):
    best_move, best_position = pick_best_move(next_moves, next_positions, max_depth, max_time)
    result = Result(best_move, best_position, move_nr)
    MOVE_QUEUE.put(result)

def start_move_calculation(max_depth: int, max_time: int):
    Thread(
        target = move_calculation_process,
        args   = (BUFFER.next_moves, BUFFER.next_positions, APP.move_nr, max_depth, max_time),
        daemon = True
    ).start()










