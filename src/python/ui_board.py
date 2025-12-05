from pyglet.image import load, SolidColorImagePattern
from pyglet import sprite
from pyglet import shapes
from dataclasses import dataclass, field
from pyglet.graphics import Batch
from current_board import is_promotion, is_valid_move, make_move, get_board, get_movable_spaces, is_piece_of_current_player, get_board_metadata

blank = SolidColorImagePattern((0, 0, 0, 0)).create_image(1, 1)

_piece_dict = {
    0:  load(f"../../assets/Chess_plt60.png"),
    1:  load(f"../../assets/Chess_rlt60.png"),
    2:  load(f"../../assets/Chess_nlt60.png"),
    3:  load(f"../../assets/Chess_blt60.png"),
    4:  load(f"../../assets/Chess_qlt60.png"),
    5:  load(f"../../assets/Chess_klt60.png"),
    6:  load(f"../../assets/Chess_pdt60.png"),
    7:  load(f"../../assets/Chess_rdt60.png"),
    8:  load(f"../../assets/Chess_ndt60.png"),
    9:  load(f"../../assets/Chess_bdt60.png"),
    10: load(f"../../assets/Chess_qdt60.png"),
    11: load(f"../../assets/Chess_kdt60.png"),
    -1: blank
}

tile_color_dark           = (237, 136,  85)
tile_color_light          = (251, 227, 214)

@dataclass
class BoardUi:
    batch: Batch
    batch_top_level: Batch

    boxes      : list = field(default_factory=list)
    sprites    : list = field(default_factory=list)
    row_labels : list = field(default_factory=list)
    col_labels : list = field(default_factory=list)

    selected_tile:  tuple[int, shapes.Rectangle] | tuple = ()
    tile_shadow:    tuple[int, shapes.Rectangle] | tuple = ()
    dragging_piece: tuple[int, sprite.Sprite]    | tuple = ()

    last_start:     tuple[int, shapes.Rectangle] | tuple = ()
    last_end:       tuple[int, shapes.Rectangle] | tuple = ()

    legal_moves:    list = field(default_factory=list)



@dataclass
class BoardDims:
    x         : int = 0
    y         : int = 0
    width     : int = 0
    height    : int = 0
    tile_size : int = 0



