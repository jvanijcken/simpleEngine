import pyglet
from pyglet import shapes
from pyglet.image import load
from pyglet import sprite
from pyglet import text
from current_board import *
from global_constants import BoardAnalysis, Move


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

def draw_board(x, y, width, height, batch, pieces, selected_fields, highlighted_fields, last_starts, last_ends, pending_promotions):
    widgets = dict(squares={}, highlight={}, selected={}, pieces={})

    tile_color_dark           = (237, 136,  85)
    tile_color_light          = (251, 227, 214)

    for i in range(64):
        _x = x + square_size * (i % 8)
        _y = y + square_size * (7 - (i // 8))

        if i in pending_promotions:
            move = pending_promotions[i]
            widgets["squares"][i] = shapes.Rectangle(
                x=_x,
                y=_y,
                width=square_size, height=square_size, color=(233, 133, 50), batch=batch)

            image = _piece_dict[move.end_piece]
            widgets["pieces"][i] = sprite.Sprite(
                x=_x + square_size/2 - image.width/2,
                y=_y + square_size/2 - image.height/2,
                img=image, batch=batch)
            continue

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
                radius = square_size/5*2, color=(174, 174, 174), batch=batch)
            widgets["highlight"][i].opacity = 128  # 50% transparent

        is_selected: bool = i in selected_fields
        if is_selected:
            widgets["selected"][i] = shapes.Rectangle(
                x=_x + 5,
                y=_y + 5,
                width=square_size - 10, height=square_size - 10, color=(174, 174, 174), batch=batch)
            widgets["selected"][i].opacity = 128  # 50% transparent

        is_selected: bool = i in last_starts + last_ends
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
    ipad = 1
    button_width = width/2 - ipad/2

    prev_color = DARK if prev_possible() else BLACK
    widgets['buttons']['prev'] = shapes.Rectangle(
        x=x,
        y=y,
        width=width/2 - ipad/2, height=height, color=prev_color,batch=batch)
    prev_lbl_color = MID_DARK if prev_possible() else DARK
    widgets['button_labels']['prev'] = text.Label(
        x=x + button_width/2,
        y=y+height/2,
        text="Prev", font_name='consolas', font_size=20, anchor_x='center', anchor_y='center', color=prev_lbl_color, batch=batch
    )
    next_color = DARK if next_possible() else BLACK
    widgets['buttons']['next'] = shapes.Rectangle(
        x=x + button_width + ipad,
        y=y,
        width=width/2 - ipad/2, height=height, color=next_color,batch=batch)
    next_lbl_color = MID_DARK if next_possible() else DARK
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
    main_box, header, body = draw_list(x, y, width, height, 1, [40] * nr_of_elements, batch)
    widgets = dict()
    widgets["boxes"] = (main_box, header, body)

    if header:
        widgets["header_text"] = place_text_in_box(
            header[0], batch, pad=0,
            texts=[
                "Depth",
                "Alpha",
                "Best",
                "Hits",
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
                f"{get_best_moves(line.moves)}",
                nr_format(line.hits),
                nr_format(line.misses),
                nr_format(line.conflicts),
                nr_format(line.writes),
                f"{line.conflicts / (line.hits + line.misses):>6.1f}%"
            ],
            widths=[100] * 7)

    return widgets


def get_best_moves(moves: list[Move]):
    best_moves = []
    best_score = None
    for move in moves:
        if best_score is None:
            best_moves, best_score = [move], move.score

        elif move.score > best_score:
            best_moves, best_score = [move], move.score

        elif move.score == best_score:
            best_moves += [move]

    try:
        return [m.notation for m in best_moves][0]
    except IndexError:
        return ""



def nr_format(nr):
    if nr < 1000:
        return f"{nr:>6}"
    elif nr < 1_000_000:
        return f"{nr / 1000:>5.1f}K"
    elif nr < 1_000_000_000:
        return f"{nr / 1_000_000:>5.1f}M"
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
        if (x + w) > (box.x + box.width):
            break
        widgets.append(text.Label(
            text=txt, x=x + w/2, y=box.y + box.height/2, width=w, batch=batch,
            anchor_x='center', anchor_y='center', font_name="Segoe UI Symbol", font_size=15, color=MID_DARK
        ))
        x += w

    return widgets


def draw_ranked_moves(x, y, width, height, batch, moves: list[Move]):
    widgets = dict()
    widgets["move_box"] = shapes.Rectangle(x, y, width, height, batch=batch, color=BLACK)
    widgets["move_boxes"] = {}
    widgets["move_texts"] = {}
    coords = place_in_grid(x, y, width, height, 1, 110, 40)
    for i, coord in enumerate(coords):
        try:
            move = moves[i]
        except IndexError:
            break

        box = shapes.Rectangle(*coord, batch=batch, color=DARK)
        txt = place_text_in_box(box, batch, 0, [f"{move.notation}"], [110])
        widgets["move_boxes"][i] = box
        widgets["move_texts"][i] = txt
    return widgets



def place_in_grid(x, y, width, height, pad, w_el, h_el):
    x_end = x + width
    y_end = y - height

    y += height
    x_s = x + 0

    result = []
    for i in range(20):
        x = x_s + 0

        for j in range(20):
            if (y - h_el - pad) < y_end:
                break
            if (x + w_el + pad) > x_end:
                break

            result.append((
                x + pad,
                y - h_el - pad,
                w_el,
                h_el
            ))
            x += pad
            x += w_el

        y -= pad
        y -= h_el

    return result



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


