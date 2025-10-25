//
// Created by jvani on 20/10/2025.
//

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>
#include "../include/transpositionTable.h"
#include "../include/algorithms.h"
#include "../include/zobristHashing.h"
#include "../include/boardEvaluation.h"


// Board object structure
typedef struct {
    PyObject_HEAD
    PyObject *board;     // list[int]
    PyObject *castles;   // list[int]
    int en_passant;
    int color;
} BoardObject;

// Deallocation
static void
Board_dealloc(BoardObject *self) {
    Py_XDECREF(self->board);
    Py_XDECREF(self->castles);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

// Constructor
static PyObject *
Board_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    BoardObject *self = (BoardObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->board = PyList_New(0);
        if (!self->board) {
            Py_DECREF(self);
            return NULL;
        }
        self->castles = PyList_New(0);
        if (!self->castles) {
            Py_DECREF(self);
            return NULL;
        }
        self->en_passant = -1;
        self->color = 0;
    }
    return (PyObject *) self;
}

// Initializer: __init__(self, board, castles, en_passant, color)
static int
Board_init(BoardObject *self, PyObject *args, PyObject *kwds) {
    PyObject *board = NULL, *castles = NULL;
    int en_passant = -1;
    int color = 0;

    static char *kwlist[] = {"board", "castles", "en_passant", "color", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOii", kwlist,
                                     &board, &castles, &en_passant, &color))
        return -1;

    // Validate board: must be list of length 64, all ints
    if (!PyList_Check(board) || PyList_Size(board) != 64) {
        PyErr_SetString(PyExc_TypeError, "board must be a list of 64 ints");
        return -1;
    }
    for (Py_ssize_t i = 0; i < 64; i++) {
        PyObject *item = PyList_GetItem(board, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "board elements must be ints");
            return -1;
        }
    }

    // Validate castles: must be list of length 4, all ints
    if (!PyList_Check(castles) || PyList_Size(castles) != 4) {
        PyErr_SetString(PyExc_TypeError, "castles must be a list of 4 ints");
        return -1;
    }
    for (Py_ssize_t i = 0; i < 4; i++) {
        PyObject *item = PyList_GetItem(castles, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "castles elements must be ints");
            return -1;
        }
    }

    Py_INCREF(board);
    Py_XDECREF(self->board);
    self->board = board;

    Py_INCREF(castles);
    Py_XDECREF(self->castles);
    self->castles = castles;

    self->en_passant = en_passant;
    self->color = color;

    return 0;
}

// Setter for board
static int
Board_set_board(BoardObject *self, PyObject *value, void *closure) {
    if (!PyList_Check(value) || PyList_Size(value) != 64) {
        PyErr_SetString(PyExc_TypeError, "board must be a list of 64 ints");
        return -1;
    }
    for (Py_ssize_t i = 0; i < 64; i++) {
        PyObject *item = PyList_GetItem(value, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "board elements must be ints");
            return -1;
        }
    }
    Py_INCREF(value);
    Py_XDECREF(self->board);
    self->board = value;
    return 0;
}

// Setter for castles
static int
Board_set_castles(BoardObject *self, PyObject *value, void *closure) {
    if (!PyList_Check(value) || PyList_Size(value) != 4) {
        PyErr_SetString(PyExc_TypeError, "castles must be a list of 4 ints");
        return -1;
    }
    for (Py_ssize_t i = 0; i < 4; i++) {
        PyObject *item = PyList_GetItem(value, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "castles elements must be ints");
            return -1;
        }
    }
    Py_INCREF(value);
    Py_XDECREF(self->castles);
    self->castles = value;
    return 0;
}//HERE END!

// Getter and setter for board
static PyObject *
Board_get_board(const BoardObject *self, void *closure) {
    Py_INCREF(self->board);
    return self->board;
}

// Getter and setter for castles
static PyObject *
Board_get_castles(const BoardObject *self, void *closure) {
    Py_INCREF(self->castles);
    return self->castles;
}

// Getter and setter for en_passant
static PyObject *
Board_get_en_passant(const BoardObject *self, void *closure) {
    return PyLong_FromLong(self->en_passant);
}

static int
Board_set_en_passant(BoardObject *self, PyObject *value, void *closure) {
    int v = PyLong_AsLong(value);
    if (v == -1 && PyErr_Occurred()) {
        return -1;
    }
    self->en_passant = v;
    return 0;
}

// Getter and setter for color
static PyObject *
Board_get_color(const BoardObject *self, void *closure) {
    return PyLong_FromLong(self->color);
}

static int
Board_set_color(BoardObject *self, PyObject *value, void *closure) {
    int v = PyLong_AsLong(value);
    if (v == -1 && PyErr_Occurred()) {
        return -1;
    }
    self->color = v;
    return 0;
}

