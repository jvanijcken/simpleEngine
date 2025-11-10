from queue import Empty
from moveGeneration import generate_moves
from globals import *
from dataclasses import dataclass
from random import randint
from multiprocessing import Queue, Process, Event
from MPworkers import MPWorker
from time import time


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
    board                   : Board

    # UI board info
    selected_fields         : list[int]
    highlighted_fields      : list[int]
    last_start_fields       : list[int]
    last_end_fields         : list[int]

    # analysis              :
    time_of_last_move       : float
    time_of_last_update     : float
    best_position           : Board | None
    score                   : int
    depth                   : int
    move_nr                 : int

    # settings              :
    white_player_cpu        : bool
    black_player_cpu        : bool
    cpu_move_time_sec       : float

    history                 : list[Board]
    next_moves              : dict[tuple[int, int], Board]

    update_id               : int


APP = App(  # this is read by UI
    board                   = START_BOARD,
    selected_fields         = [],
    highlighted_fields      = [],
    last_start_fields       = [],
    last_end_fields         = [],

    time_of_last_move       = time(),
    time_of_last_update     = time(),
    best_position           = None,
    score                   = 0,
    depth                   = 0,
    move_nr                 = 0,

    white_player_cpu        = True,
    black_player_cpu        = False,
    cpu_move_time_sec       = 2,

    history                 = [],
    next_moves              = generate_moves(START_BOARD),

    update_id               = randint(0, 10**10)
)

MP_WORKER = MPWorker()


def user_input(tile_selected=None) -> bool:
    is_legal_move         : bool      = tile_selected in APP.highlighted_fields

    piece                 : int       = APP.board.pieces[tile_selected]
    own_pieces            : list[int] = [0, 1, 2, 3, 4, 5] if APP.board.is_white else [6, 7, 8, 9, 10, 11]
    is_own_piece_selected : bool      = piece in own_pieces

    if is_legal_move:
        new_position = get_new_position(tile_selected)
        make_move(new_position)
        MP_WORKER.terminate_all_tasks()
        return True

    if is_own_piece_selected:
        select_piece(tile_selected)
        return True

    else:  # clicked on a non-active piece
        deselect_piece()
        return True


def game_checks() -> bool:
    if MP_WORKER.is_idle():
        MP_WORKER.add_task(APP.board, APP.depth + 1, APP.update_id)
        return False

    if result := MP_WORKER.get_next_result():
        update_app_data(result)
        return True

    return False

def deselect_piece():
    APP.selected_fields    = []
    APP.highlighted_fields = []


def select_piece(index):
    APP.selected_fields    = [index]
    APP.highlighted_fields = [end for start, end in APP.next_moves if start == index]


def get_new_position(index) -> Board:
    try:
        start, end = APP.selected_fields[0], index
    except IndexError:
        raise ValueError("trying to make move, but no piece selected")
    try:
        return APP.next_moves[(start, end)]
    except KeyError:
        raise ValueError("move selected was not in list of legal moves")


def make_move(board: Board):
    APP.update_id = randint(0, 10**10)

    APP.board                = board
    APP.selected_fields      = []
    APP.highlighted_fields   = []
    APP.last_start_fields    = []  # todo
    APP.last_end_fields      = []  # todo
    APP.score                = 0
    APP.depth                = 0
    APP.time_of_last_move    = time()
    APP.time_of_last_update  = time()
    APP.update_id            = randint(0, 10**10)
    APP.next_moves           = generate_moves(board)


def update_app_data(result: MPResult):
    if APP.update_id != result.update_id:  # result is irrelevant
        return

    APP.time_of_last_update = time()
    APP.best_position       =  Board(
        result.pieces,
        result.castles,
        result.en_passant,
        result.is_white
    )
    APP.score = result.score
    APP.depth = result.depth








