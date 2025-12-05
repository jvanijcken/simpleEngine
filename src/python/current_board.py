
from src.python.global_constants import *
from types import SimpleNamespace
from queue import Empty
from board_history import CURRENT, add_move

# ========== INTERFACE ========== #

def is_valid_move(start, end):
    for move in CURRENT.moves:
        if move.start == start and move.end == end:
            return True
    return False

def is_promotion(start, end):
    piece = CURRENT.board.pieces[start]
    if end in RANK1 and piece == BP:
        return True
    if end in RANK8 and piece == WP:
        return True
    return False

def make_move(start, end, end_piece=None):
    board = CURRENT.board
    if end_piece is None:
        end_piece = board.pieces[start]

    for move in CURRENT.moves:
        if move.start == start and move.end == end and move.end_piece == end_piece:
            add_move(move)
            break

def get_board():
    return CURRENT.board


def get_board_metadata():
    start = CURRENT.start_field
    end   = CURRENT.end_field
    return start, end


def is_piece_of_current_player(index):
    board = get_board()
    if board.is_white:
        return board.pieces[index] in WHITE_PIECES
    else:
        return board.pieces[index] in BLACK_PIECES


def get_movable_spaces(start):
    return [move.end for move in CURRENT.moves if move.start == start]



