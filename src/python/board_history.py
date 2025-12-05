
from src.python.global_constants import *
import time
from queue import Queue, Empty
from global_constants import START_BOARD
from PyChess import get_moves
from dataclasses import dataclass, field
from move_stuff import build_move, Move
from board_analysis import evaluate, stop_background_eval_calculation


@dataclass
class BoardContext:
    index       : int   = 0
    start_fields: list  = field(default_factory=lambda: [None])
    end_fields  : list  = field(default_factory=lambda: [None])
    boards      : list  = field(default_factory=lambda: [START_BOARD])
    move_times  : list  = field(default_factory=lambda: [time.time()])
    evals       : list  = field(default_factory=lambda: [[]])
    moves       : list  = field(default_factory=lambda: [get_possible_moves(START_BOARD)])
    result_queue: Queue = Queue()


@dataclass
class CurrentBoard:
    history: BoardContext

    @property
    def start_field(self):  return self.history.start_fields[self.history.index]

    @property
    def end_field(self):    return self.history.end_fields[self.history.index]

    @property
    def board(self):        return self.history.boards[self.history.index]

    @property
    def move_time(self):    return self.history.move_times[self.history.index]

    @property
    def eval(self):         return self.history.evals[self.history.index]

    @property
    def moves(self):        return self.history.moves[self.history.index]

    @property
    def result_queue(self): return self.history.result_queue


def get_possible_moves(start_board: Board):
    board_tuples, starts, ends = get_moves(start_board.pieces, start_board.castles, start_board.en_passant, start_board.is_white)

    nr_of_moves = len(board_tuples)
    boards = [Board(*board_tuples[i]) for i in range(nr_of_moves)]
    moves  = [build_move(starts[i], ends[i], start_board, boards[i], 0) for i in range(nr_of_moves)]
    return moves


def add_move(move: Move):
    """ properly updates all historic data and updates the current board data """
    c = HISTORY
    def add(arr, el):
        return arr[:c.index] + [el]  # if we make a new move, we delete the stored sequence that would come after that

    stop_background_eval_calculation()

    c.index       += 1
    c.boards       = add(c.boards, move.board)
    c.start_fields = add(c.start_fields, move.start)
    c.end_fields   = add(c.end_fields,   move.end)
    c.move_times   = add(c.move_times, time.time())
    c.moves        = add(c.moves, get_possible_moves(move.board))
    c.result_queue = Queue()  # ensures old eval results will be ignored
    c.evals        = add(c.evals, [])



# ========== INTERFACE =========== #
def prev_possible() -> bool:
    """ used to check if we can decrement the board index """
    return HISTORY.index > 0

def next_possible() -> bool:
    """ used to check if we can increment the board index """
    return (HISTORY.index + 1) < len(HISTORY.boards)

def set_prev():
    """ sets current board to the next move if possible """
    if prev_possible():
        HISTORY.index -= 1

def set_next():
    """ sets current board to the previous move is possible """
    if next_possible():
        HISTORY.index += 1


def periodic_check():
    """ this checks first if eval calculations are ready and initiates new eval calculations if needed """
    # this function is the only one that has access to the worker and its scheduler

    # ↓ we need to check this first, otherwise we will possibly initiate an eval calculation with the old depth
    # ↓ so that means running the same calculation again,
    try:
        result = CURRENT.result_queue.get_nowait()
        CURRENT.eval.append(result)  # note: this will also get updated on board_context
    except Empty:
        pass

    evaluate(CURRENT.result_queue, CURRENT.board, len(CURRENT.eval) + 1)


HISTORY = BoardContext()
CURRENT = CurrentBoard(HISTORY)


