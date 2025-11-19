//
// Created by jvani on 20/10/2025.
//

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <math.h>
#include <pthread.h>
#include <unistd.h>

#include "../include/transpositionTable.h"
#include "../include/algorithms.h"
#include "../include/zobristHashing.h"
#include "../include/boardEvaluation.h"

#include "../testing/debugTools.h"

pthread_mutex_t module_mutex = PTHREAD_MUTEX_INITIALIZER;
bool TERMINATE_TIME_CHECKER = false;


// HELPER FUNCTIONS
uint64_t zobristHash(const Board* board, const int color) {
    uint64_t key = 0ULL;

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

    if (color) {
        key ^= colorHash;
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


Board* convertArgsToBoard(PyObject* pieces_list, PyObject* castle_rights_list, const int en_passant, PyObject* is_white, Board* result) {
    // --- Validate input types ---
    if (!PyList_Check(pieces_list)) {
        PyErr_SetString(PyExc_TypeError, "pieces must be a list of ints");
        return NULL;
    }
    if (!PyList_Check(castle_rights_list)) {
        PyErr_SetString(PyExc_TypeError, "castle_rights must be a list of ints");
        return NULL;
    }
    if (!PyBool_Check(is_white)) {
        PyErr_SetString(PyExc_TypeError, "is_white must be a bool");
        return NULL;
    }
    const int color = (is_white == Py_True)? 0 : 1;

    // Convert pieces list → C array
    // add pieces
    for (int i = 0; i < 64; i++) {
        PyObject *item = PyList_GetItem(pieces_list, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "pieces list must contain ints");
            return NULL;
        }
        const int coloredPiece = (int)PyLong_AsLong(item);

        if (coloredPiece == NO_PIECE) continue;  // another bug fix
        const int c = coloredPiece / 6;
        const int p = coloredPiece % 6;
        result->pieces[c][p] |= (1ULL << i);
    }

    // add colors
    result->colors[WHITE] = result->pieces[WHITE][P] | result->pieces[WHITE][R] | result->pieces[WHITE][N] |
                            result->pieces[WHITE][B] | result->pieces[WHITE][Q] | result->pieces[WHITE][K];
    result->colors[BLACK] = result->pieces[BLACK][P] | result->pieces[BLACK][R] | result->pieces[BLACK][N] |
                            result->pieces[BLACK][B] | result->pieces[BLACK][Q] | result->pieces[BLACK][K];

    // Convert castle_rights list → C array
    const Py_ssize_t num_rights = PyList_Size(castle_rights_list);
    for (Py_ssize_t i = 0; i < num_rights && i < 4; i++) {
        PyObject *item = PyList_GetItem(castle_rights_list, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "castle_rights list must contain ints");
            return NULL;
        }
        const int hasRight = (int)PyLong_AsLong(item);
        result->castle |= (hasRight)? 1ULL << i : 0ULL;
    }

    result->enPassant = (en_passant == NO_MOVE)? 0ULL : 1ULL << en_passant;

    result->hash = zobristHash(result, color);
    result->eval = evaluateBoard(result);
    return result;
}


PyObject* convertBoardToArgs(const Board* board, const int color) {
    if (!board) {
        PyErr_SetString(PyExc_ValueError, "board is NULL");
        return NULL;
    }

    // --- Create Python lists ---
    PyObject *pieces_list = PyList_New(64);
    if (!pieces_list) return PyErr_NoMemory();

    PyObject *castle_rights_list = PyList_New(4);
    if (!castle_rights_list) {
        Py_DECREF(pieces_list);
        return PyErr_NoMemory();
    }

    // --- Fill pieces_list (64 squares) ---
    for (int sq = 0; sq < 64; sq++) {
        int coloredPiece = -1;  // NO_PIECE
        for (int c = 0; c < 2; c++) {  // WHITE, BLACK
            for (int p = 0; p < 6; p++) {  // P, N, B, R, Q, K
                if (board->pieces[c][p] & (1ULL << sq)) {
                    coloredPiece = c * 6 + p;
                    break;
                }
            }
            if (coloredPiece != -1) break;
        }
        PyObject *val = PyLong_FromLong(coloredPiece);
        PyList_SET_ITEM(pieces_list, sq, val);  // Steals reference
    }

    // --- Fill castle_rights_list (4 values: WK, WQ, BK, BQ) ---
    for (int i = 0; i < 4; i++) {
        int hasRight = (board->castle & (1ULL << i)) ? 1 : 0;
        PyObject *val = PyLong_FromLong(hasRight);
        PyList_SET_ITEM(castle_rights_list, i, val);
    }

    // --- en_passant ---
    int en_passant = -1;  // NO_MOVE by default
    if (board->enPassant) {
        for (int sq = 0; sq < 64; sq++) {
            if (board->enPassant & (1ULL << sq)) {
                en_passant = sq;
                break;
            }
        }
    }

    // --- Create final tuple: (pieces_list, castle_rights_list, en_passant, color) ---
    const bool is_white = color == 0;
    PyObject *result = PyTuple_New(4);
    PyTuple_SET_ITEM(result, 0, pieces_list);          // Steals ref
    PyTuple_SET_ITEM(result, 1, castle_rights_list);   // Steals ref
    PyTuple_SET_ITEM(result, 2, PyLong_FromLong(en_passant));
    PyTuple_SET_ITEM(result, 3, PyBool_FromLong(is_white));
    return result;
}

// IMPORTABLE FUNCTION
static PyObject *
direct_search(PyObject *self, PyObject *args)
{
    PyObject *pieces_list        = NULL;
    PyObject *castle_rights_list = NULL;
    int en_passant               = 0;
    PyObject *is_white           = NULL;
    int depth                    = 0;
    PyObject *stop_flag          = NULL;

    if (!PyArg_ParseTuple(args, "OOiOiO", &pieces_list, &castle_rights_list, &en_passant, &is_white, &depth, &stop_flag)) {
        return NULL;
    }
    Py_XINCREF(stop_flag);  // keep this object alive!
    Board board = {0};
    if (!convertArgsToBoard(pieces_list, castle_rights_list, en_passant, is_white, &board)) {
        return NULL;
    };
    if (!PyBool_Check(is_white)) {
        PyErr_SetString(PyExc_TypeError, "is_white must be a bool");
        return NULL;
    }
    const int color = (is_white == Py_True)? 0 : 1;
    const Result result = directSearch(&board, depth, color, stop_flag);

    const int opposite_color = (color)? 0 : 1;
    PyObject* board_args = convertBoardToArgs(&result.bestMove, opposite_color);

    PyObject* meta = Py_BuildValue(
        "(iiOiiii)",
        result.depth,
        result.score,
        PyBool_FromLong(result.calculationsInterrupted),
        result.TTHits,
        result.TTMisses,
        result.TTConflicts,
        result.TTWrites);


    Py_DECREF(stop_flag);
    return PySequence_Concat(board_args, meta);
}




// MODULE

static PyMethodDef PyChessMethods[] = {
    {
        "direct_search",
        direct_search,
        METH_VARARGS,
        "Call direct_search function"
    },
    {
        NULL, NULL, 0, NULL
    }
};

// Module definition
static PyModuleDef pychessmodule = {
    PyModuleDef_HEAD_INIT,
    "PyChess",
    "Python Chess module",
    -1,
    PyChessMethods,
    NULL, NULL, NULL, NULL
};


// Module initialization
PyMODINIT_FUNC
PyInit_PyChess(void) {

    PyObject *m = PyModule_Create(&pychessmodule);
    if (m == NULL)
        return NULL;

    return m;
}
