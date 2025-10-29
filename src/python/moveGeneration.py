from globals import *
import dataclasses
from UserInterface import show_in_new_ui



WP_ATTACKS    = [ (-1,  1), (-1, -1)                                                             ]
BP_ATTACKS    = [ ( 1,  1), ( 1, -1)                                                             ]
WP_PUSHES     = [ (-1,  0)                                                                       ]
BP_PUSHES     = [ ( 1,  0)                                                                       ]

ROOK_DELTAS   = [ ( 1,  0), (-1,  0), ( 0,  1), ( 0, -1)                                         ]
KNIGHT_DELTAS = [ ( 1,  2), ( 1, -2), (-1,  2), (-1, -2), ( 2,  1), ( 2, -1), (-2,  1), (-2, -1) ]
BISHOP_DELTAS = [ ( 1,  1), ( 1, -1), (-1,  1), (-1, -1)                                         ]
QUEEN_DELTAS  = ROOK_DELTAS + BISHOP_DELTAS
KING_DELTAS   = ROOK_DELTAS + BISHOP_DELTAS

PAWN_RANGE   = 1
ROOK_RANGE   = 7
KNIGHT_RANGE = 1
BISHOP_RANGE = 7
QUEEN_RANGE  = 7
KING_RANGE   = 1

PIECE_RANGES = [
    PAWN_RANGE, ROOK_RANGE, KNIGHT_RANGE, BISHOP_RANGE, QUEEN_RANGE, KING_RANGE,
    PAWN_RANGE, ROOK_RANGE, KNIGHT_RANGE, BISHOP_RANGE, QUEEN_RANGE, KING_RANGE
]

PIECE_DELTAS = [
    [], ROOK_DELTAS, KNIGHT_DELTAS, BISHOP_DELTAS, QUEEN_DELTAS, KING_DELTAS,
    [], ROOK_DELTAS, KNIGHT_DELTAS, BISHOP_DELTAS, QUEEN_DELTAS, KING_DELTAS,
]

def piece_moves(board: Board, position: int):
    piece: int = board.pieces[position]

    if piece == NO_PIECE:
        raise ValueError()

    if piece in [WP, BP]:
        return pawn_moves(
            board,
            WP_PUSHES  if board.is_white else BP_PUSHES,
            WP_ATTACKS if board.is_white else BP_ATTACKS,
            position,
        )

    return general_piece_moves(
        board,
        PIECE_DELTAS[piece],
        PIECE_RANGES[piece],
        position,
    )


def pawn_moves(board: Board, pushes: list[tuple], attacks: list[tuple], index: int) -> list[int]:
    own_pieces   =  WHITE_PIECES if board.is_white else BLACK_PIECES
    enemy_pieces =  BLACK_PIECES if board.is_white else WHITE_PIECES

    row, col = index // 8, index % 8
    result   = []

    start_rank: int = 6 if board.is_white    else 1
    push_range: int = 2 if row == start_rank else 1

    for delta_row, delta_col in pushes:

        for i in range(push_range):

            new_row: int = (row + delta_row * (i+1))
            new_col: int = (col + delta_col * (i+1))
            if new_row < 0 or new_row > 7 or new_col < 0 or new_col > 7:
                break

            target:       int = new_row * 8 + new_col
            target_piece: int = board.pieces[target]

            if target == board.en_passant:
                result.append(target)

            if target_piece == NO_PIECE:
                result.append(target)

            if target_piece in enemy_pieces:
                break

            if target_piece in own_pieces:
                break

    for delta_row, delta_col in attacks:

        for i in range(1):

            new_row: int = (row + delta_row * (i+1))
            new_col: int = (col + delta_col * (i+1))
            if new_row < 0 or new_row > 7 or new_col < 0 or new_col > 7:
                break

            target:       int = new_row * 8 + new_col
            target_piece: int = board.pieces[target]

            if target_piece == NO_PIECE:
                break

            if target_piece in enemy_pieces:
                result.append(target)
                break

            if target_piece in own_pieces:
                break

    return result


