from globals import Board, CHESS_SYMBOLS

from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel
from collections import namedtuple

UI_tuple = namedtuple("UI", [
    "root", "board_frame", "tiles", "prev_button", "next_button", "index_label"])




def build_ui() -> UI_tuple:
    root = CTk()

    board_frame = CTkFrame(root)
    board_frame.grid(row=0, column=0, padx=5, pady=5)

    tiles = []
    for i in range(64):
        row_index:     int  = (i // 8)
        is_black_tile: bool = i % 2 == 0

        if row_index % 2 == 0:
            is_black_tile = not is_black_tile

        color = "lightgrey" if is_black_tile else "white"

        tile = CTkButton(
            board_frame, width=30, height=30, text="", font=("consolas", 18),
            text_color="black", fg_color=color, hover_color=color,  corner_radius=0
        )
        tile.grid(row=i//8, column=i%8, padx=0, pady=0)
        tiles.append(tile)

    menu_frame = CTkFrame(root)
    menu_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

    menu_frame.columnconfigure(0, weight=1)
    menu_frame.columnconfigure(4, weight=1)

    prev_button = CTkButton(menu_frame, text="Prev", width=60)
    prev_button.grid(row=0, column=1, padx=2, pady=2)

    index_label = CTkLabel(menu_frame, text="", width=60)
    index_label.grid(row=0, column=2, padx=2, pady=2)

    next_button = CTkButton(menu_frame, text="Next", width=60)
    next_button.grid(row=0, column=3, padx=2, pady=2)

    return UI_tuple(root, board_frame, tiles, prev_button, next_button, index_label)


def show_in_new_ui(full_board_array: list[Board]):

    board_array: list[Board] = []
    for board in full_board_array:
        if all(x == -1 for x in board.board[:]):
            break
        board_array.append(board)

    ui:          UI_tuple  = build_ui()
    board_index: int       = 0
    load_new_board(ui, board_array, board_index, 0)

    def next_cmd():
        nonlocal board_index
        board_index = load_new_board(ui, board_array, board_index, +1)

    def prev_cmd():
        nonlocal board_index
        board_index = load_new_board(ui, board_array, board_index, -1)

    ui.prev_button.configure(command=prev_cmd)
    ui.next_button.configure(command=next_cmd)
    return ui.root



def load_new_board(ui: UI_tuple, board_array: list[Board], old_index: int, delta: int):

    max_len: int = len(board_array)
    if max_len == 0:
        raise ValueError()

    new_index = max(min(old_index + delta, max_len - 1), 0)

    selected_board: Board = board_array[new_index]

    for i in range(64):
        tile:     CTkButton = ui.tiles[i]
        piece_nr: int       = selected_board.board[i]
        text:     str       = CHESS_SYMBOLS[piece_nr]
        tile.configure(text=text)
    ui.index_label.configure(text = f"{new_index}")
    return new_index



def main():
    from testInterface import convert_test_board, TEST_BOARD

    tb = convert_test_board(TEST_BOARD)
    t1 = show_in_new_ui([tb])
    t1.mainloop()


if __name__ == "__main__":
    main()

