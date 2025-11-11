from queue import Empty
from moveGeneration import generate_moves
from globals import *
from dataclasses import dataclass
from random import randint
from multiprocessing import Queue, Process, Event
from MPworkers import Scheduler, MPWorker
from time import time
from threading import Lock


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

APP_LOCK = Lock()

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

    def __setattr__(self, key, value):
        with APP_LOCK:
            object.__setattr__(self, key, value)

    def __getattribute__(self, item):
        with APP_LOCK:
            return object.__getattribute__(self, item)



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


schedule = Scheduler()
worker = MPWorker()

def user_input(tile_selected):
    is_legal_move         : bool      = tile_selected in APP.highlighted_fields

    piece                 : int       = APP.board.pieces[tile_selected]
    own_pieces            : list[int] = [0, 1, 2, 3, 4, 5] if APP.board.is_white else [6, 7, 8, 9, 10, 11]
    is_own_piece_selected : bool      = piece in own_pieces

    if is_legal_move:
        start, end = APP.selected_fields[0], tile_selected
        new_position = APP.next_moves[(start, end)]
        worker.abort()
        make_move(new_position)


    elif is_own_piece_selected:
        APP.selected_fields    = [tile_selected]
        APP.highlighted_fields = [end for start, end in APP.next_moves if start == tile_selected]

    else:  # clicked on a non-active piece
        APP.selected_fields    = []
        APP.highlighted_fields = []


def game_checks():
    try:
        schedule(calc)
        print("SUCC")
    except ValueError:
        print("BUSS")


def calc():
    worker.initiate()
    d = APP.depth + 0
    print(f"scheduling with depth {d}")
    result = worker.evaluate(APP.board, APP.depth + 1, APP.update_id)
    print(f"finished with depth {d}")

    if APP.update_id != result.update_id:
        return

    APP.best_position       = result.board
    APP.score               = result.score
    APP.depth               = result.depth
    APP.time_of_last_update = time()


def make_move(board: Board):
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









