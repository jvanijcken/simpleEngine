from globals import *
from app import APP, App, square_click, app_update, start_move_calculation
from dataclasses import dataclass

from pyglet.window import Window, mouse
from pyglet.graphics import Batch
from pyglet.app import run
from pyglet import shapes
from pyglet.gl import glClearColor
from pyglet.image import load, AbstractImage
from pyglet.sprite import Sprite
from pyglet.clock import schedule_interval
from pyglet.text import Label


# Configuration
rows = 8
cols = 8
square_size = 60
background_color = (0.1, 0.1, 0.1, 1.0)  # RGBA, 0-1 floats; dark gray

window = Window(8 * 60 + 200, 8 * 60 + 200, "Pyglet Grid Example", resizable=True)

# We'll keep a list of squares so we can reposition them
grid    = []
sprites = []
buttons = []
batch   = Batch()


def render_board(app: App):
    grid.clear()
    sprites.clear()
    buttons.clear()
    batch.invalidate()

    grid_width = cols * square_size
    grid_height = rows * square_size
    x_offset = (window.width - grid_width) / 2
    y_offset = (window.height - grid_height) / 2

    for row in range(rows):
        for col in range(cols):
            index = row * 8 + col

            x = x_offset + col * square_size
            y = y_offset + row * square_size

            is_dark_square: bool = (row + col) % 2 != 0

            color = (237, 136, 85) if is_dark_square else  (251, 227, 214)
            if index in app.highlighted_fields:
                color = (234, 119, 62) if is_dark_square else (243, 180, 149)

            if index in app.selected_fields + app.last_start_fields + app.last_end_fields and not APP.highlighted_fields:
                color = (242, 170, 132) if is_dark_square else (246, 198, 173)

            square = shapes.Rectangle(x, y, square_size, square_size, color=color, batch=batch)
            grid.append(square)

            piece: int = app.board.pieces[index]
            if piece == -1:
                continue

            # Add sprite in the center of the square
            image = get_chess_asset(piece)
            sprite = Sprite(
                image,
                x=x + square_size/2 - image.width/2,
                y=y + square_size/2 - image.height/2,
                batch=batch
            )
            sprites.append(sprite)

    button = shapes.Rectangle(
        x      = (window.width  - grid_width)  / 2,
        y      = (window.height - grid_height) / 2 - 50,
        width  = grid_width,
        height = 40,
        color  = (70, 130, 180),
        batch  = batch
    )
    buttons.append(button)




def get_chess_asset(piece_nr: int) -> AbstractImage:
    piece_dict = {
        0:  "Chess_plt60.png",
        1:  "Chess_rlt60.png",
        2:  "Chess_nlt60.png",
        3:  "Chess_blt60.png",
        4:  "Chess_qlt60.png",
        5:  "Chess_klt60.png",
        6:  "Chess_pdt60.png",
        7:  "Chess_rdt60.png",
        8:  "Chess_ndt60.png",
        9:  "Chess_bdt60.png",
        10: "Chess_qdt60.png",
        11: "Chess_kdt60.png",
    }
    return load(f"../../assets/{piece_dict[piece_nr]}")


def get_tile_from_click(x, y):
    # Compute offsets
    grid_width = cols * square_size
    grid_height = rows * square_size
    x_offset = (window.width - grid_width) / 2
    y_offset = (window.height - grid_height) / 2

    # Check if click is inside grid
    if x < x_offset or x > x_offset + grid_width:
        return None
    if y < y_offset or y > y_offset + grid_height:
        return None

    # Convert to column and row
    col = int((x - x_offset) // square_size)
    row = int((y - y_offset) // square_size)

    return row, col


@window.event
def on_mouse_press(x, y, button_, modifiers):
    tile = get_tile_from_click(x, y)
    if tile:
        row, col = tile
        index = row * 8 + col
        square_click(index)
        render_board(APP)

    if button_ != mouse.LEFT:
        return
    btn = buttons[0]
    if not (btn.x <= x <= btn.x + btn.width and btn.y <= y <= btn.y + btn.height):
        return

    start_move_calculation(4, 5)


@window.event
def on_draw():
    glClearColor(*background_color)
    window.clear()
    batch.draw()


@window.event
def on_resize(width, height):
    """Recreate the grid when window is resized."""
    render_board(APP)
    return None


def update_computer_move(dt):
    if app_update(0):
        render_board(APP)

if __name__ == "__main__":
    render_board(APP)
    schedule_interval(update_computer_move, 1/60)
    run()