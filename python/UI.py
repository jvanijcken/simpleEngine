from customtkinter import CTk, CTkButton

NO_PIECE = -1

WP = 0
WR = 1
WN = 2
WB = 3
WQ = 4
WK = 5
BP = 6
BR = 7
BN = 8
BB = 9
BQ = 10
BK = 11

PIECE_NAMES = [
    "wP", "wR", "wN", "wB", "wQ", "wK",
    "bP", "bR", "bN", "bB", "bQ", "bK",
    ""  # for NO_PIECE
]

ROOT        = CTk()
SQUARES     = []
BOARD       = [0] * 64
HIGHLIGHTED = [False] * 64

SELECTED_PIECE_INDEX = -1
LAST_START = -1
LAST_END   = -1
CURRENT_PLAYER       = "w"


def init():

    for i in range(64):
        square = CTkButton(ROOT, height=40, width=40, corner_radius=0, text="")
        square.grid(row= i//8, column = i%8, padx=1, pady=1)
        SQUARES.append(square)

def display_board(pieces: list):

    for i in range(64):
        piece_nr = pieces[i]
        piece_name = PIECE_NAMES[piece_nr]
        button = SQUARES[i]
        button.configure(text=piece_name)

def select_square(index: int):
    global SELECTED_PIECE_INDEX
    global HIGHLIGHTED

    if index == SELECTED_PIECE_INDEX:
        SELECTED_PIECE_INDEX = -1
        HIGHLIGHTED = [False] * 64

    selected_piece_nr   = BOARD[index]
    selected_piece_name = PIECE_NAMES[selected_piece_nr]

    if selected_piece_name == NO_PIECE:
        SELECTED_PIECE_INDEX = -1
        HIGHLIGHTED = [False] * 64
        return

    if selected_piece_name[0] != CURRENT_PLAYER:
        SELECTED_PIECE_INDEX = -1
        HIGHLIGHTED = [False] * 64
        return

    SELECTED_PIECE_INDEX = index
    HIGHLIGHTED = get_possible_moves(index)

def get_possible_moves(index):
    return [False] * 64



if __name__ == "__main__":
    ROOT.mainloop()


