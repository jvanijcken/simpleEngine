

if __name__ == "__main__":
    from pyglet.graphics import Batch
    from pyglet import shapes
    from pyglet.gl import glClearColor
    from pyglet.image import load
    from pyglet.sprite import Sprite
    from pyglet.text import Label
    from pyglet.clock import schedule_interval
    from pyglet.app import run
    from pyglet.window import Window
    from app import APP, game_checks, user_input

    SAND_COLOR = (255, 216, 139)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Configuration
    rows = 8
    cols = 8
    square_size = 60
    background_color = (0.1, 0.1, 0.1, 1.0)  # RGBA, 0-1 floats; dark gray

    window = Window(8 * 60 + 200, 8 * 60 + 200, "Pyglet Grid Example", resizable=True)

    # We'll keep a list of squares so we can reposition them
    grid    = []
    sprites = []
    garbage = []
    buttons = {}
    labels  = {}
    batch   = Batch()


    piece_dict = {
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
    }


    def render_board():
        grid.clear()
        sprites.clear()
        buttons.clear()
        garbage.clear()
        batch.invalidate()

        board = shapes.Rectangle(
            x = (window.width  - square_size * 8) / 2,
            y = (window.height - square_size * 8) / 2,
            height=square_size * 8,
            width=square_size * 8,
            color = (0, 0, 0),
            batch=batch
        )

        # grid and chess pieces
        for row in range(rows):
            for col in range(cols):

                # tiles
                index = row * 8 + col
                is_dark_square: bool = (row + col) % 2 != 0

                tile_color_dark           = (237, 136,  85)
                tile_color_light          = (251, 227, 214)
                color = tile_color_dark if is_dark_square else tile_color_light

                square = shapes.Rectangle(
                    x      = board.x + square_size * col,
                    y      = board.y + square_size * (7 - row),
                    width  = square_size,
                    height = square_size,
                    color  = color,
                    batch  = batch)
                grid.append(square)

                if index in APP.highlighted_fields:
                    highlight_circle = shapes.Circle(
                        x      = square.x + square_size/2,
                        y      = square.y + square_size/2,
                        radius = square_size/3,
                        color  = (174, 174, 174),     # RGB color (red)
                        batch  = batch
                    )
                    highlight_circle.opacity = 128  # 50% transparent
                    garbage.append(highlight_circle)

                if index in APP.selected_fields + APP.last_start_fields + APP.last_end_fields:
                    highlight_square = shapes.Rectangle(
                        x      = board.x + square_size * col,
                        y      = board.y + square_size * (7 - row),
                        width  = square_size,
                        height = square_size,
                        color  = (174, 174, 174),
                        batch  = batch)
                    highlight_square.opacity = 128  # 50% transparent
                    garbage.append(highlight_square)

                # chess piece images
                piece: int = APP.board.pieces[index]
                if piece == -1:
                    continue
                image = piece_dict[piece]
                sprite = Sprite(
                    image,
                    x=square.x + square_size/2 - image.width/2,
                    y=square.y + square_size/2 - image.height/2,
                    batch=batch
                )
                sprites.append(sprite)

        prev_button = shapes.Rectangle(
            x      = board.x + (board.width + 20) / 2,
            y      = board.y - 40 - 20,
            width  = (board.width - 20) / 2,
            height = 40,
            color  = SAND_COLOR,
            batch  = batch
        )
        buttons["prev_button"] = prev_button
        prev_label = Label(
            text      = "Prev",
            font_name = 'consolas',
            font_size = 20,
            x         = prev_button.x + prev_button.width  / 2,
            y         = prev_button.y + prev_button.height / 2,
            anchor_x  = 'center',
            anchor_y  = 'center',
            color     = BLACK,
            batch     = batch
        )
        labels["prev_label"] = prev_label


        next_button = shapes.Rectangle(
            x      = board.x,
            y      = board.y - 40 - 20,
            width  = (board.width - 20) / 2,
            height = 40,
            color  = SAND_COLOR,
            batch  = batch
        )
        buttons["next_button"] = next_button
        next_label = Label(
            text      = "Next",
            font_name = 'consolas',
            font_size = 20,
            x         = next_button.x + next_button.width  / 2,
            y         = next_button.y + next_button.height / 2,
            anchor_x  = 'center',
            anchor_y  = 'center',
            color     = BLACK,
            batch     = batch
        )
        labels["eval_bar"] = next_label

        eval_bar = shapes.Rectangle(
            x      = board.x,
            y      = board.y + board.height + 20,
            width  = board.width,
            height = 40,
            color  = SAND_COLOR,
            batch  = batch
        )
        buttons["eval_bar"] = eval_bar
        eval_label = Label(
            text      = f"depth {APP.depth} → {APP.score} in {APP.time_of_last_update - APP.time_of_last_move:.2f} s",
            font_name = 'consolas',
            font_size = 20,
            x         = eval_bar.x + eval_bar.width  / 2,
            y         = eval_bar.y + eval_bar.height / 2,
            anchor_x  = 'center',
            anchor_y  = 'center',
            color     = BLACK,
            batch     = batch
        )
        labels["eval_label"] = eval_label


    @window.event
    def on_mouse_press(x, y, button_, modifiers):
        index = None
        for i, sqr in enumerate(grid):
            if sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height:
                index = i

        if index is not None and user_input(index):
            render_board()


    @window.event
    def on_draw():
        glClearColor(*background_color)
        window.clear()
        batch.draw()


    @window.event
    def on_resize(width, height):
        render_board()
        return None

    game_checks()
    render_board()

    def cmd(dt):
        if game_checks():
            render_board()

    schedule_interval(cmd, 1/60)
    run()
