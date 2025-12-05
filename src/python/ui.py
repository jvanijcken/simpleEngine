

if __name__ == "__main__":
    from pyglet.graphics import Batch
    from pyglet.gl import glClearColor
    from pyglet.clock import schedule_interval
    from pyglet.app import run
    from pyglet.window import Window
    from current_board import *
    from board_history import periodic_check
    from ui_board import *
    from ui_table import *
    from pyglet.gl import *

    SAND_COLOR = (255, 216, 139)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK = (20, 20, 20)

    background_color = (0.1, 0.1, 0.1, 1.0)  # RGBA, 0-1 floats; dark gray\

    window = Window(15 * 60 + 400, 8 * 60 + 200, "Pyglet Grid Example", resizable=True)
    _board_dims  = BoardDims()
    _board_widgets = BoardUi(Batch(), Batch())

    board_set_dims(_board_dims, x=0, y=0, tile_size=60)
    board_rebuild(_board_widgets)
    board_resize(_board_dims, _board_widgets)
    board_set_pieces(_board_dims, _board_widgets)

    _table_dims  = Dims()
    _table_widgets = Table(batch=Batch())
    table_set_dims(_table_dims, x_dim=4, y_dim=12, widths=[64] * 4, row_height=30, pad_x=1, x=_board_dims.width, y=0, width=window.width//2, height=_board_dims.height, resizer_width=20)
    table_set_text(_table_dims, _table_widgets, ["ABC" * 20] * 40)
    table_rebuild(_table_dims, _table_widgets)
    table_resize(_table_dims, _table_widgets)

    def in_square(sqr, x, y) -> bool:
        return sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        board_on_mouse_release(_board_dims, _board_widgets, x, y, button, modifiers)
        table_on_mouse_release(_table_dims, _table_widgets, x, y, button, modifiers)

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        board_on_mouse_press(_board_dims, _board_widgets, x, y, button, modifiers)
        table_on_mouse_press(_table_dims, _table_widgets, x, y, button, modifiers)

    @window.event
    def on_draw():
        glClearColor(*background_color)
        window.clear()

        draw_board_batch(_board_widgets)
        draw_table_batch(_table_dims, _table_widgets)


    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        board_on_mouse_drag(_board_dims, _board_widgets, x, y, dx, dy, buttons, modifiers)
        table_on_mouse_drag(_table_dims, _table_widgets, x, y, dx, dy, buttons, modifiers)

    @window.event
    def on_resize(width, height):
        board_set_dims(_board_dims)
        board_resize(_board_dims, _board_widgets)
        table_set_dims(_table_dims, x=_board_dims.width + 20, y=0, width=window.width//2)
        table_resize(_table_dims, _table_widgets)

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        table_on_mouse_motion(_table_dims, _table_widgets, x, y, dx, dy)

    schedule_interval(lambda dx: periodic_check(), 1/60)


    run()
