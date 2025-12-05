

if __name__ == "__main__":
    """
    from pyglet.graphics import Batch
    from pyglet.gl import glClearColor
    from pyglet.clock import schedule_interval
    from pyglet.app import run
    from pyglet.window import Window
    from app import *
    from render_functions import draw_board, draw_next_prev_buttons, draw_cache_info_box, draw_move_info, draw_ranked_moves
    from ui_table import draw_table_batch, rebuild_table
    from pyglet.gl import *

    SAND_COLOR = (255, 216, 139)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK = (20, 20, 20)

    # Configuration
    rows = 8
    cols = 8
    square_size = 60
    background_color = (0.1, 0.1, 0.1, 1.0)  # RGBA, 0-1 floats; dark gray\

    window = Window(15 * 60 + 400, 8 * 60 + 200, "Pyglet Grid Example", resizable=True)
    table_batch = Batch()

    def render_board():
        board_size = square_size * 8

        rebuild_table(
            x=0, y=40, width=window.width//2, height=window.height//2,
            widths=[50] * 20, heights=[20] * 20, pad=5, batch=table_batch
        )




        #x = get_ui_info()
        #d = get_board_data()
        #widgets.__ior__(draw_board(
        #    x=20,
        #    y=window.height - board_size - 20,
        #    width=board_size, height=board_size, batch=batch,
        #    pieces=d.board.pieces, selected_fields=x.selected_fields, highlighted_fields=x.highlighted_fields,
        #    last_starts=d.start_fields, last_ends=d.end_fields, pending_promotions=x.pending_promotions
        #))
        #
        #widgets.__ior__(draw_next_prev_buttons(
        #    x=20 + 1,
        #    y=window.height - board_size - 60 + 1,
        #    width=board_size - 2, height=40 - 2, batch=batch
        #))
        #_min = [20] * 5
        #_min[2] = 40
        #_var = [20] * 5
        #_var[0] = 40
        #hdr = ["h"] * 5
        #bdy = ["b"] * 5 * 12
#
        #draw_table(0, 0, window.width, window.height, _min, _var, hdr, bdy, batch)

        #table = []
        #for k in sorted(APP.board_analysis):
        #    table += [APP.board_analysis[k]]
        #
        #widgets.__ior__(draw_move_info(
        #    x=board_size + 2*20,
        #    y = window.height - board_size - 3*20,
        #    width=720, height = board_size + 40,
        #    table=table,
        #    batch=batch
        #))
        #
        #    try:
        #        key = max(APP.board_analysis)
        #        seq = APP.board_analysis[key].moves
        #    except (KeyError, ValueError):
        #        seq = []
        #    widgets.__ior__(draw_ranked_moves(
        #        x=20,
        #        y = 20,
        #        width=board_size + 20 + 722, height =window.height - board_size - 100,
        #        batch=batch, moves=seq
        #    ))
        #
        #
        #    #table = dict(
        #    #    depth=APP.depth, score=APP.score, time=[APP.time_of_last_move - x for x in APP.time_of_last_update],
        #    #    hits=APP.hits, misses=APP.misses, conflicts=APP.conflicts, writes=APP.writes)
        #    #widgets.__ior__(draw_eval_table(
        #    #    x=window.width/2 + ipad/2,
        #    #    y=window.height/2 - board_size/2,
        #    #    width=board_size, height=board_size, batch=batch, table=table))

    def in_square(sqr, x, y) -> bool:
        return sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height

    @window.event
    def on_mouse_press(x, y, button, modifiers): ...
        #for i in range(64):
        #    if in_square(widgets["squares"][i], x, y):
        #        user_tile_click(i)
        #
        #if in_square(widgets["buttons"]["next"], x, y):
        #    set_next()
        #
        #if in_square(widgets["buttons"]["prev"], x, y):
        #    set_prev()

    @window.event
    def on_draw():
        glClearColor(*background_color)
        window.clear()
        draw_table_batch()



    @window.event
    def on_resize(width, height):
        render_board()
        return None

    def interval(dt):
        periodic_check()
        render_board()


    schedule_interval(interval, 1/60)
    run()
    """