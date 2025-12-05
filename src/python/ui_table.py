from pyglet import shapes
from pyglet.gl import *
from itertools import accumulate
from dataclasses import dataclass, field
from pyglet.graphics import Batch
from pyglet import text

X      = 0
Y      = 1
WIDTH  = 2
HEIGHT = 3


@dataclass
class Dims:
    x       : int = 0
    y       : int = 0
    width   : int = 0
    height  : int = 0

    pad_x   : int = 0
    pad_y   : int = 0
    x_dim   : int = 0
    y_dim   : int = 0

    widths     : list[int] = field(default_factory=list)
    row_height : int       = 10

    resizer_width     : int = 10
    minimum_col_width : int = 10

@dataclass
class Table:

    boxes    : list[shapes.Rectangle] = field(default_factory=list)
    labels   : list[text.Label      ] = field(default_factory=list)
    resizers : list[shapes.Rectangle] = field(default_factory=list)
    texts    : list[str             ] = field(default_factory=list)

    hovered_resizer : tuple[int, shapes.Rectangle] | tuple = ()
    selected_resizer: tuple[int, shapes.Rectangle] | tuple = ()
    batch: Batch | None  = None

# todo add text-layout and faster squares

#         Widget creation
#                ↓
#     Dims -> Widgets
#      ↑
#  Ui interactions

# =========== DIMENSION STUFF =========== #
def calculate_widths(index, dims: Dims, _x, _y, dx, _dy, _buttons, _modifiers):

    if dx >= 0:

        ms = dims.width - sum(dims.widths[:index + 1]) - dims.pad_x * len(dims.widths) - dims.minimum_col_width * len(dims.widths[index + 1:])
        remainder = min(dx, ms)
        dims.widths[index] += remainder

        start = len(dims.widths) - 1
        end   = index
        step  = -1

        for i in range(start, end, step):
            if remainder <= 0:
                break
            max_space       = dims.widths[i] - dims.minimum_col_width
            dims.widths[i] -= max(0, min(max_space, remainder))
            remainder      -= max_space

    if dx <= 0:
        # remove space from selected column first
        ms = sum(dims.widths[:index + 1])
        remainder = min(-dx, ms)

        max_space           = dims.widths[index] - dims.minimum_col_width
        dims.widths[index] -= max(0, min(max_space, remainder))
        remainder          -= max_space

        # add space to most right column
        dims.widths[-1] += remainder + max_space

        # remove space from other columns
        start = 0
        end   = index
        step  = 1

        for i in range(start, end, step):
            if remainder <= 0:
                break
            max_space       = dims.widths[i] - dims.minimum_col_width
            dims.widths[i] -= max(0, min(max_space, remainder))
            remainder      -= max_space


def table_set_dims(
        dims: Dims,
        x=None, y=None,
        width=None, height=None,
        pad_x=None, pad_y=None,
        widths=None, row_height=None,
        x_dim=None, y_dim=None,
        resizer_width=None
):
    if x is not None:
        dims.x = x
    if y is not None:
        dims.y = y
    if width  is not None:
        dims.width  = width
    if height is not None:
        dims.height = height
    if row_height is not None:
        dims.row_height = row_height
    if y_dim is not None:
        dims.y_dim = y_dim
    if pad_x is not None:
        dims.pad_x = pad_x
    if pad_y is not None:
        dims.pad_y = pad_y
    if resizer_width is not None:
        dims.resizer_width = resizer_width

    if widths is not None:
        dims.widths = widths
        dims.x_dim = len(dims.widths)

    if x_dim is not None:
        dims.x_dim = min(len(dims.widths), x_dim)
        dims.widths = dims.widths[:dims.x_dim]


def table_set_text(_dims: Dims, table: Table, texts: list[str]):
    table.texts = texts


# =========== WIDGET CREATION =========== #
def redraw_resizers(dims: Dims, table: Table):
    table.resizers.clear()
    for _ in range(dims.x_dim):
        resizer = shapes.Rectangle(0, 0, 0, 0, color=(200, 200, 200), batch=table.batch)
        resizer.opacity = 0
        table.resizers.append(resizer)

def redraw_boxes(dims: Dims, table: Table):
    table.boxes.clear()
    for _ in range(dims.y_dim * dims.x_dim):
        box = shapes.Rectangle(0, 0, 0, 0, batch=table.batch, color=(0, 0, 0))
        table.boxes.append(box)

def redraw_labels(dims: Dims, table: Table):
    table.labels.clear()
    for _ in range(dims.y_dim * dims.x_dim):
        lbl = text.Label("", 0, 0, batch=table.batch, font_size=10, color=(255, 255, 255), anchor_x="center", anchor_y="center")
        table.labels.append(lbl)


