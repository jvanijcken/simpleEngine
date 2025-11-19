

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
    from app import APP, game_checks, user_input, APP_LOCK, is_next_board_available, is_prev_board_available, set_to_next_board, set_to_prev_board
    from time import time

    SAND_COLOR = (255, 216, 139)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Configuration
    rows = 8
    cols = 8
    square_size = 60
    background_color = (0.1, 0.1, 0.1, 1.0)  # RGBA, 0-1 floats; dark gray\

    CYCLE_NR = 0

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
            x = (window.width  - square_size * 8 * 2) / 2,
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
            x      = board.x,
            y      = board.y - 40 - 20,
            width  = (board.width - 20) / 2,
            height = 40,
            color  = SAND_COLOR if is_prev_board_available() else BLACK,
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
            x      = board.x + (board.width + 20) / 2,
            y      = board.y - 40 - 20,
            width  = (board.width - 20) / 2,
            height = 40,
            color  = SAND_COLOR if is_next_board_available() else BLACK,
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
            x      = board.x + board.width + 20,
            y      = board.y,
            width  = board.width,
            height = board.height,
            color  = SAND_COLOR,
            batch  = batch
        )
        buttons["eval_bar"] = eval_bar
        bar = ['|', '/', '—', '\\'][CYCLE_NR // 3 % 4]

        labels["eval_label"] = {}
        text = ''
        for i in range(len(APP.depth)):
            text = f"depth \t {APP.depth[i]:2} > {APP.score[i]:4} in {APP.time_of_last_update[i] - APP.time_of_last_move:.2f} s"
            eval_label = Label(
                text      = text,
                font_name = 'consolas',
                font_size = 20,
                x         = eval_bar.x + 20,
                y         = eval_bar.y + eval_bar.height - 20 - (i * 60),
                anchor_x  = 'left',
                anchor_y  = 'center',
                color     = BLACK,
                batch     = batch
            )
            labels["eval_label"][i] = eval_label
        for i in range(len(APP.depth)):
            text =  f" {APP.hits[i]:6} H {APP.misses[i]:6} M {APP.conflicts[i]:6} C {APP.writes[i]:6} W"
            eval_label = Label(
                text      = text,
                font_name = 'consolas',
                font_size = 20,
                x         = eval_bar.x + 20,
                y         = eval_bar.y + eval_bar.height - 20 - 30 - (i * 60),
                anchor_x  = 'left',
                anchor_y  = 'center',
                color     = BLACK,
                batch     = batch
            )
            labels["eval_label"][i * 20] = eval_label


    @window.event
    def on_mouse_press(x, y, button_, modifiers):
        index = None
        for i, sqr in enumerate(grid):
            if sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height:
                index = i

        if index is not None:
            user_input(index)

        sqr = buttons["next_button"]
        if sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height:
            set_to_next_board()

        sqr = buttons["prev_button"]
        if sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height:
            set_to_prev_board()


    @window.event
    def on_draw():
        glClearColor(*background_color)
        window.clear()
        batch.draw()


    @window.event
    def on_resize(width, height):
        with APP_LOCK:
            render_board()
        return None

    def interval(dt):
        global CYCLE_NR
        game_checks()
        with APP_LOCK:
            render_board()
        CYCLE_NR += 1


    schedule_interval(interval, 1/60)
    run()