def board_set_dims(dims: BoardDims, x=None, y=None, width=None, height=None, tile_size=None):
    if x is not None:
        dims.x = x
    if y is not None:
        dims.y = y
    if width is not None:
        dims.width = (width // 8) * 8
        dims.height = dims.width
        dims.tile_size = dims.width // 8
    if height is not None:
        dims.height = (height // 8) * 8
        dims.width = dims.height
        dims.tile_size = dims.height // 8
    if tile_size is not None:
        dims.tile_size = tile_size
        dims.height = tile_size * 8
        dims.width = tile_size * 8


# = remaking =
def redraw_board(board: BoardUi):
    board.boxes.clear()
    for i in range(8*8):
        row, col = i // 8, i % 8
        color = tile_color_dark if (row + col) % 2 != 0 else tile_color_light
        box = shapes.Rectangle(0, 0, 0, 0, color=color, batch=board.batch)
        board.boxes.append(box)


def redraw_sprites(board: BoardUi):
    board.sprites.clear()
    for i in range(8*8):
        spr = sprite.Sprite(blank, x=0, y=0, batch=board.batch)
        board.sprites.append(spr)


def board_rebuild(board: BoardUi):
    redraw_board(board)
    redraw_sprites(board)


def board_resize(dims: BoardDims, board: BoardUi):
    resize_board(dims, board)
    resize_sprites(dims, board)


# = resizing =
def resize_board(dims: BoardDims, board: BoardUi):
    for i in range(8*8):
        box = board.boxes[i]
        row, col = i // 8, i % 8
        box.x = dims.x + col * dims.tile_size
        box.y = dims.y + dims.height - row * dims.tile_size - dims.tile_size
        box.width  = dims.tile_size
        box.height = dims.tile_size


def resize_sprites(dims: BoardDims, board: BoardUi):
    for i in range(8*8):
        box = board.boxes[i]
        spr = board.sprites[i]
        spr.x = box.x
        spr.y = box.y


# == repositioning pieces
def board_set_pieces(dims: BoardDims, board: BoardUi):
    pieces = get_board().pieces
    meta = get_board_metadata()
    last_start, last_end = meta

    for i in range(8*8):
        piece = pieces[i]
        image = _piece_dict[piece]
        spr = board.sprites[i]
        spr.image = image
    board.last_start = ()
    board.last_end   = ()

    if last_start is not None:
        tile = board.boxes[last_start]
        box = shapes.Rectangle(tile.x, tile.y, tile.width, tile.height, color=(174, 174, 174), batch=board.batch)
        box.opacity = 128
        board.last_start = last_start, box

    if last_end is not None:
        tile = board.boxes[last_end]
        box = shapes.Rectangle(tile.x, tile.y, tile.width, tile.height, color=(174, 174, 174), batch=board.batch)
        box.opacity = 128
        board.last_end = last_end, box


# == internal logic == #
def select_piece(dims: BoardDims, board: BoardUi, index):
    tile = board.boxes[index]
    board.selected_tile = (index, tile)
    shadow = shapes.Rectangle(tile.x, tile.y, tile.width, tile.height, color=(174, 174, 174), batch=board.batch)
    shadow.opacity = 128
    board.tile_shadow = (index, shadow)
    board.legal_moves.clear()
    for end in get_movable_spaces(index):
        end_tile = board.boxes[end]
        space = shapes.Circle(end_tile.x + dims.tile_size// 2, end_tile.y + dims.tile_size// 2, dims.tile_size//3, color=(174, 174, 174), batch=board.batch)
        space.opacity = 128
        board.legal_moves.append(space)


def deselect_piece(board: BoardUi):
    board.selected_tile = ()  # deselect
    board.tile_shadow = ()
    board.legal_moves.clear()


# = move_piece =
def board_on_mouse_press(dims: BoardDims, board: BoardUi, x, y, button, modifiers):
    # Handle move selection
    if board.selected_tile:
        i_s, tile = board.selected_tile
        for i_e in range(8*8):
            box = board.boxes[i_e]
            if not in_square(box, x, y):
                continue
            if not is_valid_move(i_s, i_e):
                deselect_piece(board)
                break
            attempt_move(dims, board, i_s, i_e)
            break

    # Handle square selection
    deselect_piece(board)
    for i in range(8*8):
        tile = board.boxes[i]
        if not in_square(tile, x, y):
            continue
        if not is_piece_of_current_player(i):
            break
        select_piece(dims, board, i)
        break


def board_on_mouse_drag(dims: BoardDims, board: BoardUi, x, y, dx, dy, buttons, modifiers):
    # Handle piece dragging
    if board.selected_tile:

        if not board.dragging_piece:
            i, tile = board.selected_tile
            spr = board.sprites[i]
            drag_image = spr.image
            spr.image = blank

            drag_spr = sprite.Sprite(drag_image, x, y, batch=board.batch_top_level)
            board.dragging_piece = (i, drag_spr)

        i , draw_spr = board.dragging_piece
        draw_spr.x = x - dims.tile_size // 2
        draw_spr.y = y - dims.tile_size // 2


def board_on_mouse_release(dims: BoardDims, board: BoardUi, x, y, _button, _modifiers):
    # Handle tile deselection
    if not board.dragging_piece:
        return

    # Handle piece dragging
    i_s, spr = board.dragging_piece
    source = board.sprites[i_s]
    source.image = spr.image

    for i_e in range(8*8):
        box = board.boxes[i_e]

        if not in_square(box, x, y):
            continue

        if not is_valid_move(i_s, i_e):
            start_spr = board.sprites[i_s]
            start_spr.image = spr.image
            spr.image = blank
            deselect_piece(board)
            break

        attempt_move(dims, board, i_s, i_e)
        break

    spr.image = blank
    board.dragging_piece = ()


def attempt_move(dims: BoardDims, board: BoardUi, start, end):
    if is_promotion(start, end):
        ...  # show whole promotion menu  # todo
    else:
        make_move(start, end)
        board_set_pieces(dims, board)
        draw_board_batch(board)

        deselect_piece(board)


def draw_board_batch(board: BoardUi):
    board.batch.draw()
    board.batch_top_level.draw()


def in_square(sqr, x, y) -> bool:
    return sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height