# =========== WIDGET REPOSITION =========== #
def resize_boxes(dims: Dims, table: Table, only=None):
    x_coords = list( accumulate(dims.widths[i]  + dims.pad_x for i in range(dims.x_dim)) )
    y_coords = list( accumulate(dims.row_height + dims.pad_y for _ in range(dims.y_dim)) )

    for i in range(dims.x_dim * dims.y_dim):
        if only and i % dims.x_dim not in only:
            continue
        r, c = i // dims.x_dim, i % dims.x_dim
        box = table.boxes[i]
        box.x = dims.x + x_coords[c] - dims.widths[c]
        box.y = dims.y + dims.height - y_coords[r]
        box.width  = dims.widths[c]
        box.height = dims.row_height


def resize_resizers(dims: Dims, table: Table):
    for resizer, box in zip(table.resizers, table.boxes):
        resizer.x = box.x + box.width - dims.resizer_width//2
        resizer.y = box.y
        resizer.height=box.height
        resizer.width = dims.resizer_width


def resize_text(dims: Dims, table: Table, only=None, fast=False):
    for i in range(dims.x_dim * dims.y_dim):
        if only and i % dims.x_dim not in only:
            continue
        box = table.boxes[i]
        lbl = table.labels[i]
        try: txt = table.texts[i]
        except IndexError: txt = ""

        lbl.x = box.x + box.width // 2
        lbl.y = box.y + box.height // 2

        if fast:
            continue

        max_chars = len(txt)
        pixel_per_char = lbl.font_size * 0.8  # approximate

        estimate = int(box.width / pixel_per_char)
        estimate = max(0, min(estimate, max_chars))

        if estimate < len(txt):
            lbl.text = (txt[:estimate -2] + "..")[:estimate]
        else:
            lbl.text = txt[:estimate]



# =========== COMPLETE RERENDERING =========== #


def table_rebuild(dims: Dims, table: Table):
    table.batch.invalidate()

    redraw_boxes(dims, table)
    redraw_labels(dims, table)
    redraw_resizers(dims, table)

def table_resize(dims: Dims, table: Table):
    resize_boxes(dims, table)
    resize_text(dims, table)
    resize_resizers(dims, table)



# =========== BATCH DRAWING =========== #
def draw_table_batch(dims: Dims, table: Table):
    glEnable(GL_SCISSOR_TEST)
    glScissor(dims.x, dims.y, dims.width, dims.height)
    glClearColor(0.1, 0.1, 0.1, 0.1)
    glClear(GL_COLOR_BUFFER_BIT)
    table.batch.draw()
    glDisable(GL_SCISSOR_TEST)


# =========== UI_INTERACTION STUFF =========== #
def in_square(sqr, x, y) -> bool:
    return sqr.x <= x <= sqr.x + sqr.width and sqr.y <= y <= sqr.y + sqr.height


def get_clicked_element(x, y, widgets):
    for index, resizer in enumerate(widgets):
        if in_square(resizer, x, y):
            return index, resizer
    return ()


def table_on_mouse_release(dims: Dims, table: Table, _x, _y, _button, _modifiers):
    if table.selected_resizer:
        resize_text(dims, table)
        table.selected_resizer = ()


def table_on_mouse_press(dims: Dims, table: Table, x, y, _button, _modifiers):
    element = get_clicked_element(x, y, table.resizers)
    if not element:
        return
    index, resizer = element
    table.selected_resizer = (index, resizer)

    for i in range(dims.y_dim * dims.x_dim):
        table.labels[i].text = ".."



def table_on_mouse_drag(dims: Dims, table: Table, x, y, dx, dy, buttons, modifiers):
    if table.selected_resizer:
        index, resizer = table.selected_resizer

        calculate_widths(index, dims, x, y, dx, dy, buttons, modifiers)

        resize_boxes(dims, table)
        resize_text(dims, table, fast=True)
        resize_resizers(dims, table)


def table_on_mouse_motion(_dims: Dims, table: Table, x, y, _dx, _dy):
    if table.hovered_resizer:
        _, resizer = table.hovered_resizer
        resizer.opacity = 0

    table.hovered_resizer = ()
    for i in range(4):
        resizer = table.resizers[i]
        if in_square(resizer, x, y):
            table.hovered_resizer = (i, resizer)
            break

    if table.hovered_resizer:
        for i in range(4): table.resizers[i].opacity = 0
        _, resizer = table.hovered_resizer
        resizer.opacity = 128