// GetSet table
static PyGetSetDef Board_getsetters[] = {
    {"board", (getter)Board_get_board, (setter)Board_set_board, "board list", NULL},
    {"castles", (getter)Board_get_castles, (setter)Board_set_castles, "castles list", NULL},
    {"en_passant", (getter)Board_get_en_passant, (setter)Board_set_en_passant, "en_passant int", NULL},
    {"color", (getter)Board_get_color, (setter)Board_set_color, "color int", NULL},
    {NULL}  /* Sentinel */
};

// Type definition
static PyTypeObject BoardType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "PyChess.Board",
    .tp_doc = "Board objects",
    .tp_basicsize = sizeof(BoardObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = Board_new,
    .tp_init = (initproc) Board_init,
    .tp_dealloc = (destructor) Board_dealloc,
    .tp_getset = Board_getsetters,
};


// IMPORTABLE FUNCTION

void pyBoardToCStruct(Board *pBoard, const PyObject *board_obj);
void CStructToPyBoard(const Board* pBoard, PyObject **out_py_board);


static PyObject *
pyIDS(PyObject *self, PyObject *args)
{
    PyObject *board_obj = NULL;
    int color = 0;
    int maxDepth = 0;
    double durationSeconds = 0.0;

    // Parse: Board, color, maxDepth, durationSeconds
    if (!PyArg_ParseTuple(args, "O!iid", &BoardType, &board_obj, &color, &maxDepth, &durationSeconds)) {
        return NULL;
    }

    // Verify board type
    if (!PyObject_TypeCheck(board_obj, &BoardType)) {
        PyErr_SetString(PyExc_TypeError, "Expected a PyChess.Board object as first argument");
        return NULL;
    }

    // Convert Python Board to C Board struct
    Board board;
    pyBoardToCStruct(&board, board_obj);

    // Allocate best sequence array (depth-limited)
    Board *bestSeq = malloc(sizeof(Board) * maxDepth);
    if (!bestSeq) {
        PyErr_NoMemory();
        return NULL;
    }

    const int durationSecondsInt = (int)round(durationSeconds);

    // Run your core search
    const int score = timeLimitedIterativeDeepeningSearch(&board, maxDepth, color, bestSeq, durationSecondsInt);

    // Convert bestSeq → Python list of PyChess.Board objects
    PyObject *py_list = PyList_New(maxDepth);
    if (!py_list) {
        free(bestSeq);
        PyErr_NoMemory();
        return NULL;
    }

    for (int i = 0; i < maxDepth; i++) {
        PyObject *pyBoardObj = NULL;
        CStructToPyBoard(&bestSeq[i], &pyBoardObj);
        if (!pyBoardObj) {
            // Cleanup and propagate error
            Py_DECREF(py_list);
            free(bestSeq);
            return NULL;
        }
        PyList_SetItem(py_list, i, pyBoardObj);  // steals reference
    }

    free(bestSeq);

    // Return a tuple: (score, [list of Boards])
    PyObject *result = Py_BuildValue("(iO)", score, py_list);
    Py_DECREF(py_list); // Py_BuildValue() increments refcount

    return result;
}


// MODULE

