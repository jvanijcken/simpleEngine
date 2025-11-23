

if __name__ == "__main__":
    from pyglet.graphics import Batch
    from pyglet.gl import glClearColor
    from pyglet.clock import schedule_interval
    from pyglet.app import run
    from pyglet.window import Window
    from app import APP, game_checks, user_input, APP_LOCK, set_to_next_board, set_to_prev_board
    from render_functions import draw_board, draw_next_prev_buttons, draw_eval_table, draw_cache_info_box, draw_move_info

    SAND_COLOR = (255, 216, 139)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK = (20, 20, 20)

    # Configuration
    rows = 8
    cols = 8
    square_size = 60
    background_color = (0.1, 0.1, 0.1, 1.0)  # RGBA, 0-1 floats; dark gray\

    window = Window(15 * 60 + 200, 8 * 60 + 200, "Pyglet Grid Example", resizable=True)

    # We'll keep a list of squares so we can reposition them
    widgets = {}
    batch   = Batch()

    def render_board():
        with APP_LOCK:
            board_size = square_size * 8
            batch.invalidate()
            widgets.clear()

            widgets.__ior__(draw_board(
                x=20,
                y=window.height - board_size - 20,
                width=board_size, height=board_size, batch=batch,
                pieces=APP.board.pieces, selected_fields=APP.selected_fields, highlighted_fields=APP.highlighted_fields))

            widgets.__ior__(draw_next_prev_buttons(
                x=20,
                y=window.height - board_size - 40 - 20 - 20,
                width=board_size, height=40, batch=batch))

            widgets.__ior__(draw_cache_info_box(
                x=20,
                y = 20,
                width=board_size, height = window.height - board_size - 40 - 20 - 20 -20- 20,
                batch=batch, table=APP.board_analysis
            ))

            table = []
            for k in sorted(APP.board_analysis):
                table += [APP.board_analysis[k]]

            widgets.__ior__(draw_move_info(
                x=board_size + 2*20,
                y = 20,
                width=window.width - board_size - 3*20, height = window.height - 2*20,
                table=table,
                batch=batch
            ))


            #table = dict(
            #    depth=APP.depth, score=APP.score, time=[APP.time_of_last_move - x for x in APP.time_of_last_update],
            #    hits=APP.hits, misses=APP.misses, conflicts=APP.conflicts, writes=APP.writes)
            #widgets.__ior__(draw_eval_table(
            #    x=window.width/2 + ipad/2,
            #    y=window.height/2 - board_size/2,
            #    width=board_size, height=board_size, batch=batch, table=table))

    def in_square(sqr, x, y) -> bool:
        return sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        for i in range(64):
            if in_square(widgets["squares"][i], x, y):
                user_input(i)

        if in_square(widgets["buttons"]["next"], x, y):
            set_to_next_board()

        if in_square(widgets["buttons"]["prev"], x, y):
            set_to_prev_board()

    @window.event
    def on_draw():
        glClearColor(*background_color)
        window.clear()
        batch.draw()

    @window.event
    def on_resize(width, height):
        render_board()
        return None

    def interval(dt):
        game_checks()
        render_board()


    schedule_interval(interval, 1/60)
    run()