def general_piece_moves(board: Board, directions: list[tuple], max_range: int, index: int) -> list[int]:
    own_pieces   =  WHITE_PIECES if board.is_white else BLACK_PIECES
    enemy_pieces =  BLACK_PIECES if board.is_white else WHITE_PIECES

    row, col = index // 8, index % 8
    result = []

    for delta_row, delta_col in directions:

        for i in range(max_range):
            new_row: int = (row + (delta_row * (i+1)))
            new_col: int = (col + (delta_col * (i+1)))

            if new_row < 0 or new_row > 7 or new_col < 0 or new_col > 7:
                break

            target:       int = new_row * 8 + new_col
            target_piece: int = board.pieces[target]

            if target_piece == NO_PIECE:
                result.append(target)

            if target_piece in enemy_pieces:
                result.append(target)
                break

            if target_piece in own_pieces:
                break

    return result


def generate_moves(board: Board) -> tuple[list[Move], list[Board]]:
    own_pieces   =  WHITE_PIECES if board.is_white else BLACK_PIECES

    positions: list[Board] = []
    moves:     list[Move]  = []

    for start in range(64):
        start_piece: int = board.pieces[start]

        if start_piece not in own_pieces:
            continue

        for end in piece_moves(board, start):

            captured_piece: int = board.pieces[end]

            end_pieces = [start_piece]

            if start_piece == WP and end // 8 == 0:  # promotion
                end_pieces = [WR, WN, WB, WQ]

            if start_piece == BP and end // 8 == 7:  # promotion
                end_pieces = [WR, WN, WB, WQ]

            for end_piece in end_pieces:

                move: Move = Move(start, end, start_piece, end_piece, captured_piece, board.is_white)

                king:          int   = WK if board.is_white else BK
                king_position: int   = board.pieces.index(king)
                new_position:  Board = move_piece(board, move)

                if can_be_attacked(new_position, king_position): ... # invalid position
                    #continue

                positions.append(new_position)
                moves.append(move)

    return moves, positions


def move_piece(board: Board, move: Move) -> Board:
    new_position: Board = Board(
        board.pieces[:],
        board.castles[:],
        board.en_passant,
        board.is_white
    )

    new_position.pieces[move.start] = NO_PIECE
    new_position.pieces[move.end]   = move.end_piece

    if move.end == board.en_passant:  # remove pawn if en passant
        start_row = move.start // 8
        end_col   = move.end    & 8
        new_position.pieces[start_row * 8 + end_col] = NO_PIECE

    new_position.is_white = not board.is_white

    if board.is_white:  # revoke white castle rights
        if move.start_piece == WK:
            new_position.castles[WHITE_QUEENSIDE] = 0
            new_position.castles[WHITE_KINGSIDE ] = 0

        if (move.start_piece == WR and move.start == A1) or (move.captured_piece == WR and move.end == A1):
            new_position.castles[WHITE_QUEENSIDE] = 0

        if (move.start_piece == WR and move.start == H1) or (move.captured_piece == WR and move.end == H1):
            new_position.castles[WHITE_KINGSIDE] = 0

    else:   # revoke black castle rights
        if move.start_piece == BK:
            new_position.castles[0] = 0
            new_position.castles[1] = 0

        if (move.start_piece == BR and move.start == A8) or (move.captured_piece == BR and move.end == A8):
            new_position.castles[BLACK_QUEENSIDE] = 0

        if (move.start_piece == BR and move.start == H8) or (move.captured_piece == BR and move.end == H8):
            new_position.castles[BLACK_KINGSIDE] = 0

    new_position.en_passant = NO_MOVE # update en passant
    if (
            (move.start_piece == WP and move.start - move.end == 8) or
            (move.start_piece == WP and move.end - move.start == 8)):
        new_position.en_passant = max(move.start, move.end) - 8

    return new_position


def can_be_attacked(board: Board, pos: int) -> bool:
    own_pieces   =  WHITE_PIECES if board.is_white else BLACK_PIECES

    for start in range(64):
        start_piece: int = board.pieces[start]

        if start_piece == NO_PIECE:
            continue

        if start_piece in own_pieces:
            continue

        if start_piece in [WP, BP]:
            moves = pawn_moves(
                board,
                WP_PUSHES  if board.is_white else BP_PUSHES,
                WP_ATTACKS if board.is_white else BP_ATTACKS,
                start,
            )

        else:
            moves = general_piece_moves(
                board,
                PIECE_DELTAS[start_piece],
                PIECE_RANGES[start_piece],
                start,
            )

        for end in moves:

            if end == pos:
                return True

    return False


def get_castle(board: Board, castle_nr: int) -> Move | None:
    return None







