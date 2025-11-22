from move_generation import generate_moves
from global_constants import *
from dataclasses import dataclass
from random import randint
from board_analysis import Scheduler, MPWorker
from time import time, sleep
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
    """ holds all the state of the app, and is the only thing the app rendering is based on """
    board                   : Board

    # UI board info
    selected_fields         : list[int]
    highlighted_fields      : list[int]
    last_start_fields       : list[int]
    last_end_fields         : list[int]

    # analysis
    time_of_last_move       : float
    board_analysis          : dict[int, BoardAnalysis]
    move_nr                 : int

    # settings
    white_player_cpu        : bool
    black_player_cpu        : bool
    cpu_move_time_sec       : float

    # history
    index                   : int
    history                 : list[Board]
    next_moves              : dict[tuple[int, int], Board]

    # update tracking
    update_id               : int


APP = App(  # this is read by UI
    board                   = START_BOARD,
    selected_fields         = [],
    highlighted_fields      = [],
    last_start_fields       = [],
    last_end_fields         = [],

    time_of_last_move       = time(),
    board_analysis          = {},

    move_nr                 = 0,

    white_player_cpu        = False,
    black_player_cpu        = False,
    cpu_move_time_sec       = 2,

    index                   = 0,
    history                 = [START_BOARD],
    next_moves              = generate_moves(START_BOARD),

    update_id               = randint(0, 10**10)
)


schedule_eval = Scheduler()
schedule_move = Scheduler()
worker = MPWorker()

def user_input(tile_selected):
    """ interprets user inputs and handles corresponding app actions"""
    with APP_LOCK:
        if APP.board.is_white:
            if APP.white_player_cpu:
                return  # no player moves available because cpu makes the move
        else:
            if APP.black_player_cpu:
                return  # no player moves available because cpu makes the move

        is_legal_move         : bool      = tile_selected in APP.highlighted_fields

        piece                 : int       = APP.board.pieces[tile_selected]
        own_pieces            : list[int] = [0, 1, 2, 3, 4, 5] if APP.board.is_white else [6, 7, 8, 9, 10, 11]
        is_own_piece_selected : bool      = piece in own_pieces

        # make move
        if is_legal_move:
            start, end = APP.selected_fields[0], tile_selected
            new_position = APP.next_moves[(start, end)]
            worker.abort()
            make_move(new_position)

        # select my own piece
        elif is_own_piece_selected:
            APP.selected_fields    = [tile_selected]
            APP.highlighted_fields = [end for start, end in APP.next_moves if start == tile_selected]

        # clicked on a non-active piece
        else:
            APP.selected_fields    = []
            APP.highlighted_fields = []


def game_checks():
    """ should run frequently to initiate evaluation calculations and cpu moves """
    #try:
    #    schedule_move(cpu_move)
    #except ValueError as e:
    #    ...

    try:
        schedule_eval(calc)
    except ValueError as e:
        ...




def calc():
    """ goes through the process of calculating the evaluation of a certain position, should be run in a Scheduler """
    worker.initiate()
    depth = max(APP.board_analysis.keys()) + 1 if APP.board_analysis else 0
    result = worker.evaluate(APP.board, depth, APP.update_id)
    if result is None:
        return

    with APP_LOCK:
        result = {k: v for k, v in result.items() if v.update_id == APP.update_id}
        APP.board_analysis |= result


"""
def cpu_move():
    #makes sure the engine thinks for a certain amount of seconds before picking the best move
    start = time()
    update_id = APP.update_id + 0  # copy update_id ( +0 is important!)

    while True:
        sleep(1 / 120)

        # check if I can stop waiting
        if APP.board.is_white:
            if not APP.white_player_cpu:  # no active white CPU
                return
        else:
            if not APP.black_player_cpu:  # no active black CPU
                return

        if APP.update_id != update_id:  # new move made
            return

        with APP_LOCK:
            # calculation time is up
            if time() - start < APP.cpu_move_time_sec:
                continue
            if APP.depth[-1] < 5:
                print("no sufficient depth yet")
                continue

        worker.abort()  # signal mp_worker to stop calculating
        schedule_eval.wait_after_task_finished()  # wait on the other thread

        with APP_LOCK:  # prevent data from changing last moment
            if APP.update_id != update_id:  # check for last moment change
                print("move process expired")
                return

            if APP.best_position is None:  # check if there is some best position
                print("no best position found")
                return

            make_move(APP.best_position[-1])  # move
        break  # stop the loop
"""

def make_move(board: Board):
    """ handle all app changes associated with a new board """
    APP.board                = board
    APP.best_position        = [board]
    APP.selected_fields      = []
    APP.highlighted_fields   = []
    APP.last_start_fields    = []  # todo
    APP.last_end_fields      = []  # todo
    APP.board_analysis       = {}
    APP.time_of_last_move    = time()
    APP.update_id            = randint(0, 10**10)
    APP.next_moves           = generate_moves(board)
    APP.index                = APP.index + 1
    APP.history              = APP.history[:APP.index] + [board]


def is_prev_board_available():
    return APP.index > 0

def set_to_prev_board():
    with APP_LOCK:
        if not is_prev_board_available():
            return
        worker.abort()
        APP.index = APP.index - 1
        APP.board = APP.history[APP.index]

        APP.best_position        = [APP.board]
        APP.selected_fields      = []
        APP.highlighted_fields   = []
        APP.last_start_fields    = []  # todo
        APP.last_end_fields      = []  # todo
        APP.board_analysis       = {}
        APP.time_of_last_move    = time()
        APP.update_id            = randint(0, 10**10)
        APP.next_moves           = generate_moves(APP.board)


def is_next_board_available():
    return (APP.index + 1) < len(APP.history)

def set_to_next_board():
    with APP_LOCK:
        if not is_next_board_available():
            return
        worker.abort()
        APP.index = APP.index + 1
        APP.board = APP.history[APP.index]

        APP.best_position        = [APP.board]
        APP.selected_fields      = []
        APP.highlighted_fields   = []
        APP.last_start_fields    = []  # todo
        APP.last_end_fields      = []  # todo
        APP.board_analysis       = {}
        APP.time_of_last_move    = time()
        APP.update_id            = randint(0, 10**10)
        APP.next_moves           = generate_moves(APP.board)