static PyMethodDef PyChessMethods[] = {
    {"pyIDS", pyIDS, METH_VARARGS, "Call pyIDS function"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static PyModuleDef pychessmodule = {
    PyModuleDef_HEAD_INIT,
    "PyChess",
    "Python Chess module with Board object",
    -1,
    PyChessMethods,  // <- attach methods here!
    NULL, NULL, NULL, NULL
};


// Module initialization
PyMODINIT_FUNC
PyInit_PyChess(void) {
    if (PyType_Ready(&BoardType) < 0)
        return NULL;

    PyObject *m = PyModule_Create(&pychessmodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&BoardType);
    if (PyModule_AddObject(m, "Board", (PyObject *)&BoardType) < 0) {
        Py_DECREF(&BoardType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}


// HELPER FUNCTIONS
uint64_t zobristHash(const Board* board, const int color) {
    uint64_t key = 0ULL;
    if (color) {
        key ^= colorHash;
    }
    for (int c = 0; c < 2; c++) {
        for (int piece = 0; piece < 6; piece++) {
            uint64_t pieces = board->pieces[c][piece];

            while (pieces) {
                const int index = __builtin_ctzll(pieces);
                key ^= tableHash[c][piece][index];
                pieces &= pieces - 1;
            }
        }
    }
    return key;
}


int evaluateBoard(const Board *pBoard) {
    int score = 0;

    for (int c = 0; c < 2; c++) {
        for (int p = 0; p < 6; p++) {
            uint64_t pieces = pBoard->pieces[c][p];
            while (pieces) {
                const int index = __builtin_ctzll(pieces);
                pieces &= pieces - 1;  // had a bug before (accidentally used pieces &= -pieces) -> caused infinite loop
                score += pieceEvaluators[c][p][index];
            }
        }
    }
    return score;
}


void pyBoardToCStruct(Board *pBoard, const PyObject *board_obj) {

    // Check that it’s actually a Board object
    if (!PyObject_TypeCheck(board_obj, &BoardType)) {
        PyErr_SetString(PyExc_TypeError, "Expected a PyChess.Board object");
        return;
    }

    // Cast to our C struct
    const BoardObject *board = (BoardObject *)board_obj;

    // ===== Extract Python-level fields =====
    PyObject *py_board = board->board;     // list[int] of length 64
    PyObject *py_castles = board->castles; // list[int] of length 4
    const int en_passant = board->en_passant;
    const int color = board->color;

    // ===== Convert Python lists to C arrays =====
    int board_array[64];
    int castles_array[4];

    for (Py_ssize_t i = 0; i < 64; i++) {
        PyObject *item = PyList_GetItem(py_board, i);  // borrowed reference
        board_array[i] = (int) PyLong_AsLong(item);
    }

    for (Py_ssize_t i = 0; i < 4; i++) {
        PyObject *item = PyList_GetItem(py_castles, i);  // borrowed reference
        castles_array[i] = (int) PyLong_AsLong(item);
    }

    // Build a Board C struct
    // clear board
    for (int c = 0; c < 2; c++) {
        for (int p = 0; p < 6; p++) {
            pBoard->pieces[c][p] = 0ULL;
        }
    }
    // convert en passant into uint64_t
    pBoard->enPassant = (en_passant == -1)? 0ULL : 1ULL << en_passant;

    // add pieces
    for (int i = 0; i < 64; i++) {
        const int coloredPiece = board_array[i];
        if (coloredPiece == NO_PIECE) break;
        const int c = coloredPiece / 6;
        const int p = coloredPiece % 6;
        pBoard->pieces[c][p] |= (1ULL << i);
    }

    // add colors
    pBoard->colors[WHITE] = pBoard->pieces[WHITE][P] | pBoard->pieces[WHITE][R] | pBoard->pieces[WHITE][N] |
                            pBoard->pieces[WHITE][B] | pBoard->pieces[WHITE][Q] | pBoard->pieces[WHITE][K];
    pBoard->colors[BLACK] = pBoard->pieces[BLACK][P] | pBoard->pieces[BLACK][R] | pBoard->pieces[BLACK][N] |
                            pBoard->pieces[BLACK][B] | pBoard->pieces[BLACK][Q] | pBoard->pieces[BLACK][K];

    // add castles
    pBoard->castle = 0ULL;
    for (int i = 0; i < 4; i++) {
        if (castles_array[i] == 0) break;
        pBoard->castle |= 1ULL << i;
    }
    pBoard->hash = zobristHash(pBoard, color);
    pBoard->eval = evaluateBoard(pBoard);
}


void CStructToPyBoard(const Board *pBoard, PyObject **out_py_board)
{
    // Create the Python lists for board and castles
    PyObject *py_board_list = PyList_New(64);
    PyObject *py_castles_list = PyList_New(4);

    if (!py_board_list || !py_castles_list) {
        Py_XDECREF(py_board_list);
        Py_XDECREF(py_castles_list);
        PyErr_SetString(PyExc_RuntimeError, "Failed to allocate board or castles list");
        return;
    }

    // ===== Convert C bitboards -> Python board list =====
    // We'll encode each square with (color * 6 + piece_type)
    // or NO_PIECE (usually -1 or 0) if empty
    for (int sq = 0; sq < 64; sq++) {
        int piece_code = NO_PIECE; // define NO_PIECE = -1 somewhere
        for (int c = 0; c < 2; c++) {
            for (int p = 0; p < 6; p++) {
                if (pBoard->pieces[c][p] & (1ULL << sq)) {
                    piece_code = c * 6 + p;
                    goto found_piece;
                }
            }
        }
        found_piece:
        PyList_SetItem(py_board_list, sq, PyLong_FromLong(piece_code));
    }

    // ===== Castling rights =====
    // You used bits 0..3 for castling flags
    for (int i = 0; i < 4; i++) {
        const int castle_flag = (pBoard->castle & (1ULL << i)) ? 1 : 0;
        PyList_SetItem(py_castles_list, i, PyLong_FromLong(castle_flag));
    }

    // ===== En passant square =====
    int en_passant = -1;
    if (pBoard->enPassant != 0ULL) {
        en_passant = __builtin_ctzll(pBoard->enPassant);  // lowest set bit index (0..63)
    }

    // ===== Side to move =====
    const int color = (pBoard->colors[WHITE] & 1ULL) ? WHITE : BLACK; // depends on your engine's definition
    // (You may want to store current color directly in Board; adjust this accordingly.)

    // ===== Create the PyChess.Board Python object =====
    PyObject *args_tuple = Py_BuildValue("OOii",
                                         py_board_list,
                                         py_castles_list,
                                         en_passant,
                                         color);

    PyObject *py_board_obj = PyObject_CallObject((PyObject *) &BoardType, args_tuple);

    Py_DECREF(args_tuple);
    Py_DECREF(py_board_list);
    Py_DECREF(py_castles_list);

    if (!py_board_obj) {
        PyErr_Print(); // prints the actual TypeError
        PyErr_SetString(PyExc_RuntimeError, "Failed to create PyChess.Board object");
        return;
    }

    *out_py_board = py_board_obj;
}
