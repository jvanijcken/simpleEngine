import ctypes
lib = ctypes.CDLL("C:\\Users\\jvani\\CLionProjects\\simpleEngine\\core.dll")

# DECLARATIONS

# Example struct placeholder (we’ll define this next)
import ctypes

class CBoard(ctypes.Structure):
    _fields_ = [
        ("pieces", (ctypes.c_uint64 * 6) * 2),  # 2x6 array of uint64_t
        ("colors", ctypes.c_uint64 * 2),
        ("enPassant", ctypes.c_uint64),
        ("hash", ctypes.c_uint64),
        ("castle", ctypes.c_uint8),
        ("moveIndex", ctypes.c_int),
        ("eval", ctypes.c_int),
    ]


# Define argument and return types
lib.iterativeDeepeningSearch.argtypes = [
    ctypes.POINTER(CBoard),  # const Board* board
    ctypes.c_int,           # int maxDepth
    ctypes.c_int,           # int color
    ctypes.POINTER(CBoard)   # Board bestSeq[]
]
lib.iterativeDeepeningSearch.restype = ctypes.c_int

lib.timeLimitedIterativeDeepeningSearch.argtypes = [
    ctypes.POINTER(CBoard),  # Board* board
    ctypes.c_int,           # int maxDepth
    ctypes.c_int,           # int color
    ctypes.POINTER(CBoard),  # Board bestSeq[]
    ctypes.c_int            # int durationSeconds
]
lib.timeLimitedIterativeDeepeningSearch.restype = ctypes.c_int

import ctypes

# Assuming you already have lib loaded and Board defined as you wrote.

# Create input Board instance and fill it
board = CBoard()
board.castle = 15
board.pieces[0] = (ctypes.c_uint64 * 6)(2**1,  2**2,  2**3,  2**4,  2**5,  2**6)
board.pieces[1] = (ctypes.c_uint64 * 6)(2**55, 2**56, 2**57, 2**58, 2**59, 2**60)


class PyBoard:
    def __init__(self, pieces, colors, en_passant, castle):
        self.pieces    = pieces
        self.colors    = colors
        self.enPassant = en_passant
        self.castle    = castle




# Create an array of Board structs for bestSeq output (e.g., maxDepth=5)
maxDepth = 2
BestSeqArray = CBoard * maxDepth  # array type of Boards
bestSeq = BestSeqArray()  # create instance of array

# Call the function
color = 1  # example value

result = lib.iterativeDeepeningSearch(
    ctypes.byref(board),
    maxDepth,
    color,
    bestSeq
)

print("Result:", result)

# Now bestSeq contains maxDepth Boards - you can inspect them
for i in range(maxDepth):
    print(f"BestSeq[{i}] eval:", bestSeq[i].eval)




if __name__ == "__main__":
    pass