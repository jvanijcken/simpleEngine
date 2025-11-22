from global_constants import *


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


MOVE_TABLE = [
    (lambda board, index: pawn_moves(         board, WP_PUSHES,     WP_ATTACKS,   index, is_white=True)),
    (lambda board, index: general_piece_moves(board, ROOK_DELTAS,   ROOK_RANGE,   index, is_white=True)),
    (lambda board, index: general_piece_moves(board, KNIGHT_DELTAS, KNIGHT_RANGE, index, is_white=True)),
    (lambda board, index: general_piece_moves(board, BISHOP_DELTAS, BISHOP_RANGE, index, is_white=True)),
    (lambda board, index: general_piece_moves(board, QUEEN_DELTAS,  QUEEN_RANGE,  index, is_white=True)),
    (lambda board, index: general_piece_moves(board, KING_DELTAS,   KING_RANGE,   index, is_white=True)),
    (lambda board, index: pawn_moves(         board, BP_PUSHES,     BP_ATTACKS,   index, is_white=False)),
    (lambda board, index: general_piece_moves(board, ROOK_DELTAS,   ROOK_RANGE,   index, is_white=False)),
    (lambda board, index: general_piece_moves(board, KNIGHT_DELTAS, KNIGHT_RANGE, index, is_white=False)),
    (lambda board, index: general_piece_moves(board, BISHOP_DELTAS, BISHOP_RANGE, index, is_white=False)),
    (lambda board, index: general_piece_moves(board, QUEEN_DELTAS,  QUEEN_RANGE,  index, is_white=False)),
    (lambda board, index: general_piece_moves(board, KING_DELTAS,   KING_RANGE,   index, is_white=False)),
]


def pawn_moves(board: Board, pushes: list[tuple], attacks: list[tuple], index: int, is_white: bool) -> list[int]:
    own_pieces   =  WHITE_PIECES if is_white else BLACK_PIECES
    enemy_pieces =  BLACK_PIECES if is_white else WHITE_PIECES

    row, col = index // 8, index % 8
    result   = []

    start_rank: int = 6 if is_white          else 1
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
            if target_piece in enemy_pieces or target == board.en_passant:
                result.append(target)
                break
            if target_piece in own_pieces:
                break
    return result


def general_piece_moves(board: Board, directions: list[tuple], max_range: int, index: int, is_white: bool) -> list[int]:
    own_pieces   =  WHITE_PIECES if is_white else BLACK_PIECES
    enemy_pieces =  BLACK_PIECES if is_white else WHITE_PIECES

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


def generate_moves(board: Board) -> dict[tuple[int, int], Board]:
    own_pieces   =  WHITE_PIECES if board.is_white else BLACK_PIECES

    result: dict[tuple[int, int], Board] = {}

    for start in range(64):
        start_piece: int = board.pieces[start]

        if start_piece not in own_pieces:
            continue

        for end in MOVE_TABLE[start_piece](board, start):
            captured_piece: int = board.pieces[end]

            if start_piece == WP and end // 8 == 0:  # promotion
                end_pieces = [WR, WN, WB, WQ]
            elif start_piece == BP and end // 8 == 7:  # promotion
                end_pieces = [WR, WN, WB, WQ]
            else:
                end_pieces = [start_piece]

            for end_piece in end_pieces:
                move: Move = Move(start, end, start_piece, end_piece, captured_piece, board.is_white)

                new_position:  Board = move_piece(board, move)
                king:          int   = WK if board.is_white else BK
                king_position: int   = new_position.pieces.index(king)

                if can_be_attacked(new_position, king_position, board.is_white): # invalid position
                    continue

                result[(start, end)] = new_position

    if board.is_white:
        result |= white_kingside_castle(board)
        result |= white_queenside_castle(board)
    else:
        result |= black_kingside_castle(board)
        result |= black_queenside_castle(board)
    return result


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
        end_col   = move.end    % 8
        new_position.pieces[start_row * 8 + end_col] = NO_PIECE

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
            (move.start_piece == WP and abs(move.end - move.start) == 16) or
            (move.start_piece == BP and abs(move.end - move.start) == 16)):
        new_position.en_passant = max(move.start, move.end) - 8

    new_position.is_white = not board.is_white

    return new_position


def can_be_attacked(board: Board, position: int, is_white: bool) -> bool:
    defenders = range(0,  6) if is_white else range(6, 12)
    attackers = range(6, 12) if is_white else range(0,  6)

    for defender, attacker in zip(defenders, attackers):
        moves = MOVE_TABLE[defender](board, position)  # from this position, what moves can my own pieces make?
        for move in moves:
            if board.pieces[move] == attacker:  # if there is an enemy piece of the same type, it means it can get to the position too
                return True
    return False


def black_kingside_castle(board: Board):
    if board.castles[BLACK_KINGSIDE] == 0:
        return {}
    for tile in [F8, G8]:
        if board.pieces[tile] != NO_PIECE:
            return {}
    for tile in [E8, F8, G8]:
        if can_be_attacked(board, tile, is_white=False):
            return {}

    board = move_piece(board, Move(E8, G8, BK, BK, NO_PIECE, False, BLACK_KINGSIDE))
    board.is_white = False
    board = move_piece(board, Move(H8, F8, BR, BR, NO_PIECE, False, BLACK_KINGSIDE))
    return {(E8, G8) : board}


def black_queenside_castle(board: Board):
    if board.castles[BLACK_QUEENSIDE] == 0:
        return {}
    for tile in [D8, C8, B8]:
        if board.pieces[tile] != NO_PIECE:
            return {}
    for tile in [E8, D8, C8]:
        if can_be_attacked(board, tile, is_white=False):
            return {}

    board = move_piece(board, Move(E8, C8, BK, BK, NO_PIECE, False, BLACK_QUEENSIDE))
    board.is_white = False
    board = move_piece(board, Move(A8, D8, BR, BR, NO_PIECE, False, BLACK_QUEENSIDE))
    return {(E8, C8) : board}


def white_kingside_castle(board: Board):
    if board.castles[WHITE_KINGSIDE] == 0:
        return {}
    for tile in [F1, G1]:
        if board.pieces[tile] != NO_PIECE:
            return {}
    for tile in [E1, F1, G1]:
        if can_be_attacked(board, tile, is_white=True):
            return {}

    board = move_piece(board, Move(E1, G1, WK, WK, NO_PIECE, True, WHITE_KINGSIDE))
    board.is_white = True
    board = move_piece(board, Move(H1, F1, WR, WR, NO_PIECE, True, WHITE_KINGSIDE))
    return {(E1, G1) : board}


def white_queenside_castle(board: Board):
    if board.castles[WHITE_QUEENSIDE] == 0:
        return {}
    for tile in [D1, C1, B1]:
        if board.pieces[tile] != NO_PIECE:
            return {}
    for tile in [E1, D1, C1]:
        if can_be_attacked(board, tile, is_white=True):
            return {}

    board = move_piece(board, Move(E1, C1, WK, WK, NO_PIECE, True, WHITE_KINGSIDE))
    board.is_white = True
    board = move_piece(board, Move(A1, D1, WR, WR, NO_PIECE, True, WHITE_KINGSIDE))
    return {(E1, C1) : board}






