from pyglet import shapes
from pyglet.image import load
from pyglet import sprite
from pyglet import text
from app import is_next_board_available, is_prev_board_available, set_to_next_board, set_to_prev_board
from global_constants import BoardAnalysis


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
}
_widgets = {}

def draw_board(x, y, width, height, batch, pieces, selected_fields, highlighted_fields):
    widgets = dict(squares={}, highlight={}, selected={}, pieces={})

    tile_color_dark           = (237, 136,  85)
    tile_color_light          = (251, 227, 214)

    for i in range(64):
        _x = x + square_size * (i % 8)
        _y = y + square_size * (7 - (i // 8))

        is_dark_square: bool = ((i // 8) + (i % 8)) % 2 != 0
        color = tile_color_dark if is_dark_square else tile_color_light

        widgets["squares"][i] = shapes.Rectangle(
            x=_x,
            y=_y,
            width=square_size, height=square_size, color=color, batch=batch)

        is_highlighted: bool = i in highlighted_fields
        if is_highlighted:
            widgets["highlight"][i] = shapes.Circle(
                x=_x + square_size/2,
                y=_y + square_size/2,
                radius = square_size/3, color=(174, 174, 174), batch=batch)
            widgets["highlight"][i].opacity = 128  # 50% transparent

        is_selected: bool = i in selected_fields
        if is_selected:
            widgets["selected"][i] = shapes.Rectangle(
                x=_x,
                y=_y,
                width=square_size, height=square_size, color=(174, 174, 174), batch=batch)
            widgets["selected"][i].opacity = 128  # 50% transparent

        is_piece: bool = pieces[i] != -1
        if is_piece:
            image = _piece_dict[pieces[i]]
            widgets["pieces"][i] = sprite.Sprite(
                x=_x + square_size/2 - image.width/2,
                y=_y + square_size/2 - image.height/2,
                img=image, batch=batch)
    return widgets


def draw_next_prev_buttons(x, y, width, height, batch):
    widgets = dict(buttons={}, button_labels={})
    ipad = 20
    button_width = width/2 - ipad/2

    prev_color = DARK if is_prev_board_available() else BLACK
    widgets['buttons']['prev'] = shapes.Rectangle(
        x=x,
        y=y,
        width=width/2 - ipad/2, height=height, color=prev_color,batch=batch)
    prev_lbl_color = MID_DARK if is_prev_board_available() else DARK
    widgets['button_labels']['prev'] = text.Label(
        x=x + button_width/2,
        y=y+height/2,
        text="Prev", font_name='consolas', font_size=20, anchor_x='center', anchor_y='center', color=prev_lbl_color, batch=batch
    )
    next_color = DARK if is_next_board_available() else BLACK
    widgets['buttons']['next'] = shapes.Rectangle(
        x=x + button_width + ipad,
        y=y,
        width=width/2 - ipad/2, height=height, color=next_color,batch=batch)
    next_lbl_color = MID_DARK if is_next_board_available() else DARK
    widgets['button_labels']['next'] = text.Label(
        x=x + button_width + ipad + button_width/2,
        y=y+height/2,
        text="Next", font_name='consolas', font_size=20, anchor_x='center', anchor_y='center', color=next_lbl_color, batch=batch)
    return widgets


def draw_cache_info_box(x, y, width, height, batch, table: dict[int, BoardAnalysis]):
    widgets: dict[str, shapes.Rectangle | text.Label | dict] = dict()
    if width < 0 or height < 0:
        return widgets

    widgets["cache_info_box"] = shapes.Rectangle(x, y, width=width, height=height, color=BLACK, batch=batch)
    return widgets


def draw_move_info(x, y, width, height, batch, table: list[BoardAnalysis]):
    nr_of_elements = len(table) + 1
    main_box, header, body = draw_list(x, y, width, height, 5, [40] * nr_of_elements, batch)
    widgets = dict()
    widgets["boxes"] = (main_box, header, body)

    if header:
        widgets["header_text"] = place_text_in_box(
            header[0], batch, pad=0,
            texts=[
                "depth",
                "alpha",
                "hits",
                "Misses",
                "Conflicts",
                "Writes",
                "Confl.%"
            ],
            widths=[100] * 7)

    widgets["body_text"] = {}
    for i, box in enumerate(body):
        line: BoardAnalysis = table[i]
        widgets["body_text"][i] = place_text_in_box(
            box, batch, pad=0,
            texts=[
                f"{i}",
                f"{line.best_score}",
                nr_format(line.hits),
                nr_format(line.misses),
                nr_format(line.conflicts),
                nr_format(line.writes),
                f"{line.conflicts / (line.hits + line.misses):>6.1f}%"
            ],
            widths=[100] * 7)

    return widgets


def nr_format(nr):
    if nr < 1000:
        return f"{nr:>6}"  # Aligns the numbe
    elif nr < 1_000_000:
        return f"{nr / 1000:>5.1f}K"  # 6 cha
    elif nr < 1_000_000_000:
        return f"{nr / 1_000_000:>5.1f}M"  #
    else:
        return f"{nr / 1_000_000_000:>5.1f}B"


def draw_list(x, y, width, height, pad, elements, batch):
    header, body = [], []
    main_box = shapes.Rectangle(x, y, width, height, color=BLACK, batch=batch)
    positions, space_left = place_vertical(x, y, width, height, pad, elements)

    # header
    try:
        header.append(shapes.Rectangle(*positions.pop(0), color=DARK, batch=batch))
    except IndexError:
        pass # there is no place for header

    # body
    for i, info in enumerate(elements):
        try:
            position = positions[i]
            body.append(shapes.Rectangle(*position, color=DARK, batch=batch))
        except IndexError:
            pass # there is no place for element

    return main_box, header, body


def place_vertical(x, y, width, height, pad, heights
                   ) -> tuple[list[tuple[int, int, int, int]], int]:
    result = []
    y_el = y + height
    x_el = x + pad
    w_el = width - 2*pad

    for i, h_el in enumerate(heights):
        y_el -= pad
        y_el -= h_el
        if y_el < y:
            break
        result += [(x_el, y_el, w_el, h_el)]

    space_left = y_el - y

    return result, space_left


def place_text_in_box(box, batch, pad, texts, widths):
    widgets = []
    x = box.x
    for txt, w in zip(texts, widths):
        x += pad
        widgets.append(text.Label(
            text=txt, x=x + w/2, y=box.y + box.height/2, width=w, batch=batch,
            anchor_x='center', anchor_y='center', font_name="Consolas", font_size=15, color=MID_DARK
        ))
        x += w

    return widgets













def draw_eval_table(x, y, width, height, batch, table):
    widgets: dict = dict(labels={}, cache_info={})
    widgets['background'] = shapes.Rectangle(
        x=x,
        y=y,
        width=width, height=height, color=MID_DARK, batch=batch)

    nr_of_rows = len(table['depth'])
    for i in range(nr_of_rows):
        txt = (f"depth {table["depth"][i]:2} > "
               f"{table["score"][i]:4} "
               f"in {table["time"][i]:.2f} s")
        widgets["labels"][i] = text.Label(
            x=x + 20,
            y=y + height - 20 - (i * 60),
            text=txt, font_name='consolas', font_size=20, anchor_x='left', anchor_y='center', color=BLACK, batch=batch)

    for i in range(nr_of_rows):
        txt =  (f"{table["hits"][i]:6} H "
                f"{table["misses"][i]:6} M "
                f"{table["conflicts"][i]:6} C "
                f"{table["writes"][i]:6} W")
        widgets["cache_info"][i] = text.Label(
            x=x+20,
            y=y + height - 20 - (i * 60) - 30,
            text=txt, font_name='consolas', font_size=20, anchor_x='left', anchor_y='center', color=BLACK, batch=batch)
    return widgets



SAND_COLOR = (255, 216, 139)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK = (20, 20, 20)
MID_DARK = (80, 80, 80)

# Configuration
rows = 8
cols = 8
square_size = 60
background_color = (0.1, 0.1, 0.1, 1.0)  # RGBA, 0-1 floats; dark gray\

CYCLE_NR = 0


